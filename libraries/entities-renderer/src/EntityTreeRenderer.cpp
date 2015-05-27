//
//  EntityTreeRenderer.cpp
//  interface/src
//
//  Created by Brad Hefta-Gaub on 12/6/13.
//  Copyright 2013 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#include <gpu/GPUConfig.h>

#include <glm/gtx/quaternion.hpp>

#include <QEventLoop>
#include <QScriptSyntaxCheckResult>

#include <AbstractScriptingServicesInterface.h>
#include <AbstractViewStateInterface.h>
#include <DeferredLightingEffect.h>
#include <GlowEffect.h>
#include <Model.h>
#include <NetworkAccessManager.h>
#include <PerfStat.h>
#include <SceneScriptingInterface.h>
#include <ScriptEngine.h>
#include <TextureCache.h>
#include <SoundCache.h>

#include "EntityTreeRenderer.h"

#include "RenderableBoxEntityItem.h"
#include "RenderableLightEntityItem.h"
#include "RenderableModelEntityItem.h"
#include "RenderableParticleEffectEntityItem.h"
#include "RenderableSphereEntityItem.h"
#include "RenderableTextEntityItem.h"
#include "RenderableWebEntityItem.h"
#include "RenderableZoneEntityItem.h"
#include "RenderableLineEntityItem.h"
#include "EntitiesRendererLogging.h"

EntityTreeRenderer::EntityTreeRenderer(bool wantScripts, AbstractViewStateInterface* viewState, 
                                            AbstractScriptingServicesInterface* scriptingServices) :
    OctreeRenderer(),
    _wantScripts(wantScripts),
    _entitiesScriptEngine(NULL),
    _sandboxScriptEngine(NULL),
    _localAudioInterface(NULL),
    _lastMouseEventValid(false),
    _viewState(viewState),
    _scriptingServices(scriptingServices),
    _displayElementChildProxies(false),
    _displayModelBounds(false),
    _displayModelElementProxy(false),
    _dontDoPrecisionPicking(false)
{
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Model, RenderableModelEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Box, RenderableBoxEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Sphere, RenderableSphereEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Light, RenderableLightEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Text, RenderableTextEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Web, RenderableWebEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(ParticleEffect, RenderableParticleEffectEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Zone, RenderableZoneEntityItem::factory)
    REGISTER_ENTITY_TYPE_WITH_FACTORY(Line, RenderableLineEntityItem::factory)
    
    _currentHoverOverEntityID = UNKNOWN_ENTITY_ID;
    _currentClickingOnEntityID = UNKNOWN_ENTITY_ID;
}

EntityTreeRenderer::~EntityTreeRenderer() {
    // NOTE: we don't need to delete _entitiesScriptEngine because it is registered with the application and has a 
    // signal tied to call it's deleteLater on doneRunning
    if (_sandboxScriptEngine) {
        // TODO: consider reworking how _sandboxScriptEngine is managed. It's treated differently than _entitiesScriptEngine
        // because we don't call registerScriptEngineWithApplicationServices() for it. This implementation is confusing and 
        // potentially error prone because it's not a full fledged ScriptEngine that has been fully connected to the 
        // application. We did this so that scripts that were ill-formed could be evaluated but not execute against the 
        // application services. But this means it's shutdown behavior is different from other ScriptEngines
        delete _sandboxScriptEngine;
        _sandboxScriptEngine = NULL;
    }
}

void EntityTreeRenderer::clear() {
    leaveAllEntities();
    foreach (const EntityItemID& entityID, _entityScripts.keys()) {
        checkAndCallUnload(entityID);
    }
    OctreeRenderer::clear();
    _entityScripts.clear();
}

void EntityTreeRenderer::init() {
    OctreeRenderer::init();
    EntityTree* entityTree = static_cast<EntityTree*>(_tree);
    entityTree->setFBXService(this);

    if (_wantScripts) {
        _entitiesScriptEngine = new ScriptEngine(NO_SCRIPT, "Entities",
                                        _scriptingServices->getControllerScriptingInterface());
        _scriptingServices->registerScriptEngineWithApplicationServices(_entitiesScriptEngine);

        _sandboxScriptEngine = new ScriptEngine(NO_SCRIPT, "Entities Sandbox", NULL);
    }

    // make sure our "last avatar position" is something other than our current position, so that on our
    // first chance, we'll check for enter/leave entity events.    
    _lastAvatarPosition = _viewState->getAvatarPosition() + glm::vec3((float)TREE_SCALE);
    
    connect(entityTree, &EntityTree::deletingEntity, this, &EntityTreeRenderer::deletingEntity);
    connect(entityTree, &EntityTree::addingEntity, this, &EntityTreeRenderer::addingEntity);
    connect(entityTree, &EntityTree::entityScriptChanging, this, &EntityTreeRenderer::entitySciptChanging);
}

void EntityTreeRenderer::shutdown() {
    _entitiesScriptEngine->disconnect(); // disconnect all slots/signals from the script engine
    _shuttingDown = true;
}

void EntityTreeRenderer::scriptContentsAvailable(const QUrl& url, const QString& scriptContents) {
    if (_waitingOnPreload.contains(url)) {
        QList<EntityItemID> entityIDs = _waitingOnPreload.values(url);
        _waitingOnPreload.remove(url);
        foreach(EntityItemID entityID, entityIDs) {
            checkAndCallPreload(entityID);
        } 
    }
}

void EntityTreeRenderer::errorInLoadingScript(const QUrl& url) {
    if (_waitingOnPreload.contains(url)) {
        _waitingOnPreload.remove(url);
    }
}

QScriptValue EntityTreeRenderer::loadEntityScript(const EntityItemID& entityItemID, bool isPreload) {
    EntityItemPointer entity = static_cast<EntityTree*>(_tree)->findEntityByEntityItemID(entityItemID);
    return loadEntityScript(entity, isPreload);
}


QString EntityTreeRenderer::loadScriptContents(const QString& scriptMaybeURLorText, bool& isURL, bool& isPending, QUrl& urlOut) {
    isPending = false;
    QUrl url(scriptMaybeURLorText);
    
    // If the url is not valid, this must be script text...
    // We document "direct injection" scripts as starting with "(function...", and that would never be a valid url.
    // But QUrl thinks it is.
    if (!url.isValid() || scriptMaybeURLorText.startsWith("(")) {
        isURL = false;
        return scriptMaybeURLorText;
    }
    isURL = true;
    urlOut = url;

    QString scriptContents; // assume empty
    
    // if the scheme length is one or lower, maybe they typed in a file, let's try
    const int WINDOWS_DRIVE_LETTER_SIZE = 1;
    if (url.scheme().size() <= WINDOWS_DRIVE_LETTER_SIZE) {
        url = QUrl::fromLocalFile(scriptMaybeURLorText);
    }

    // ok, let's see if it's valid... and if so, load it
    if (url.isValid()) {
        if (url.scheme() == "file") {
            QString fileName = url.toLocalFile();
            QFile scriptFile(fileName);
            if (scriptFile.open(QFile::ReadOnly | QFile::Text)) {
                qCDebug(entitiesrenderer) << "Loading file:" << fileName;
                QTextStream in(&scriptFile);
                scriptContents = in.readAll();
            } else {
                qCDebug(entitiesrenderer) << "ERROR Loading file:" << fileName;
            }
        } else {
            auto scriptCache = DependencyManager::get<ScriptCache>();
            
            if (!scriptCache->isInBadScriptList(url)) {
                scriptContents = scriptCache->getScript(url, this, isPending);
            }
        }
    }
    
    return scriptContents;
}


QScriptValue EntityTreeRenderer::loadEntityScript(EntityItemPointer entity, bool isPreload) {
    if (_shuttingDown) {
        return QScriptValue(); // since we're shutting down, we don't load any more scripts
    }
    
    if (!entity) {
        return QScriptValue(); // no entity...
    }
    
    // NOTE: we keep local variables for the entityID and the script because
    // below in loadScriptContents() it's possible for us to execute the
    // application event loop, which may cause our entity to be deleted on
    // us. We don't really need access the entity after this point, can
    // can accomplish all we need to here with just the script "text" and the ID.
    EntityItemID entityID = entity->getEntityItemID();
    QString entityScript = entity->getScript();

    if (_entityScripts.contains(entityID)) {
        EntityScriptDetails details = _entityScripts[entityID];
        
        // check to make sure our script text hasn't changed on us since we last loaded it
        if (details.scriptText == entityScript) {
            return details.scriptObject; // previously loaded
        }
        
        // if we got here, then we previously loaded a script, but the entity's script value
        // has changed and so we need to reload it.
        _entityScripts.remove(entityID);
    }
    if (entityScript.isEmpty()) {
        return QScriptValue(); // no script
    }
    
    bool isURL = false; // loadScriptContents() will tell us if this is a URL or just text.
    bool isPending = false;
    QUrl url;
    QString scriptContents = loadScriptContents(entityScript, isURL, isPending, url);
    
    if (isPending && isPreload && isURL) {
        _waitingOnPreload.insert(url, entityID);
    }

    auto scriptCache = DependencyManager::get<ScriptCache>();

    if (isURL && scriptCache->isInBadScriptList(url)) {
        return QScriptValue(); // no script contents...
    }
    
    if (scriptContents.isEmpty()) {
        return QScriptValue(); // no script contents...
    }
    
    QScriptSyntaxCheckResult syntaxCheck = QScriptEngine::checkSyntax(scriptContents);
    if (syntaxCheck.state() != QScriptSyntaxCheckResult::Valid) {
        qCDebug(entitiesrenderer) << "EntityTreeRenderer::loadEntityScript() entity:" << entityID;
        qCDebug(entitiesrenderer) << "   " << syntaxCheck.errorMessage() << ":"
                          << syntaxCheck.errorLineNumber() << syntaxCheck.errorColumnNumber();
        qCDebug(entitiesrenderer) << "    SCRIPT:" << entityScript;

        scriptCache->addScriptToBadScriptList(url);
        
        return QScriptValue(); // invalid script
    }
    
    if (isURL) {
        _entitiesScriptEngine->setParentURL(entity->getScript());
    }
    QScriptValue entityScriptConstructor = _sandboxScriptEngine->evaluate(scriptContents);
    
    if (!entityScriptConstructor.isFunction()) {
        qCDebug(entitiesrenderer) << "EntityTreeRenderer::loadEntityScript() entity:" << entityID;
        qCDebug(entitiesrenderer) << "    NOT CONSTRUCTOR";
        qCDebug(entitiesrenderer) << "    SCRIPT:" << entityScript;

        scriptCache->addScriptToBadScriptList(url);

        return QScriptValue(); // invalid script
    } else {
        entityScriptConstructor = _entitiesScriptEngine->evaluate(scriptContents);
    }

    QScriptValue entityScriptObject = entityScriptConstructor.construct();
    EntityScriptDetails newDetails = { entityScript, entityScriptObject };
    _entityScripts[entityID] = newDetails;

    if (isURL) {
        _entitiesScriptEngine->setParentURL("");
    }

    return entityScriptObject; // newly constructed
}

QScriptValue EntityTreeRenderer::getPreviouslyLoadedEntityScript(const EntityItemID& entityID) {
    if (_entityScripts.contains(entityID)) {
        EntityScriptDetails details = _entityScripts[entityID];
        return details.scriptObject; // previously loaded
    }
    return QScriptValue(); // no script
}

void EntityTreeRenderer::setTree(Octree* newTree) {
    OctreeRenderer::setTree(newTree);
    static_cast<EntityTree*>(_tree)->setFBXService(this);
}

void EntityTreeRenderer::update() {
    if (_tree && !_shuttingDown) {
        EntityTree* tree = static_cast<EntityTree*>(_tree);
        tree->update();
        
        // check to see if the avatar has moved and if we need to handle enter/leave entity logic
        checkEnterLeaveEntities();

        // Even if we're not moving the mouse, if we started clicking on an entity and we have
        // not yet released the hold then this is still considered a holdingClickOnEntity event
        // and we want to simulate this message here as well as in mouse move
        if (_lastMouseEventValid && !_currentClickingOnEntityID.isInvalidID()) {
            emit holdingClickOnEntity(_currentClickingOnEntityID, _lastMouseEvent);
            QScriptValueList currentClickingEntityArgs = createMouseEventArgs(_currentClickingOnEntityID, _lastMouseEvent);
            QScriptValue currentClickingEntity = loadEntityScript(_currentClickingOnEntityID);
            if (currentClickingEntity.property("holdingClickOnEntity").isValid()) {
                currentClickingEntity.property("holdingClickOnEntity").call(currentClickingEntity, currentClickingEntityArgs);
            }
        }

    }
}

void EntityTreeRenderer::checkEnterLeaveEntities() {
    if (_tree && !_shuttingDown) {
        glm::vec3 avatarPosition = _viewState->getAvatarPosition();
        
        if (avatarPosition != _lastAvatarPosition) {
            float radius = 1.0f; // for now, assume 1 meter radius
            QVector<EntityItemPointer> foundEntities;
            QVector<EntityItemID> entitiesContainingAvatar;
            
            // find the entities near us
            _tree->lockForRead(); // don't let someone else change our tree while we search
            static_cast<EntityTree*>(_tree)->findEntities(avatarPosition, radius, foundEntities);

            // create a list of entities that actually contain the avatar's position
            foreach(EntityItemPointer entity, foundEntities) {
                if (entity->contains(avatarPosition)) {
                    entitiesContainingAvatar << entity->getEntityItemID();
                }
            }
            _tree->unlock();
            
            // Note: at this point we don't need to worry about the tree being locked, because we only deal with
            // EntityItemIDs from here. The loadEntityScript() method is robust against attempting to load scripts
            // for entity IDs that no longer exist. 

            // for all of our previous containing entities, if they are no longer containing then send them a leave event
            foreach(const EntityItemID& entityID, _currentEntitiesInside) {
                if (!entitiesContainingAvatar.contains(entityID)) {
                    emit leaveEntity(entityID);
                    QScriptValueList entityArgs = createEntityArgs(entityID);
                    QScriptValue entityScript = loadEntityScript(entityID);
                    if (entityScript.property("leaveEntity").isValid()) {
                        entityScript.property("leaveEntity").call(entityScript, entityArgs);
                    }

                }
            }

            // for all of our new containing entities, if they weren't previously containing then send them an enter event
            foreach(const EntityItemID& entityID, entitiesContainingAvatar) {
                if (!_currentEntitiesInside.contains(entityID)) {
                    emit enterEntity(entityID);
                    QScriptValueList entityArgs = createEntityArgs(entityID);
                    QScriptValue entityScript = loadEntityScript(entityID);
                    if (entityScript.property("enterEntity").isValid()) {
                        entityScript.property("enterEntity").call(entityScript, entityArgs);
                    }
                }
            }
            _currentEntitiesInside = entitiesContainingAvatar;
            _lastAvatarPosition = avatarPosition;
        }
    }
}

void EntityTreeRenderer::leaveAllEntities() {
    if (_tree && !_shuttingDown) {

        // for all of our previous containing entities, if they are no longer containing then send them a leave event
        foreach(const EntityItemID& entityID, _currentEntitiesInside) {
            emit leaveEntity(entityID);
            QScriptValueList entityArgs = createEntityArgs(entityID);
            QScriptValue entityScript = loadEntityScript(entityID);
            if (entityScript.property("leaveEntity").isValid()) {
                entityScript.property("leaveEntity").call(entityScript, entityArgs);
            }
        }
        _currentEntitiesInside.clear();
        
        // make sure our "last avatar position" is something other than our current position, so that on our
        // first chance, we'll check for enter/leave entity events.    
        _lastAvatarPosition = _viewState->getAvatarPosition() + glm::vec3((float)TREE_SCALE);
    }
}
void EntityTreeRenderer::render(RenderArgs::RenderMode renderMode,
                                RenderArgs::RenderSide renderSide,
                                RenderArgs::DebugFlags renderDebugFlags) {
    if (_tree && !_shuttingDown) {
        Model::startScene(renderSide);

        ViewFrustum* frustum = (renderMode == RenderArgs::SHADOW_RENDER_MODE) ?
            _viewState->getShadowViewFrustum() : _viewState->getCurrentViewFrustum();

        RenderArgs args(this, frustum, getSizeScale(), getBoundaryLevelAdjust(),
                        renderMode, renderSide, renderDebugFlags);

        _tree->lockForRead();

        // Whenever you're in an intersection between zones, we will always choose the smallest zone.
        _bestZone = NULL;
        _bestZoneVolume = std::numeric_limits<float>::max();
        _tree->recurseTreeWithOperation(renderOperation, &args);

        QSharedPointer<SceneScriptingInterface> scene = DependencyManager::get<SceneScriptingInterface>();
        
        if (_bestZone) {
            if (!_hasPreviousZone) {
                _previousKeyLightColor = scene->getKeyLightColor();
                _previousKeyLightIntensity = scene->getKeyLightIntensity();
                _previousKeyLightAmbientIntensity = scene->getKeyLightAmbientIntensity();
                _previousKeyLightDirection = scene->getKeyLightDirection();
                _previousStageSunModelEnabled = scene->isStageSunModelEnabled();
                _previousStageLongitude = scene->getStageLocationLongitude();
                _previousStageLatitude = scene->getStageLocationLatitude();
                _previousStageAltitude = scene->getStageLocationAltitude();
                _previousStageHour = scene->getStageDayTime();
                _previousStageDay = scene->getStageYearTime();
                _hasPreviousZone = true;
            }
            scene->setKeyLightColor(_bestZone->getKeyLightColorVec3());
            scene->setKeyLightIntensity(_bestZone->getKeyLightIntensity());
            scene->setKeyLightAmbientIntensity(_bestZone->getKeyLightAmbientIntensity());
            scene->setKeyLightDirection(_bestZone->getKeyLightDirection());
            scene->setStageSunModelEnable(_bestZone->getStageProperties().getSunModelEnabled());
            scene->setStageLocation(_bestZone->getStageProperties().getLongitude(), _bestZone->getStageProperties().getLatitude(),
                                    _bestZone->getStageProperties().getAltitude());
            scene->setStageDayTime(_bestZone->getStageProperties().calculateHour());
            scene->setStageYearTime(_bestZone->getStageProperties().calculateDay());

            if (_bestZone->getBackgroundMode() == BACKGROUND_MODE_ATMOSPHERE) {
                EnvironmentData data = _bestZone->getEnvironmentData();
                glm::vec3 keyLightDirection = scene->getKeyLightDirection();
                glm::vec3 inverseKeyLightDirection = keyLightDirection * -1.0f;
                
                // NOTE: is this right? It seems like the "sun" should be based on the center of the 
                //       atmosphere, not where the camera is.
                glm::vec3 keyLightLocation = _viewState->getAvatarPosition() 
                                                + (inverseKeyLightDirection * data.getAtmosphereOuterRadius());
                                                
                data.setSunLocation(keyLightLocation);

                const float KEY_LIGHT_INTENSITY_TO_SUN_BRIGHTNESS_RATIO = 20.0f;
                float sunBrightness = scene->getKeyLightIntensity() * KEY_LIGHT_INTENSITY_TO_SUN_BRIGHTNESS_RATIO;
                data.setSunBrightness(sunBrightness);

                _viewState->overrideEnvironmentData(data);
                scene->getSkyStage()->setBackgroundMode(model::SunSkyStage::SKY_DOME);

            } else {
                _viewState->endOverrideEnvironmentData();
                auto stage = scene->getSkyStage();
                 if (_bestZone->getBackgroundMode() == BACKGROUND_MODE_SKYBOX) {
                    stage->getSkybox()->setColor(_bestZone->getSkyboxProperties().getColorVec3());
                    if (_bestZone->getSkyboxProperties().getURL().isEmpty()) {
                        stage->getSkybox()->setCubemap(gpu::TexturePointer());
                    } else {
                        // Update the Texture of the Skybox with the one pointed by this zone
                        auto cubeMap = DependencyManager::get<TextureCache>()->getTexture(_bestZone->getSkyboxProperties().getURL(), CUBE_TEXTURE);
                        stage->getSkybox()->setCubemap(cubeMap->getGPUTexture()); 
                    }
                    stage->setBackgroundMode(model::SunSkyStage::SKY_BOX);
                } else {
                    stage->setBackgroundMode(model::SunSkyStage::SKY_DOME); // let the application atmosphere through
                }
            }

        } else {
            if (_hasPreviousZone) {
                scene->setKeyLightColor(_previousKeyLightColor);
                scene->setKeyLightIntensity(_previousKeyLightIntensity);
                scene->setKeyLightAmbientIntensity(_previousKeyLightAmbientIntensity);
                scene->setKeyLightDirection(_previousKeyLightDirection);
                scene->setStageSunModelEnable(_previousStageSunModelEnabled);
                scene->setStageLocation(_previousStageLongitude, _previousStageLatitude, 
                                        _previousStageAltitude);
                scene->setStageDayTime(_previousStageHour);
                scene->setStageYearTime(_previousStageDay);
                _hasPreviousZone = false;
            }
            _viewState->endOverrideEnvironmentData();
            scene->getSkyStage()->setBackgroundMode(model::SunSkyStage::SKY_DOME);  // let the application atmosphere through
        }

        // we must call endScene while we still have the tree locked so that no one deletes a model
        // on us while rendering the scene    
        Model::endScene(renderMode, &args);
        _tree->unlock();
    
        // stats...
        _meshesConsidered = args._meshesConsidered;
        _meshesRendered = args._meshesRendered;
        _meshesOutOfView = args._meshesOutOfView;
        _meshesTooSmall = args._meshesTooSmall;

        _elementsTouched = args._elementsTouched;
        _itemsRendered = args._itemsRendered;
        _itemsOutOfView = args._itemsOutOfView;
        _itemsTooSmall = args._itemsTooSmall;

        _materialSwitches = args._materialSwitches;
        _trianglesRendered = args._trianglesRendered;
        _quadsRendered = args._quadsRendered;

        _translucentMeshPartsRendered = args._translucentMeshPartsRendered;
        _opaqueMeshPartsRendered = args._opaqueMeshPartsRendered;
    }
    deleteReleasedModels(); // seems like as good as any other place to do some memory cleanup
}

const FBXGeometry* EntityTreeRenderer::getGeometryForEntity(EntityItemPointer entityItem) {
    const FBXGeometry* result = NULL;
    
    if (entityItem->getType() == EntityTypes::Model) {
        std::shared_ptr<RenderableModelEntityItem> modelEntityItem = 
                                                        std::dynamic_pointer_cast<RenderableModelEntityItem>(entityItem);
        assert(modelEntityItem); // we need this!!!
        Model* model = modelEntityItem->getModel(this);
        if (model) {
            result = &model->getGeometry()->getFBXGeometry();
        }
    }
    return result;
}

const Model* EntityTreeRenderer::getModelForEntityItem(EntityItemPointer entityItem) {
    const Model* result = NULL;
    if (entityItem->getType() == EntityTypes::Model) {
        std::shared_ptr<RenderableModelEntityItem> modelEntityItem = 
                                                        std::dynamic_pointer_cast<RenderableModelEntityItem>(entityItem);
        result = modelEntityItem->getModel(this);
    }
    return result;
}

const FBXGeometry* EntityTreeRenderer::getCollisionGeometryForEntity(EntityItemPointer entityItem) {
    const FBXGeometry* result = NULL;
    
    if (entityItem->getType() == EntityTypes::Model) {
        std::shared_ptr<RenderableModelEntityItem> modelEntityItem = 
                                                        std::dynamic_pointer_cast<RenderableModelEntityItem>(entityItem);
        if (modelEntityItem->hasCompoundShapeURL()) {
            Model* model = modelEntityItem->getModel(this);
            if (model) {
                const QSharedPointer<NetworkGeometry> collisionNetworkGeometry = model->getCollisionGeometry();
                if (!collisionNetworkGeometry.isNull()) {
                    result = &collisionNetworkGeometry->getFBXGeometry();
                }
            }
        }
    }
    return result;
}

void EntityTreeRenderer::renderElementProxy(EntityTreeElement* entityTreeElement) {
    glm::vec3 elementCenter = entityTreeElement->getAACube().calcCenter();
    float elementSize = entityTreeElement->getScale();
    glPushMatrix();
        glTranslatef(elementCenter.x, elementCenter.y, elementCenter.z);
        DependencyManager::get<DeferredLightingEffect>()->renderWireCube(elementSize, glm::vec4(1.0f, 0.0f, 0.0f, 1.0f));
    glPopMatrix();

    if (_displayElementChildProxies) {
        // draw the children
        float halfSize = elementSize / 2.0f;
        float quarterSize = elementSize / 4.0f;
        glPushMatrix();
            glTranslatef(elementCenter.x - quarterSize, elementCenter.y - quarterSize, elementCenter.z - quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(1.0f, 1.0f, 0.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x + quarterSize, elementCenter.y - quarterSize, elementCenter.z - quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(1.0f, 0.0f, 1.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x - quarterSize, elementCenter.y + quarterSize, elementCenter.z - quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(0.0f, 1.0f, 0.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x - quarterSize, elementCenter.y - quarterSize, elementCenter.z + quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(0.0f, 0.0f, 1.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x + quarterSize, elementCenter.y + quarterSize, elementCenter.z + quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(1.0f, 1.0f, 1.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x - quarterSize, elementCenter.y + quarterSize, elementCenter.z + quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(0.0f, 0.5f, 0.5f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x + quarterSize, elementCenter.y - quarterSize, elementCenter.z + quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(0.5f, 0.0f, 0.0f, 1.0f));
        glPopMatrix();

        glPushMatrix();
            glTranslatef(elementCenter.x + quarterSize, elementCenter.y + quarterSize, elementCenter.z - quarterSize);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(halfSize, glm::vec4(0.0f, 0.5f, 0.0f, 1.0f));
        glPopMatrix();
    }
}

void EntityTreeRenderer::renderProxies(EntityItemPointer entity, RenderArgs* args) {
    bool isShadowMode = args->_renderMode == RenderArgs::SHADOW_RENDER_MODE;
    if (!isShadowMode && _displayModelBounds) {
        PerformanceTimer perfTimer("renderProxies");

        AACube maxCube = entity->getMaximumAACube();
        AACube minCube = entity->getMinimumAACube();
        AABox entityBox = entity->getAABox();

        glm::vec3 maxCenter = maxCube.calcCenter();
        glm::vec3 minCenter = minCube.calcCenter();
        glm::vec3 entityBoxCenter = entityBox.calcCenter();
        glm::vec3 entityBoxScale = entityBox.getScale();

        // draw the max bounding cube
        glPushMatrix();
            glTranslatef(maxCenter.x, maxCenter.y, maxCenter.z);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(maxCube.getScale(), glm::vec4(1.0f, 1.0f, 0.0f, 1.0f));
        glPopMatrix();

        // draw the min bounding cube
        glPushMatrix();
            glTranslatef(minCenter.x, minCenter.y, minCenter.z);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(minCube.getScale(), glm::vec4(0.0f, 1.0f, 0.0f, 1.0f));
        glPopMatrix();
        
        // draw the entityBox bounding box
        glPushMatrix();
            glTranslatef(entityBoxCenter.x, entityBoxCenter.y, entityBoxCenter.z);
            glScalef(entityBoxScale.x, entityBoxScale.y, entityBoxScale.z);
            DependencyManager::get<DeferredLightingEffect>()->renderWireCube(1.0f, glm::vec4(0.0f, 0.0f, 1.0f, 1.0f));
        glPopMatrix();


        glm::vec3 position = entity->getPosition();
        glm::vec3 center = entity->getCenter();
        glm::vec3 dimensions = entity->getDimensions();
        glm::quat rotation = entity->getRotation();

        glPushMatrix();
            glTranslatef(position.x, position.y, position.z);
            glm::vec3 axis = glm::axis(rotation);
            glRotatef(glm::degrees(glm::angle(rotation)), axis.x, axis.y, axis.z);
            glPushMatrix();
                glm::vec3 positionToCenter = center - position;
                glTranslatef(positionToCenter.x, positionToCenter.y, positionToCenter.z);
                glScalef(dimensions.x, dimensions.y, dimensions.z);
                DependencyManager::get<DeferredLightingEffect>()->renderWireCube(1.0f, glm::vec4(1.0f, 0.0f, 1.0f, 1.0f));
            glPopMatrix();
        glPopMatrix();
    }
}

void EntityTreeRenderer::renderElement(OctreeElement* element, RenderArgs* args) {
    args->_elementsTouched++;
    // actually render it here...
    // we need to iterate the actual entityItems of the element
    EntityTreeElement* entityTreeElement = static_cast<EntityTreeElement*>(element);

    EntityItems& entityItems = entityTreeElement->getEntities();
    

    uint16_t numberOfEntities = entityItems.size();

    bool isShadowMode = args->_renderMode == RenderArgs::SHADOW_RENDER_MODE;

    if (!isShadowMode && _displayModelElementProxy && numberOfEntities > 0) {
        renderElementProxy(entityTreeElement);
    }
    
    for (uint16_t i = 0; i < numberOfEntities; i++) {
        EntityItemPointer entityItem = entityItems[i];
        
        if (entityItem->isVisible()) {

            // NOTE: Zone Entities are a special case we handle here...
            if (entityItem->getType() == EntityTypes::Zone) {
                if (entityItem->contains(_viewState->getAvatarPosition())) {
                    float entityVolumeEstimate = entityItem->getVolumeEstimate();
                    if (entityVolumeEstimate < _bestZoneVolume) {
                        _bestZoneVolume = entityVolumeEstimate;
                        _bestZone = std::dynamic_pointer_cast<ZoneEntityItem>(entityItem);
                    } else if (entityVolumeEstimate == _bestZoneVolume) {
                        if (!_bestZone) {
                            _bestZoneVolume = entityVolumeEstimate;
                            _bestZone = std::dynamic_pointer_cast<ZoneEntityItem>(entityItem);
                        } else {
                            // in the case of the volume being equal, we will use the
                            // EntityItemID to deterministically pick one entity over the other
                            if (entityItem->getEntityItemID() < _bestZone->getEntityItemID()) {
                                _bestZoneVolume = entityVolumeEstimate;
                                _bestZone = std::dynamic_pointer_cast<ZoneEntityItem>(entityItem);
                            }
                        }
                    }
                }
            }
            
            // render entityItem
            AABox entityBox = entityItem->getAABox();
            
            // TODO: some entity types (like lights) might want to be rendered even
            // when they are outside of the view frustum...
            float distance = args->_viewFrustum->distanceToCamera(entityBox.calcCenter());
            
            bool outOfView = args->_viewFrustum->boxInFrustum(entityBox) == ViewFrustum::OUTSIDE;
            if (!outOfView) {
                bool bigEnoughToRender = _viewState->shouldRenderMesh(entityBox.getLargestDimension(), distance);
                
                if (bigEnoughToRender) {
                    renderProxies(entityItem, args);
                    
                    Glower* glower = NULL;
                    if (entityItem->getGlowLevel() > 0.0f) {
                        glower = new Glower(entityItem->getGlowLevel());
                    }
                    entityItem->render(args);
                    args->_itemsRendered++;
                    if (glower) {
                        delete glower;
                    }
                } else {
                    args->_itemsTooSmall++;
                }
            } else {
                args->_itemsOutOfView++;
            }
        }
    }
}

float EntityTreeRenderer::getSizeScale() const {
    return _viewState->getSizeScale();
}

int EntityTreeRenderer::getBoundaryLevelAdjust() const { 
    return _viewState->getBoundaryLevelAdjust();
}


void EntityTreeRenderer::processEraseMessage(const QByteArray& dataByteArray, const SharedNodePointer& sourceNode) {
    static_cast<EntityTree*>(_tree)->processEraseMessage(dataByteArray, sourceNode);
}

Model* EntityTreeRenderer::allocateModel(const QString& url, const QString& collisionUrl) {
    Model* model = NULL;
    // Make sure we only create and delete models on the thread that owns the EntityTreeRenderer
    if (QThread::currentThread() != thread()) {
        QMetaObject::invokeMethod(this, "allocateModel", Qt::BlockingQueuedConnection, 
                Q_RETURN_ARG(Model*, model),
                Q_ARG(const QString&, url));

        return model;
    }
    model = new Model();
    model->init();
    model->setURL(QUrl(url));
    model->setCollisionModelURL(QUrl(collisionUrl));
    return model;
}

Model* EntityTreeRenderer::updateModel(Model* original, const QString& newUrl, const QString& collisionUrl) {
    Model* model = NULL;

    // The caller shouldn't call us if the URL doesn't need to change. But if they
    // do, we just return their original back to them.
    if (!original || (QUrl(newUrl) == original->getURL())) {
        return original;
    }

    // Before we do any creating or deleting, make sure we're on our renderer thread
    if (QThread::currentThread() != thread()) {
        QMetaObject::invokeMethod(this, "updateModel", Qt::BlockingQueuedConnection, 
                Q_RETURN_ARG(Model*, model),
                Q_ARG(Model*, original),
                Q_ARG(const QString&, newUrl));

        return model;
    }

    // at this point we know we need to replace the model, and we know we're on the
    // correct thread, so we can do all our work.
    if (original) {
        delete original; // delete the old model...
    }

    // create the model and correctly initialize it with the new url
    model = new Model();
    model->init();
    model->setURL(QUrl(newUrl));
    model->setCollisionModelURL(QUrl(collisionUrl));
        
    return model;
}

void EntityTreeRenderer::releaseModel(Model* model) {
    // If we're not on the renderer's thread, then remember this model to be deleted later
    if (QThread::currentThread() != thread()) {
        _releasedModels << model;
    } else { // otherwise just delete it right away
        delete model;
    }
}

void EntityTreeRenderer::deleteReleasedModels() {
    if (_releasedModels.size() > 0) {
        foreach(Model* model, _releasedModels) {
            delete model;
        }
        _releasedModels.clear();
    }
}

RayToEntityIntersectionResult EntityTreeRenderer::findRayIntersectionWorker(const PickRay& ray, Octree::lockType lockType, 
                                                                                    bool precisionPicking) {
    RayToEntityIntersectionResult result;
    if (_tree) {
        EntityTree* entityTree = static_cast<EntityTree*>(_tree);

        OctreeElement* element;
        EntityItemPointer intersectedEntity = NULL;
        result.intersects = entityTree->findRayIntersection(ray.origin, ray.direction, element, result.distance, result.face, 
                                                                (void**)&intersectedEntity, lockType, &result.accurate, 
                                                                precisionPicking);
        if (result.intersects && intersectedEntity) {
            result.entityID = intersectedEntity->getEntityItemID();
            result.properties = intersectedEntity->getProperties();
            result.intersection = ray.origin + (ray.direction * result.distance);
            result.entity = intersectedEntity;
        }
    }
    return result;
}

void EntityTreeRenderer::connectSignalsToSlots(EntityScriptingInterface* entityScriptingInterface) {
    connect(this, &EntityTreeRenderer::mousePressOnEntity, entityScriptingInterface, 
        [=](const RayToEntityIntersectionResult& intersection, const QMouseEvent* event, unsigned int deviceId){
        entityScriptingInterface->mousePressOnEntity(intersection.entityID, MouseEvent(*event, deviceId));
    });
    connect(this, &EntityTreeRenderer::mouseMoveOnEntity, entityScriptingInterface, 
        [=](const RayToEntityIntersectionResult& intersection, const QMouseEvent* event, unsigned int deviceId) {
        entityScriptingInterface->mouseMoveOnEntity(intersection.entityID, MouseEvent(*event, deviceId));
    });
    connect(this, &EntityTreeRenderer::mouseReleaseOnEntity, entityScriptingInterface, 
        [=](const RayToEntityIntersectionResult& intersection, const QMouseEvent* event, unsigned int deviceId) {
        entityScriptingInterface->mouseReleaseOnEntity(intersection.entityID, MouseEvent(*event, deviceId));
    });

    connect(this, &EntityTreeRenderer::clickDownOnEntity, entityScriptingInterface, &EntityScriptingInterface::clickDownOnEntity);
    connect(this, &EntityTreeRenderer::holdingClickOnEntity, entityScriptingInterface, &EntityScriptingInterface::holdingClickOnEntity);
    connect(this, &EntityTreeRenderer::clickReleaseOnEntity, entityScriptingInterface, &EntityScriptingInterface::clickReleaseOnEntity);

    connect(this, &EntityTreeRenderer::hoverEnterEntity, entityScriptingInterface, &EntityScriptingInterface::hoverEnterEntity);
    connect(this, &EntityTreeRenderer::hoverOverEntity, entityScriptingInterface, &EntityScriptingInterface::hoverOverEntity);
    connect(this, &EntityTreeRenderer::hoverLeaveEntity, entityScriptingInterface, &EntityScriptingInterface::hoverLeaveEntity);

    connect(this, &EntityTreeRenderer::enterEntity, entityScriptingInterface, &EntityScriptingInterface::enterEntity);
    connect(this, &EntityTreeRenderer::leaveEntity, entityScriptingInterface, &EntityScriptingInterface::leaveEntity);
    connect(this, &EntityTreeRenderer::collisionWithEntity, entityScriptingInterface, &EntityScriptingInterface::collisionWithEntity);
}

QScriptValueList EntityTreeRenderer::createMouseEventArgs(const EntityItemID& entityID, QMouseEvent* event, unsigned int deviceID) {
    QScriptValueList args;
    args << entityID.toScriptValue(_entitiesScriptEngine);
    args << MouseEvent(*event, deviceID).toScriptValue(_entitiesScriptEngine);
    return args;
}

QScriptValueList EntityTreeRenderer::createMouseEventArgs(const EntityItemID& entityID, const MouseEvent& mouseEvent) {
    QScriptValueList args;
    args << entityID.toScriptValue(_entitiesScriptEngine);
    args << mouseEvent.toScriptValue(_entitiesScriptEngine);
    return args;
}


QScriptValueList EntityTreeRenderer::createEntityArgs(const EntityItemID& entityID) {
    QScriptValueList args;
    args << entityID.toScriptValue(_entitiesScriptEngine);
    return args;
}

void EntityTreeRenderer::mousePressEvent(QMouseEvent* event, unsigned int deviceID) {
    // If we don't have a tree, or we're in the process of shutting down, then don't
    // process these events.
    if (!_tree || _shuttingDown) {
        return;
    }
    PerformanceTimer perfTimer("EntityTreeRenderer::mousePressEvent");
    PickRay ray = _viewState->computePickRay(event->x(), event->y());

    bool precisionPicking = !_dontDoPrecisionPicking;
    RayToEntityIntersectionResult rayPickResult = findRayIntersectionWorker(ray, Octree::Lock, precisionPicking);
    if (rayPickResult.intersects) {
        //qCDebug(entitiesrenderer) << "mousePressEvent over entity:" << rayPickResult.entityID;
        emit mousePressOnEntity(rayPickResult, event, deviceID);

        QScriptValueList entityScriptArgs = createMouseEventArgs(rayPickResult.entityID, event, deviceID);
        QScriptValue entityScript = loadEntityScript(rayPickResult.entity);
        if (entityScript.property("mousePressOnEntity").isValid()) {
            entityScript.property("mousePressOnEntity").call(entityScript, entityScriptArgs);
        }
    
        _currentClickingOnEntityID = rayPickResult.entityID;
        emit clickDownOnEntity(_currentClickingOnEntityID, MouseEvent(*event, deviceID));
        if (entityScript.property("clickDownOnEntity").isValid()) {
            entityScript.property("clickDownOnEntity").call(entityScript, entityScriptArgs);
        }
    }
    _lastMouseEvent = MouseEvent(*event, deviceID);
    _lastMouseEventValid = true;
}

void EntityTreeRenderer::mouseReleaseEvent(QMouseEvent* event, unsigned int deviceID) {
    // If we don't have a tree, or we're in the process of shutting down, then don't
    // process these events.
    if (!_tree || _shuttingDown) {
        return;
    }
    PerformanceTimer perfTimer("EntityTreeRenderer::mouseReleaseEvent");
    PickRay ray = _viewState->computePickRay(event->x(), event->y());
    bool precisionPicking = !_dontDoPrecisionPicking;
    RayToEntityIntersectionResult rayPickResult = findRayIntersectionWorker(ray, Octree::Lock, precisionPicking);
    if (rayPickResult.intersects) {
        //qCDebug(entitiesrenderer) << "mouseReleaseEvent over entity:" << rayPickResult.entityID;
        emit mouseReleaseOnEntity(rayPickResult, event, deviceID);

        QScriptValueList entityScriptArgs = createMouseEventArgs(rayPickResult.entityID, event, deviceID);
        QScriptValue entityScript = loadEntityScript(rayPickResult.entity);
        if (entityScript.property("mouseReleaseOnEntity").isValid()) {
            entityScript.property("mouseReleaseOnEntity").call(entityScript, entityScriptArgs);
        }
    }

    // Even if we're no longer intersecting with an entity, if we started clicking on it, and now
    // we're releasing the button, then this is considered a clickOn event
    if (!_currentClickingOnEntityID.isInvalidID()) {
        emit clickReleaseOnEntity(_currentClickingOnEntityID, MouseEvent(*event, deviceID));

        QScriptValueList currentClickingEntityArgs = createMouseEventArgs(_currentClickingOnEntityID, event, deviceID);
        QScriptValue currentClickingEntity = loadEntityScript(_currentClickingOnEntityID);
        if (currentClickingEntity.property("clickReleaseOnEntity").isValid()) {
            currentClickingEntity.property("clickReleaseOnEntity").call(currentClickingEntity, currentClickingEntityArgs);
        }
    }

    // makes it the unknown ID, we just released so we can't be clicking on anything
    _currentClickingOnEntityID = UNKNOWN_ENTITY_ID;
    _lastMouseEvent = MouseEvent(*event, deviceID);
    _lastMouseEventValid = true;
}

void EntityTreeRenderer::mouseMoveEvent(QMouseEvent* event, unsigned int deviceID) {
    // If we don't have a tree, or we're in the process of shutting down, then don't
    // process these events.
    if (!_tree || _shuttingDown) {
        return;
    }
    PerformanceTimer perfTimer("EntityTreeRenderer::mouseMoveEvent");

    PickRay ray = _viewState->computePickRay(event->x(), event->y());

    bool precisionPicking = false; // for mouse moves we do not do precision picking
    RayToEntityIntersectionResult rayPickResult = findRayIntersectionWorker(ray, Octree::TryLock, precisionPicking);
    if (rayPickResult.intersects) {
        QScriptValueList entityScriptArgs = createMouseEventArgs(rayPickResult.entityID, event, deviceID);

        // load the entity script if needed...
        QScriptValue entityScript = loadEntityScript(rayPickResult.entity);
        if (entityScript.property("mouseMoveEvent").isValid()) {
            entityScript.property("mouseMoveEvent").call(entityScript, entityScriptArgs);
        }

        //qCDebug(entitiesrenderer) << "mouseMoveEvent over entity:" << rayPickResult.entityID;
        emit mouseMoveOnEntity(rayPickResult, event, deviceID);
        if (entityScript.property("mouseMoveOnEntity").isValid()) {
            entityScript.property("mouseMoveOnEntity").call(entityScript, entityScriptArgs);
        }
    
        // handle the hover logic...
    
        // if we were previously hovering over an entity, and this new entity is not the same as our previous entity
        // then we need to send the hover leave.
        if (!_currentHoverOverEntityID.isInvalidID() && rayPickResult.entityID != _currentHoverOverEntityID) {
            emit hoverLeaveEntity(_currentHoverOverEntityID, MouseEvent(*event, deviceID));

            QScriptValueList currentHoverEntityArgs = createMouseEventArgs(_currentHoverOverEntityID, event, deviceID);

            QScriptValue currentHoverEntity = loadEntityScript(_currentHoverOverEntityID);
            if (currentHoverEntity.property("hoverLeaveEntity").isValid()) {
                currentHoverEntity.property("hoverLeaveEntity").call(currentHoverEntity, currentHoverEntityArgs);
            }
        }

        // If the new hover entity does not match the previous hover entity then we are entering the new one
        // this is true if the _currentHoverOverEntityID is known or unknown
        if (rayPickResult.entityID != _currentHoverOverEntityID) {
            emit hoverEnterEntity(rayPickResult.entityID, MouseEvent(*event, deviceID));
            if (entityScript.property("hoverEnterEntity").isValid()) {
                entityScript.property("hoverEnterEntity").call(entityScript, entityScriptArgs);
            }
        }

        // and finally, no matter what, if we're intersecting an entity then we're definitely hovering over it, and
        // we should send our hover over event
        emit hoverOverEntity(rayPickResult.entityID, MouseEvent(*event, deviceID));
        if (entityScript.property("hoverOverEntity").isValid()) {
            entityScript.property("hoverOverEntity").call(entityScript, entityScriptArgs);
        }

        // remember what we're hovering over
        _currentHoverOverEntityID = rayPickResult.entityID;

    } else {
        // handle the hover logic...
        // if we were previously hovering over an entity, and we're no longer hovering over any entity then we need to 
        // send the hover leave for our previous entity
        if (!_currentHoverOverEntityID.isInvalidID()) {
            emit hoverLeaveEntity(_currentHoverOverEntityID, MouseEvent(*event, deviceID));

            QScriptValueList currentHoverEntityArgs = createMouseEventArgs(_currentHoverOverEntityID, event, deviceID);

            QScriptValue currentHoverEntity = loadEntityScript(_currentHoverOverEntityID);
            if (currentHoverEntity.property("hoverLeaveEntity").isValid()) {
                currentHoverEntity.property("hoverLeaveEntity").call(currentHoverEntity, currentHoverEntityArgs);
            }

            _currentHoverOverEntityID = UNKNOWN_ENTITY_ID; // makes it the unknown ID
        }
    }

    // Even if we're no longer intersecting with an entity, if we started clicking on an entity and we have
    // not yet released the hold then this is still considered a holdingClickOnEntity event
    if (!_currentClickingOnEntityID.isInvalidID()) {
        emit holdingClickOnEntity(_currentClickingOnEntityID, MouseEvent(*event, deviceID));

        QScriptValueList currentClickingEntityArgs = createMouseEventArgs(_currentClickingOnEntityID, event, deviceID);

        QScriptValue currentClickingEntity = loadEntityScript(_currentClickingOnEntityID);
        if (currentClickingEntity.property("holdingClickOnEntity").isValid()) {
            currentClickingEntity.property("holdingClickOnEntity").call(currentClickingEntity, currentClickingEntityArgs);
        }
    }
    _lastMouseEvent = MouseEvent(*event, deviceID);
    _lastMouseEventValid = true;
}

void EntityTreeRenderer::deletingEntity(const EntityItemID& entityID) {
    if (_tree && !_shuttingDown) {
        checkAndCallUnload(entityID);
    }
    _entityScripts.remove(entityID);
}

void EntityTreeRenderer::addingEntity(const EntityItemID& entityID) {
    checkAndCallPreload(entityID);
}

void EntityTreeRenderer::entitySciptChanging(const EntityItemID& entityID) {
    if (_tree && !_shuttingDown) {
        checkAndCallUnload(entityID);
        checkAndCallPreload(entityID);
    }
}

void EntityTreeRenderer::checkAndCallPreload(const EntityItemID& entityID) {
    if (_tree && !_shuttingDown) {
        // load the entity script if needed...
        QScriptValue entityScript = loadEntityScript(entityID, true); // is preload!
        if (entityScript.property("preload").isValid()) {
            QScriptValueList entityArgs = createEntityArgs(entityID);
            entityScript.property("preload").call(entityScript, entityArgs);
        }
    }
}

void EntityTreeRenderer::checkAndCallUnload(const EntityItemID& entityID) {
    if (_tree && !_shuttingDown) {
        QScriptValue entityScript = getPreviouslyLoadedEntityScript(entityID);
        if (entityScript.property("unload").isValid()) {
            QScriptValueList entityArgs = createEntityArgs(entityID);
            entityScript.property("unload").call(entityScript, entityArgs);
        }
    }
}


void EntityTreeRenderer::playEntityCollisionSound(const QUuid& myNodeID, EntityTree* entityTree, const EntityItemID& id, const Collision& collision) {
    EntityItemPointer entity = entityTree->findEntityByEntityItemID(id);
    if (!entity) {
        return;
    }
    QUuid simulatorID = entity->getSimulatorID();
    if (simulatorID.isNull() || (simulatorID != myNodeID)) {
        return; // Only one injector per simulation, please.
    }
    const QString& collisionSoundURL = entity->getCollisionSoundURL();
    if (collisionSoundURL.isEmpty()) {
        return;
    }
    const float mass = entity->computeMass();
    const float COLLISION_PENTRATION_TO_VELOCITY = 50; // as a subsitute for RELATIVE entity->getVelocity()
    const float linearVelocity = glm::length(collision.penetration) * COLLISION_PENTRATION_TO_VELOCITY;
    const float energy = mass * linearVelocity * linearVelocity / 2.0f;
    const glm::vec3 position = collision.contactPoint;
    const float COLLISION_ENERGY_AT_FULL_VOLUME = 0.5f;
    const float COLLISION_MINIMUM_VOLUME = 0.001f;
    const float energyFactorOfFull = fmin(1.0f, energy / COLLISION_ENERGY_AT_FULL_VOLUME);
    if (energyFactorOfFull < COLLISION_MINIMUM_VOLUME) {
        return;
    }

    auto soundCache = DependencyManager::get<SoundCache>();
    if (soundCache.isNull()) {
        return;
    }
    SharedSoundPointer sound = soundCache.data()->getSound(QUrl(collisionSoundURL));
    if (sound.isNull() || !sound->isReady()) {
        return;
    }

    // This is a hack. Quiet sound aren't really heard at all, so we compress everything to the range [1-c, 1], if we play it all.
    const float COLLISION_SOUND_COMPRESSION_RANGE = 0.7f;
    float volume = energyFactorOfFull;
    volume = (volume * COLLISION_SOUND_COMPRESSION_RANGE) + (1.0f - COLLISION_SOUND_COMPRESSION_RANGE);
    
    // This is quite similar to AudioScriptingInterface::playSound() and should probably be refactored.
    AudioInjectorOptions options;
    options.stereo = sound->isStereo();
    options.position = position;
    options.volume = volume;
    AudioInjector* injector = new AudioInjector(sound.data(), options);
    injector->setLocalAudioInterface(_localAudioInterface);
    injector->triggerDeleteAfterFinish();
    QThread* injectorThread = new QThread();
    injectorThread->setObjectName("Audio Injector Thread");
    injector->moveToThread(injectorThread);
    // start injecting when the injector thread starts
    connect(injectorThread, &QThread::started, injector, &AudioInjector::injectAudio);
    // connect the right slots and signals for AudioInjector and thread cleanup
    connect(injector, &AudioInjector::destroyed, injectorThread, &QThread::quit);
    connect(injectorThread, &QThread::finished, injectorThread, &QThread::deleteLater);
    injectorThread->start();
}

void EntityTreeRenderer::entityCollisionWithEntity(const EntityItemID& idA, const EntityItemID& idB,
                                                    const Collision& collision) {
    // If we don't have a tree, or we're in the process of shutting down, then don't
    // process these events.
    if (!_tree || _shuttingDown) {
        return;
    }
    // Don't respond to small continuous contacts.
    const float COLLISION_MINUMUM_PENETRATION = 0.005f;
    if ((collision.type != CONTACT_EVENT_TYPE_START) && (glm::length(collision.penetration) < COLLISION_MINUMUM_PENETRATION)) {
        return;
    }

    // See if we should play sounds
    EntityTree* entityTree = static_cast<EntityTree*>(_tree);
    const QUuid& myNodeID = DependencyManager::get<NodeList>()->getSessionUUID();
    playEntityCollisionSound(myNodeID, entityTree, idA, collision);
    playEntityCollisionSound(myNodeID, entityTree, idB, collision);

    // And now the entity scripts
    emit collisionWithEntity(idA, idB, collision);
    QScriptValue entityScriptA = loadEntityScript(idA);
    if (entityScriptA.property("collisionWithEntity").isValid()) {
        QScriptValueList args;
        args << idA.toScriptValue(_entitiesScriptEngine);
        args << idB.toScriptValue(_entitiesScriptEngine);
        args << collisionToScriptValue(_entitiesScriptEngine, collision);
        entityScriptA.property("collisionWithEntity").call(entityScriptA, args);
    }

    emit collisionWithEntity(idB, idA, collision);
    QScriptValue entityScriptB = loadEntityScript(idB);
    if (entityScriptB.property("collisionWithEntity").isValid()) {
        QScriptValueList args;
        args << idB.toScriptValue(_entitiesScriptEngine);
        args << idA.toScriptValue(_entitiesScriptEngine);
        args << collisionToScriptValue(_entitiesScriptEngine, collision);
        entityScriptB.property("collisionWithEntity").call(entityScriptA, args);
    }
}

