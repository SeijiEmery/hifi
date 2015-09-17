//
//  Camera.cpp
//  interface/src
//
//  Copyright 2013 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#include <glm/gtx/quaternion.hpp>

#include <SharedUtil.h>
#include <EventTypes.h>

#include "Application.h"
#include "Camera.h"
#include "Menu.h"
#include "Util.h"


CameraMode stringToMode(const QString& mode) {
    if (mode == "third person") {
        return CAMERA_MODE_THIRD_PERSON;
    } else if (mode == "first person") {
        return CAMERA_MODE_FIRST_PERSON;
    } else if (mode == "mirror") {
        return CAMERA_MODE_MIRROR;
    } else if (mode == "independent") {
        return CAMERA_MODE_INDEPENDENT;
    }
    return CAMERA_MODE_NULL;
}

QString modeToString(CameraMode mode) {
    if (mode == CAMERA_MODE_THIRD_PERSON) {
        return "third person";
    } else if (mode == CAMERA_MODE_FIRST_PERSON) {
        return "first person";
    } else if (mode == CAMERA_MODE_MIRROR) {
        return "mirror";
    } else if (mode == CAMERA_MODE_INDEPENDENT) {
        return "independent";
    }
    return "unknown";
}

Camera::Camera() : 
    _projection(glm::perspective(glm::radians(DEFAULT_FIELD_OF_VIEW_DEGREES), 16.0f/9.0f, DEFAULT_NEAR_CLIP, DEFAULT_FAR_CLIP))
{
}

void Camera::update(float deltaTime) {
    if (_isKeepLookingAt) {
        lookAt(_lookingAt);
    }
    return;
}

void Camera::recompose() {
    mat4 orientation = glm::mat4_cast(_rotation);
    mat4 translation = glm::translate(mat4(), _position);
    _transform = translation * orientation;
}

void Camera::decompose() {
    _position = vec3(_transform[3]);
    _rotation = glm::quat_cast(_transform);
}

void Camera::setTransform(const glm::mat4& transform) {
    _transform = transform;
    decompose();
}

void Camera::setPosition(const glm::vec3& position) {
    _position = position;
    recompose();
    if (_isKeepLookingAt) {
        lookAt(_lookingAt);
    }
}

void Camera::setRotation(const glm::quat& rotation) {
    _rotation = rotation; 
    recompose();
    if (_isKeepLookingAt) {
        lookAt(_lookingAt);
    }
}

void Camera::setMode(CameraMode mode) {
    _mode = mode;
    emit modeUpdated(modeToString(mode));
}

void Camera::setProjection(const glm::mat4& projection) { 
    _projection = projection;
}

PickRay Camera::computePickRay(float x, float y) {
    return qApp->computePickRay(x, y);
}

void Camera::setModeString(const QString& mode) {
    CameraMode targetMode = stringToMode(mode);
        
    switch (targetMode) {
        case CAMERA_MODE_FIRST_PERSON:
            Menu::getInstance()->setIsOptionChecked(MenuOption::FirstPerson, true);
            break;
        case CAMERA_MODE_THIRD_PERSON:
            Menu::getInstance()->setIsOptionChecked(MenuOption::ThirdPerson, true);
            break;
        case CAMERA_MODE_MIRROR:
            Menu::getInstance()->setIsOptionChecked(MenuOption::FullscreenMirror, true);
            break;
        case CAMERA_MODE_INDEPENDENT:
            Menu::getInstance()->setIsOptionChecked(MenuOption::IndependentMode, true);
            break;
        default:
            break;
    }
    
    qApp->cameraMenuChanged();
    
    if (_mode != targetMode) {
        setMode(targetMode);
    }
}

QString Camera::getModeString() const {
    return modeToString(_mode);
}

void Camera::lookAt(const glm::vec3& lookAt) {
    glm::vec3 up = IDENTITY_UP;
    glm::mat4 lookAtMatrix = glm::lookAt(_position, lookAt, up);
    glm::quat rotation = glm::quat_cast(lookAtMatrix);
    rotation.w = -rotation.w; // Rosedale approved
    _rotation = rotation;
}

void Camera::keepLookingAt(const glm::vec3& point) {
    lookAt(point);
    _isKeepLookingAt = true;
    _lookingAt = point;
}

void Camera::loadViewFrustum(ViewFrustum& frustum) const {
    // We will use these below, from either the camera or head vectors calculated above
    frustum.setProjection(getProjection());

    // Set the viewFrustum up with the correct position and orientation of the camera
    frustum.setPosition(getPosition());
    frustum.setOrientation(getRotation());

    // Ask the ViewFrustum class to calculate our corners
    frustum.calculate();
}

ViewFrustum Camera::toViewFrustum() const {
    ViewFrustum result;
    loadViewFrustum(result);
    return result;
}
