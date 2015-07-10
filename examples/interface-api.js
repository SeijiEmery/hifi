var Entities = {
	// native class
};
/** 
 * @param QString actionTypeString
 * @param QUuid entityID
 * @param QVariantMap args
 * @returns QUuid
 */
Entities.addAction = function (actionTypeString, entityID, args) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:131)
    return {};
};
/** 
 * @returns bool
 */
Entities.canAdjustLocks = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:69)
    return false;
};
/** finds the closest model to the center point, within the radius will return a EntityItemID.isKnownID = false if no models are in the radius this function will not find any models in script engine contexts which don't have access to models * @param glm::vec3 center
 * @param float radius
 * @returns QUuid
 */
Entities.findClosestEntity = function (center, radius) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:91)
    return {};
};
/** 
 * @param bool value
 * @returns void
 */
Entities.setLightsArePickable = function (value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:110)
};
/** 
 * @param QUuid entityID
 * @param int value
 * @returns bool
 */
Entities.setAllVoxels = function (entityID, value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:124)
    return false;
};
/** adds a model with the specific properties * @param EntityItemProperties properties
 * @returns QUuid
 */
Entities.addEntity = function (properties) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:75)
    return {};
};
/** finds models within the search sphere specified by the center point and radius this function will not find any models in script engine contexts which don't have access to models * @param glm::vec3 corner
 * @param glm::vec3 dimensions
 * @returns QVector< QUuid >
 */
Entities.findEntitiesInBox = function (corner, dimensions) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:99)
    return [ {} ];
};
/** 
 * @param QUuid entityID
 * @param glm::vec3 center
 * @param float radius
 * @param int value
 * @returns bool
 */
Entities.setVoxelSphere = function (entityID, center, radius, value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:122)
    return false;
};
/** 
 * @returns void
 */
Entities.dumpTree = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:129)
};
/** 
 * @param QUuid entityID
 * @param QUuid actionID
 * @returns QVariantMap
 */
Entities.getActionArguments = function (entityID, actionID) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:135)
    return {};
};
/** 
 * @param QUuid entityID
 * @returns QVector< QUuid >
 */
Entities.getActionIDs = function (entityID) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:134)
    return [ {} ];
};
/** 
 * @param bool value
 * @returns void
 */
Entities.setSendPhysicsUpdates = function (value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:119)
};
/** edits a model updating only the included properties, will return the identified EntityItemID * @param QUuid entityID
 * @param EntityItemProperties properties
 * @returns QUuid
 */
Entities.editEntity = function (entityID, properties) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:83)
    return {};
};
/** 
 * @param QUuid entityID
 * @param QUuid actionID
 * @returns bool
 */
Entities.deleteAction = function (entityID, actionID) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:133)
    return false;
};
/** deletes a model * @param QUuid entityID
 * @returns void
 */
Entities.deleteEntity = function (entityID) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:86)
};
/** 
 * @param QUuid entityID
 * @param QVector< glm::vec3 > points
 * @returns bool
 */
Entities.setAllPoints = function (entityID, points) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:126)
    return false;
};
/** If the scripting context has visible entities, this will determine a ray intersection, and will block in order to return an accurate result. * @param PickRay ray
 * @param bool precisionPicking = false
 * @returns RayToEntityIntersectionResult
 */
Entities.findRayIntersectionBlocking = function (ray, precisionPicking) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:108)
};
/** 
 * @param bool value
 * @returns void
 */
Entities.setZonesArePickable = function (value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:113)
};
/** If the scripting context has visible entities, this will determine a ray intersection, the results may be inaccurate if the engine is unable to access the visible entities, in which case result.accurate will be false. * @param PickRay ray
 * @param bool precisionPicking = false
 * @returns RayToEntityIntersectionResult
 */
Entities.findRayIntersection = function (ray, precisionPicking) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:104)
};
/** gets the current model properties for a specific model this function will not find return results in script engine contexts which don't have access to models * @param QUuid entityID
 * @returns EntityItemProperties
 */
Entities.getEntityProperties = function (entityID) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:79)
};
/** 
 * @returns bool
 */
Entities.getDrawZoneBoundaries = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:117)
    return false;
};
/** 
 * @returns bool
 */
Entities.canRez = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:72)
    return false;
};
/** 
 * @param QUuid entityID
 * @param glm::vec3 point
 * @returns bool
 */
Entities.appendPoint = function (entityID, point) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:127)
    return false;
};
/** 
 * @param QUuid entityID
 * @param glm::vec3 position
 * @param int value
 * @returns bool
 */
Entities.setVoxel = function (entityID, position, value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:123)
    return false;
};
/** 
 * @returns bool
 */
Entities.getZonesArePickable = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:114)
    return false;
};
/** 
 * @returns bool
 */
Entities.getLightsArePickable = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:111)
    return false;
};
/** 
 * @param bool value
 * @returns void
 */
Entities.setDrawZoneBoundaries = function (value) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:116)
};
/** 
 * @returns bool
 */
Entities.getSendPhysicsUpdates = function () {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:120)
    return false;
};
/** finds models within the search sphere specified by the center point and radius this function will not find any models in script engine contexts which don't have access to models * @param glm::vec3 center
 * @param float radius
 * @returns QVector< QUuid >
 */
Entities.findEntities = function (center, radius) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:95)
    return [ {} ];
};
/** 
 * @param QUuid entityID
 * @param QUuid actionID
 * @param QVariantMap arguments
 * @returns bool
 */
Entities.updateAction = function (entityID, actionID, arguments) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/entities/src/EntityScriptingInterface.h:132)
    return false;
};
var Vec3 = {
	// native class
};
/** 
 * @param glm::vec3 v
 * @returns glm::vec3
 */
Vec3.normalize = function (v) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:39)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns float
 */
Vec3.distance = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:37)
    return 0.0;
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @param glm::vec3 v3
 * @returns float
 */
Vec3.orientedAngle = function (v1, v2, v3) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:38)
    return 0.0;
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns glm::vec3
 */
Vec3.sum = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:34)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns glm::vec3
 */
Vec3.cross = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:29)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns bool
 */
Vec3.equal = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:42)
    return false;
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns glm::vec3
 */
Vec3.reflect = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:28)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @param float m
 * @returns glm::vec3
 */
Vec3.mix = function (v1, v2, m) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:40)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v
 * @returns float
 */
Vec3.length = function (v) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:36)
    return 0.0;
};
/** 
 * @param glm::quat q
 * @param glm::vec3 v
 * @returns glm::vec3
 */
Vec3.multiplyQbyV = function (q, v) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:33)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param QString lable
 * @param glm::vec3 v
 * @returns void
 */
Vec3.print = function (lable, v) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:41)
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns glm::vec3
 */
Vec3.subtract = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:35)
    return { x: 0.0, y: 0.0, z: 0.0 };
};
/** 
 * @param glm::vec3 v1
 * @param glm::vec3 v2
 * @returns float
 */
Vec3.dot = function (v1, v2) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:30)
    return 0.0;
};
/** 
 * @param float f
 * @param glm::vec3 v1
 * @returns glm::vec3
 */
Vec3.multiply = function (f, v1) {
    // native code
    // (/Users/semery/hifi-docgen/libraries/script-engine/src/Vec3.h:32)
    return { x: 0.0, y: 0.0, z: 0.0 };
};