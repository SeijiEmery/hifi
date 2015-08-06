//
//  Camera.h
//  tests/modelviewer/src/
//
//  Created by Seiji Emery on 8/4/15
//  Copyright (c) 2014 High Fidelity, Inc. All rights reserved.
//

#ifndef HIFI_MODELVIEWER_CAMERA_H
#define HIFI_MODELVIEWER_CAMERA_H

#include "Transform.h"
#include <glm/glm.hpp>
#include <memory>
#include <vector>
#include <map>

/// POD defining camera state. Double buffered, so multiple controllers can write to it at once.
struct CameraState {
    Transform cameraTransform;

    CameraState (const CameraState & cameraState) :
            cameraTransform(cameraState.cameraTransform) {}
};

// Camera controller interface. Should encapsulate input from one peripheral (keyboard/gamepad/etc), and perform all
// camera updates for that peripheral.
// Note that due to c++ multiple inheritance, once class can implement both camera and ui controls (so these can/should
// become integrated under the hood). (ie. class GamepadController : public ICameraController, IGuiController { ... })
class ICameraController {
public:
    virtual ~ICameraController () = 0;

    /// Applies updates to the camera state iff input has been recieved (ie. controller buttons have been pressed, etc).
    /// This enables us to trivially implement multiple active controllers (ie. you could have a vive, gamepad, and kb/m
    /// all plugged in and available responsible for game input. Move the analog sticks on the gamepad and that
    /// moves the camera; move the mouse or press a keyboard button and that applies updates, etc).
    /// This becomes more complicated with ui, but that's another subject.
    virtual bool maybeUpdateCameraState(const CameraState & currentState, CameraState & nextState, float dt) = 0;

    /// Called when this class a) gets focus (exclusive focus?), or b) loses focus to something else
    virtual void notifyChangedFocus (bool hasFocus) = 0;
    virtual void onCameraRegistered () = 0;
    virtual void onCameraUnregistered () = 0;
};
typedef std::shared_ptr<ICameraController> CameraControllerPtr;


/// Contains camera state, a list of registered controllers, and methods for interfacing with the renderer and
/// the external application.
/// Methods for moving the camera are NOT provided -- use a ICameraController impl instead.
class Camera {
public:
    Camera () {}
    Camera (const Camera & other);
    Camera (Camera && other);

    //
    // Interface methods
    //

    /// Registers an ICameraController using a QString id/handle.
    void registerController(QString id, const ICameraControllerPtr & controller);
    void unregisterController(QString id);

    //
    // Renderer methods
    //

    void update (float dt);

    void setProjectionMatrix (const glm::mat4 & matrix);
    const glm::mat4& getProjectionMatrix ();
    glm::mat4 getViewMatrix ();
    ViewFrustrum getFrustrum(); // redundant...?

    // (tbd)
protected:
    /// Non-owning references to ICameraControllers
    std::vector<ICameraControllerPtr> _controllerList;

    /// Lookup structure for the controller list. Modified whenever an item is added or deleted.
    /// Note: this requires a lot of maintenance to keep in sync with _controllerList, though registerController and
    /// unregisterController are the only methods that need to do so atm.
    std::map<QString, int> _controllerMap;

    /// Double buffered camera state
    CameraState _cameraStates[2];
    int _activeState = 0;               // toggle 1 / 0

    glm::mat4 _projectionMatrix;
    int _lastFocusedController = -1;
};

#endif //HIFI_MODELVIEWER_CAMERA_H