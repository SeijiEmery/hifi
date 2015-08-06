//
//  Camera.cpp
//  tests/modelviewer/src/
//
//  Created by Seiji Emery on 8/4/15
//  Copyright (c) 2014 High Fidelity, Inc. All rights reserved.
//

#include "Camera.h"
#include <cassert>

// Singlethreaded version. Maybe create lightweight threaded/pooled too?
void Camera::update (float dt) {
    int s0 = _activeState, s1 = (_activeState+1) & 0x1;

    // First controller that applies updates
    int activeController = -1;

    bool hasExclusiveAccess = true;
    for (int i = 0; i < _controllerList.size(); ++i) {
        if (_controllerList[i]->maybeUpdateCameraState(_cameraStates[s0], _cameraStates[s1], dt)) {
            if (activeController >= 0)
                hasExclusiveAccess = false;
            else
                activeController = i;
        }
    }

    if (activeController != _lastFocusedController) {
        if (_lastFocusedController >= 0)
            _controllerList[_lastFocusedController]->notifyChangedFocus(false);
        if (activeController >= 0 && hasExclusiveAccess)
            _controllerList[activeController]->notifyChangedFocus(true);
    }
    _lastFocusedController = activeController;
    _activeState = (_activeState + 1) & 0x1;
}

void Camera::registerController(QString id, const ICameraController & controller) {
    if (_controllerMap.find(id) != _controllerMap.end()) {
        qDebug() << "Camera already has controller registered with id \"" << id << "\".";
    } else {
        _controllerMap[id] = _controllerList.size();
        _controllerList.push_back(controller);
        controller.onCameraRegistered();
    }
    assert(_controllerList.size() == _controllerMap.size());
}

template <typename K, typename V>
static bool findKeyMatchingValue (const std::map<K, V> &m, const V & value, K &key) {
    for (auto kv : m) {
        if (kv.second == value) {
            key = kv.first;
            return true;
        }
    }
    return false;
}

// This needs testing
void Camera::unregisterController(QString id) {
    if (_controllerMap.find(id) == _controllerMap.end()) {
        qDebug() << "No Camera controller with id \"" << id << "\" to unregister.";
    } else {
        auto idx = _controllerMap.find()->second;
        if (_lastFocusedController == idx) {
            _controllerList[idx]->notifyCameraChangedFocus(false);
            _lastFocusedController = -1;
        }
        _controllerList[idx]->onCameraUnregistered();
        if (_controllerList.size() > 1) {
            auto end = _controllerList.size() - 1;
            QString key;
            assert(findKeyMatchingValue(_controllerMap, end, key));

            // Swap-delete current value, replacing it with one from the end of the list
            _controllerMap[key] = idx;
            _controllerList[idx] = std::move(_controllerList[end]);

            if (_lastFocusedController == end)
                _lastFocusedController = idx;
        }
        _controllerList.pop_back();
    }
    assert(_controllerList.size() == _controllerMap.size());
}










