(function(){
/** 
 * @namespace 
 * @property {{x: number, y: number, z: number}} position
 * @property {{x: number, y: number, z: number, w: number}} orientation
 * @property {string} mode 
*/
this.Camera = {};
/** 
 * @slot
 * @function getModeString
 * @memberof Camera
 * @returns {string} 
*/
this.Camera.getModeString = function(){};
/** 
 * @slot
 * @function setModeString
 * @memberof Camera
 * @param {string} mode 
*/
this.Camera.setModeString = function(mode){};
/** 
 * @slot
 * @function getPosition
 * @memberof Camera
 * @returns {{x: number, y: number, z: number}} 
*/
this.Camera.getPosition = function(){};
/** 
 * @slot
 * @function setPosition
 * @memberof Camera
 * @param {{x: number, y: number, z: number}} position 
*/
this.Camera.setPosition = function(position){};
/** 
 * @slot
 * @function getOrientation
 * @memberof Camera
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Camera.getOrientation = function(){};
/** 
 * @slot
 * @function setOrientation
 * @memberof Camera
 * @param {{x: number, y: number, z: number, w: number}} orientation 
*/
this.Camera.setOrientation = function(orientation){};
/** 
 * @slot
 * @function computePickRay
 * @memberof Camera
 * @param {number} x
 * @param {number} y
 * @returns {PickRay} 
*/
this.Camera.computePickRay = function(x, y){};
/** 
 * one time change to what the camera is looking at
 * 
 * @slot
 * @function lookAt
 * @memberof Camera
 * @param {{x: number, y: number, z: number}} value 
*/
this.Camera.lookAt = function(value){};
/** 
 * fix what the camera is looking at, and keep the camera looking at this even if position changes
 * 
 * @slot
 * @function keepLookingAt
 * @memberof Camera
 * @param {{x: number, y: number, z: number}} value 
*/
this.Camera.keepLookingAt = function(value){};
/** 
 * stops the keep looking at feature, doesn't change what's being looked at, but will stop camera from
 * continuing to update it's orientation to keep looking at the item
 * 
 * @slot
 * @function stopLooking
 * @memberof Camera 
*/
this.Camera.stopLooking = function(){};
/** 
 * @signal
 * @function modeUpdated
 * @memberof Camera
 * @param {string} newMode 
*/
this.Camera.modeUpdated = function(newMode){};/** 
 * @namespace 
 * @property {bool} shouldRenderLocally
 * @property {{x: number, y: number, z: number}} motorVelocity
 * @property {number} motorTimescale
 * @property {string} motorReferenceFrame
 * @property {string} collisionSoundURL 
*/
this.MyAvatar = {};
/** 
 * @function getDefaultEyePosition
 * @memberof MyAvatar
 * @returns {{x: number, y: number, z: number}} 
*/
this.MyAvatar.getDefaultEyePosition = function(){};
/** 
 * Allows scripts to run animations.
 * 
 * @function startAnimation
 * @memberof MyAvatar
 * @param {string} url
 * @param {number} fps
 * @param {number} priority
 * @param {bool} loop
 * @param {bool} hold
 * @param {number} firstFrame
 * @param {number} lastFrame
 * @param {string[]} maskedJoints 
*/
this.MyAvatar.startAnimation = function(url, fps, priority, loop, hold, firstFrame, lastFrame, maskedJoints){};
/** 
 * Stops an animation as identified by a URL.
 * 
 * @function stopAnimation
 * @memberof MyAvatar
 * @param {string} url 
*/
this.MyAvatar.stopAnimation = function(url){};
/** 
 * Starts an animation by its role, using the provided URL and parameters if the avatar doesn't have a
 * custom animation for the role.
 * 
 * @function startAnimationByRole
 * @memberof MyAvatar
 * @param {string} role
 * @param {string} url
 * @param {number} fps
 * @param {number} priority
 * @param {bool} loop
 * @param {bool} hold
 * @param {number} firstFrame
 * @param {number} lastFrame
 * @param {string[]} maskedJoints 
*/
this.MyAvatar.startAnimationByRole = function(role, url, fps, priority, loop, hold, firstFrame, lastFrame, maskedJoints){};
/** 
 * Stops an animation identified by its role.
 * 
 * @function stopAnimationByRole
 * @memberof MyAvatar
 * @param {string} role 
*/
this.MyAvatar.stopAnimationByRole = function(role){};
/** 
 * @function getAnimationDetailsByRole
 * @memberof MyAvatar
 * @param {string} role
 * @returns {AnimationDetails} 
*/
this.MyAvatar.getAnimationDetailsByRole = function(role){};
/** 
 * @function getAnimationDetails
 * @memberof MyAvatar
 * @param {string} url
 * @returns {AnimationDetails} 
*/
this.MyAvatar.getAnimationDetails = function(url){};
/** 
 * @function getTrackedHeadPosition
 * @memberof MyAvatar
 * @returns {{x: number, y: number, z: number}} 
*/
this.MyAvatar.getTrackedHeadPosition = function(){};
/** 
 * @function getHeadPosition
 * @memberof MyAvatar
 * @returns {{x: number, y: number, z: number}} 
*/
this.MyAvatar.getHeadPosition = function(){};
/** 
 * @function getHeadFinalYaw
 * @memberof MyAvatar
 * @returns {number} 
*/
this.MyAvatar.getHeadFinalYaw = function(){};
/** 
 * @function getHeadFinalRoll
 * @memberof MyAvatar
 * @returns {number} 
*/
this.MyAvatar.getHeadFinalRoll = function(){};
/** 
 * @function getHeadFinalPitch
 * @memberof MyAvatar
 * @returns {number} 
*/
this.MyAvatar.getHeadFinalPitch = function(){};
/** 
 * @function getHeadDeltaPitch
 * @memberof MyAvatar
 * @returns {number} 
*/
this.MyAvatar.getHeadDeltaPitch = function(){};
/** 
 * @function getEyePosition
 * @memberof MyAvatar
 * @returns {{x: number, y: number, z: number}} 
*/
this.MyAvatar.getEyePosition = function(){};
/** 
 * @function getTargetAvatarPosition
 * @memberof MyAvatar
 * @returns {{x: number, y: number, z: number}} 
*/
this.MyAvatar.getTargetAvatarPosition = function(){};
/** 
 * @function useFullAvatarURL
 * @memberof MyAvatar
 * @param {QUrl} fullAvatarURL
 * @param {string} modelName 
*/
this.MyAvatar.useFullAvatarURL = function(fullAvatarURL, modelName){};
/** 
 * @function useHeadURL
 * @memberof MyAvatar
 * @param {QUrl} headURL
 * @param {string} modelName 
*/
this.MyAvatar.useHeadURL = function(headURL, modelName){};
/** 
 * @function useBodyURL
 * @memberof MyAvatar
 * @param {QUrl} bodyURL
 * @param {string} modelName 
*/
this.MyAvatar.useBodyURL = function(bodyURL, modelName){};
/** 
 * @function useHeadAndBodyURLs
 * @memberof MyAvatar
 * @param {QUrl} headURL
 * @param {QUrl} bodyURL
 * @param {string} headName
 * @param {string} bodyName 
*/
this.MyAvatar.useHeadAndBodyURLs = function(headURL, bodyURL, headName, bodyName){};
/** 
 * @function getUseFullAvatar
 * @memberof MyAvatar
 * @returns {bool} 
*/
this.MyAvatar.getUseFullAvatar = function(){};
/** 
 * @function getFullAvatarURLFromPreferences
 * @memberof MyAvatar
 * @returns {QUrl} 
*/
this.MyAvatar.getFullAvatarURLFromPreferences = function(){};
/** 
 * @function getHeadURLFromPreferences
 * @memberof MyAvatar
 * @returns {QUrl} 
*/
this.MyAvatar.getHeadURLFromPreferences = function(){};
/** 
 * @function getBodyURLFromPreferences
 * @memberof MyAvatar
 * @returns {QUrl} 
*/
this.MyAvatar.getBodyURLFromPreferences = function(){};
/** 
 * @function getHeadModelName
 * @memberof MyAvatar
 * @returns {string} 
*/
this.MyAvatar.getHeadModelName = function(){};
/** 
 * @function getBodyModelName
 * @memberof MyAvatar
 * @returns {string} 
*/
this.MyAvatar.getBodyModelName = function(){};
/** 
 * @function getFullAvartarModelName
 * @memberof MyAvatar
 * @returns {string} 
*/
this.MyAvatar.getFullAvartarModelName = function(){};
/** 
 * @function getModelDescription
 * @memberof MyAvatar
 * @returns {string} 
*/
this.MyAvatar.getModelDescription = function(){};
/** 
 * @slot
 * @function increaseSize
 * @memberof MyAvatar 
*/
this.MyAvatar.increaseSize = function(){};
/** 
 * @slot
 * @function decreaseSize
 * @memberof MyAvatar 
*/
this.MyAvatar.decreaseSize = function(){};
/** 
 * @slot
 * @function resetSize
 * @memberof MyAvatar 
*/
this.MyAvatar.resetSize = function(){};
/** 
 * @slot
 * @function goToLocation
 * @memberof MyAvatar
 * @param {{x: number, y: number, z: number}} newPosition
 * @param {bool} hasOrientation
 * @param {{x: number, y: number, z: number, w: number}} newOrientation
 * @param {bool} shouldFaceLocation 
*/
this.MyAvatar.goToLocation = function(newPosition, hasOrientation, newOrientation, shouldFaceLocation){};
/** 
 * @slot
 * @function addThrust
 * @memberof MyAvatar
 * @param {{x: number, y: number, z: number}} newThrust 
*/
this.MyAvatar.addThrust = function(newThrust){};
/** 
 * @signal
 * @function transformChanged
 * @memberof MyAvatar 
*/
this.MyAvatar.transformChanged = function(){};
/** 
 * @signal
 * @function newCollisionSoundURL
 * @memberof MyAvatar
 * @param {QUrl} url 
*/
this.MyAvatar.newCollisionSoundURL = function(url){};
/** 
 * @signal
 * @function collisionWithEntity
 * @memberof MyAvatar
 * @param {Collision} collision 
*/
this.MyAvatar.collisionWithEntity = function(collision){};/** 
 * @namespace  
*/
this.AnimationCache = {};
/** 
 * @function getAnimation
 * @memberof AnimationCache
 * @param {string} url
 * @returns {AnimationPointer} 
*/
this.AnimationCache.getAnimation = function(url){};
/** 
 * @function getAnimation
 * @memberof AnimationCache
 * @param {QUrl} url
 * @returns {AnimationPointer} 
*/
this.AnimationCache.getAnimation = function(url){};/** 
 * @namespace  
*/
this.Settings = {};
/** 
 * @slot
 * @function getValue
 * @memberof Settings
 * @param {string} setting
 * @returns {object} 
*/
this.Settings.getValue = function(setting){};
/** 
 * @slot
 * @function getValue
 * @memberof Settings
 * @param {string} setting
 * @param {object} defaultValue
 * @returns {object} 
*/
this.Settings.getValue = function(setting, defaultValue){};
/** 
 * @slot
 * @function setValue
 * @memberof Settings
 * @param {string} setting
 * @param {object} value 
*/
this.Settings.setValue = function(setting, value){};/** 
 * @namespace  
*/
this.Overlays = {};
/** 
 * adds an overlay with the specific properties
 * 
 * @slot
 * @function addOverlay
 * @memberof Overlays
 * @param {string} type
 * @param {object} properties
 * @returns {number} 
*/
this.Overlays.addOverlay = function(type, properties){};
/** 
 * adds an overlay that's already been created
 * 
 * @slot
 * @function addOverlay
 * @memberof Overlays
 * @param {Overlay} overlay
 * @returns {number} 
*/
this.Overlays.addOverlay = function(overlay){};
/** 
 * clones an existing overlay
 * 
 * @slot
 * @function cloneOverlay
 * @memberof Overlays
 * @param {number} id
 * @returns {number} 
*/
this.Overlays.cloneOverlay = function(id){};
/** 
 * edits an overlay updating only the included properties, will return the identified OverlayID in case
 * of successful edit, if the input id is for an unknown overlay this function will have no effect
 * 
 * @slot
 * @function editOverlay
 * @memberof Overlays
 * @param {number} id
 * @param {object} properties
 * @returns {bool} 
*/
this.Overlays.editOverlay = function(id, properties){};
/** 
 * deletes a particle
 * 
 * @slot
 * @function deleteOverlay
 * @memberof Overlays
 * @param {number} id 
*/
this.Overlays.deleteOverlay = function(id){};
/** 
 * returns the top most 2D overlay at the screen point, or 0 if not overlay at that point
 * 
 * @slot
 * @function getOverlayAtPoint
 * @memberof Overlays
 * @param {{x: number, y: number, z: number}} point
 * @returns {number} 
*/
this.Overlays.getOverlayAtPoint = function(point){};
/** 
 * returns the value of specified property, or null if there is no such property
 * 
 * @slot
 * @function getProperty
 * @memberof Overlays
 * @param {number} id
 * @param {string} property
 * @returns {OverlayPropertyResult} 
*/
this.Overlays.getProperty = function(id, property){};
/** 
 * returns details about the closest 3D <ref refid="class_overlay" kindref="compound" >Overlay</ref>
 * 
 * @slot
 * @function findRayIntersection
 * @memberof Overlays
 * @param {PickRay} ray
 * @returns {RayToOverlayIntersectionResult} 
*/
this.Overlays.findRayIntersection = function(ray){};
/** 
 * returns whether the overlay's assets are loaded or not
 * 
 * @slot
 * @function isLoaded
 * @memberof Overlays
 * @param {number} id
 * @returns {bool} 
*/
this.Overlays.isLoaded = function(id){};
/** 
 * returns the size of the given text in the specified overlay if it is a text overlay: in pixels if it
 * is a 2D text overlay; in meters if it is a 3D text overlay
 * 
 * @slot
 * @function textSize
 * @memberof Overlays
 * @param {number} id
 * @param {string} text
 * @returns {QSizeF} 
*/
this.Overlays.textSize = function(id, text){};/** 
 * @namespace  
*/
this.AudioDevice = {};
/** 
 * @slot
 * @function setInputDevice
 * @memberof AudioDevice
 * @param {string} deviceName
 * @returns {bool} 
*/
this.AudioDevice.setInputDevice = function(deviceName){};
/** 
 * @slot
 * @function setOutputDevice
 * @memberof AudioDevice
 * @param {string} deviceName
 * @returns {bool} 
*/
this.AudioDevice.setOutputDevice = function(deviceName){};
/** 
 * @slot
 * @function getInputDevice
 * @memberof AudioDevice
 * @returns {string} 
*/
this.AudioDevice.getInputDevice = function(){};
/** 
 * @slot
 * @function getOutputDevice
 * @memberof AudioDevice
 * @returns {string} 
*/
this.AudioDevice.getOutputDevice = function(){};
/** 
 * @slot
 * @function getDefaultInputDevice
 * @memberof AudioDevice
 * @returns {string} 
*/
this.AudioDevice.getDefaultInputDevice = function(){};
/** 
 * @slot
 * @function getDefaultOutputDevice
 * @memberof AudioDevice
 * @returns {string} 
*/
this.AudioDevice.getDefaultOutputDevice = function(){};
/** 
 * @slot
 * @function getInputDevices
 * @memberof AudioDevice
 * @returns {string[]} 
*/
this.AudioDevice.getInputDevices = function(){};
/** 
 * @slot
 * @function getOutputDevices
 * @memberof AudioDevice
 * @returns {string[]} 
*/
this.AudioDevice.getOutputDevices = function(){};
/** 
 * @slot
 * @function getInputVolume
 * @memberof AudioDevice
 * @returns {number} 
*/
this.AudioDevice.getInputVolume = function(){};
/** 
 * @slot
 * @function setInputVolume
 * @memberof AudioDevice
 * @param {number} volume 
*/
this.AudioDevice.setInputVolume = function(volume){};
/** 
 * @slot
 * @function setReverb
 * @memberof AudioDevice
 * @param {bool} reverb 
*/
this.AudioDevice.setReverb = function(reverb){};
/** 
 * @slot
 * @function setReverbOptions
 * @memberof AudioDevice
 * @param {AudioEffectOptions} options 
*/
this.AudioDevice.setReverbOptions = function(options){};
/** 
 * @slot
 * @function getMuted
 * @memberof AudioDevice
 * @returns {bool} 
*/
this.AudioDevice.getMuted = function(){};
/** 
 * @slot
 * @function toggleMute
 * @memberof AudioDevice 
*/
this.AudioDevice.toggleMute = function(){};
/** 
 * @signal
 * @function muteToggled
 * @memberof AudioDevice 
*/
this.AudioDevice.muteToggled = function(){};
/** 
 * @signal
 * @function deviceChanged
 * @memberof AudioDevice 
*/
this.AudioDevice.deviceChanged = function(){};/** 
 * @namespace  
*/
this.Audio = {};
/** 
 * @function playSound
 * @memberof Audio
 * @param {Sound} sound
 * @param {AudioInjectorOptions} injectorOptions
 * @returns {ScriptAudioInjector} 
*/
this.Audio.playSound = function(sound, injectorOptions){};
/** 
 * @function injectGeneratedNoise
 * @memberof Audio
 * @param {bool} inject 
*/
this.Audio.injectGeneratedNoise = function(inject){};
/** 
 * @function selectPinkNoise
 * @memberof Audio 
*/
this.Audio.selectPinkNoise = function(){};
/** 
 * @function selectSine440
 * @memberof Audio 
*/
this.Audio.selectSine440 = function(){};
/** 
 * @function setStereoInput
 * @memberof Audio
 * @param {bool} stereo 
*/
this.Audio.setStereoInput = function(stereo){};
/** 
 * @signal
 * @function mutedByMixer
 * @memberof Audio 
*/
this.Audio.mutedByMixer = function(){};
/** 
 * @signal
 * @function environmentMuted
 * @memberof Audio 
*/
this.Audio.environmentMuted = function(){};
/** 
 * @signal
 * @function receivedFirstPacket
 * @memberof Audio 
*/
this.Audio.receivedFirstPacket = function(){};
/** 
 * @signal
 * @function disconnected
 * @memberof Audio 
*/
this.Audio.disconnected = function(){};/** 
 * @namespace  
*/
this.Account = {};
/** 
 * @signal
 * @function balanceChanged
 * @memberof Account
 * @param {number} newBalance 
*/
this.Account.balanceChanged = function(newBalance){};
/** 
 * @slot
 * @function getInstance
 * @memberof Account
 * @returns {AccountScriptingInterface} 
*/
this.Account.getInstance = function(){};
/** 
 * @slot
 * @function getBalance
 * @memberof Account
 * @returns {number} 
*/
this.Account.getBalance = function(){};
/** 
 * @slot
 * @function isLoggedIn
 * @memberof Account
 * @returns {bool} 
*/
this.Account.isLoggedIn = function(){};
/** 
 * @slot
 * @function updateBalance
 * @memberof Account 
*/
this.Account.updateBalance = function(){};/** 
 * @namespace  
*/
this.Quat = {};
/** 
 * @slot
 * @function multiply
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q1
 * @param {{x: number, y: number, z: number, w: number}} q2
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.multiply = function(q1, q2){};
/** 
 * @slot
 * @function fromVec3Degrees
 * @memberof Quat
 * @param {{x: number, y: number, z: number}} vec3
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.fromVec3Degrees = function(vec3){};
/** 
 * @slot
 * @function fromVec3Radians
 * @memberof Quat
 * @param {{x: number, y: number, z: number}} vec3
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.fromVec3Radians = function(vec3){};
/** 
 * @slot
 * @function fromPitchYawRollDegrees
 * @memberof Quat
 * @param {number} pitch
 * @param {number} yaw
 * @param {number} roll
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.fromPitchYawRollDegrees = function(pitch, yaw, roll){};
/** 
 * @slot
 * @function fromPitchYawRollRadians
 * @memberof Quat
 * @param {number} pitch
 * @param {number} yaw
 * @param {number} roll
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.fromPitchYawRollRadians = function(pitch, yaw, roll){};
/** 
 * @slot
 * @function inverse
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.inverse = function(q){};
/** 
 * @slot
 * @function getFront
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {{x: number, y: number, z: number}} 
*/
this.Quat.getFront = function(orientation){};
/** 
 * @slot
 * @function getRight
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {{x: number, y: number, z: number}} 
*/
this.Quat.getRight = function(orientation){};
/** 
 * @slot
 * @function getUp
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {{x: number, y: number, z: number}} 
*/
this.Quat.getUp = function(orientation){};
/** 
 * @slot
 * @function safeEulerAngles
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {{x: number, y: number, z: number}} 
*/
this.Quat.safeEulerAngles = function(orientation){};
/** 
 * @slot
 * @function angleAxis
 * @memberof Quat
 * @param {number} angle
 * @param {{x: number, y: number, z: number}} v
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.angleAxis = function(angle, v){};
/** 
 * @slot
 * @function axis
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {{x: number, y: number, z: number}} 
*/
this.Quat.axis = function(orientation){};
/** 
 * @slot
 * @function angle
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} orientation
 * @returns {number} 
*/
this.Quat.angle = function(orientation){};
/** 
 * @slot
 * @function mix
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q1
 * @param {{x: number, y: number, z: number, w: number}} q2
 * @param {number} alpha
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.mix = function(q1, q2, alpha){};
/** 
 * Spherical Linear Interpolation.
 * 
 * @slot
 * @function slerp
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q1
 * @param {{x: number, y: number, z: number, w: number}} q2
 * @param {number} alpha
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.slerp = function(q1, q2, alpha){};
/** 
 * @slot
 * @function squad
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q1
 * @param {{x: number, y: number, z: number, w: number}} q2
 * @param {{x: number, y: number, z: number, w: number}} s1
 * @param {{x: number, y: number, z: number, w: number}} s2
 * @param {number} h
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Quat.squad = function(q1, q2, s1, s2, h){};
/** 
 * @slot
 * @function dot
 * @memberof Quat
 * @param {{x: number, y: number, z: number, w: number}} q1
 * @param {{x: number, y: number, z: number, w: number}} q2
 * @returns {number} 
*/
this.Quat.dot = function(q1, q2){};
/** 
 * @slot
 * @function print
 * @memberof Quat
 * @param {string} lable
 * @param {{x: number, y: number, z: number, w: number}} q 
*/
this.Quat.print = function(lable, q){};
/** 
 * @slot
 * @function equal
 * @memberof Quat
 * @param {{x: number, y: number, z: number}} q1
 * @param {{x: number, y: number, z: number}} q2
 * @returns {bool} 
*/
this.Quat.equal = function(q1, q2){};/** 
 * @namespace  
*/
this.AbstractInputController = {};
/** 
 * @slot
 * @function isActive
 * @memberof AbstractInputController
 * @returns {bool} 
*/
this.AbstractInputController.isActive = function(){};
/** 
 * @slot
 * @function getAbsTranslation
 * @memberof AbstractInputController
 * @returns {{x: number, y: number, z: number}} 
*/
this.AbstractInputController.getAbsTranslation = function(){};
/** 
 * @slot
 * @function getAbsRotation
 * @memberof AbstractInputController
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.AbstractInputController.getAbsRotation = function(){};
/** 
 * @slot
 * @function getLocTranslation
 * @memberof AbstractInputController
 * @returns {{x: number, y: number, z: number}} 
*/
this.AbstractInputController.getLocTranslation = function(){};
/** 
 * @slot
 * @function getLocRotation
 * @memberof AbstractInputController
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.AbstractInputController.getLocRotation = function(){};
/** 
 * @signal
 * @function spatialEvent
 * @memberof AbstractInputController
 * @param {SpatialEvent} event 
*/
this.AbstractInputController.spatialEvent = function(event){};/** 
 * @namespace  
*/
this.Script = {};
/** 
 * @function setIsAvatar
 * @memberof Script
 * @param {bool} isAvatar 
*/
this.Script.setIsAvatar = function(isAvatar){};
/** 
 * @function addEventHandler
 * @memberof Script
 * @param {EntityItemID} entityID
 * @param {string} eventName
 * @param {object} handler 
*/
this.Script.addEventHandler = function(entityID, eventName, handler){};
/** 
 * @function removeEventHandler
 * @memberof Script
 * @param {EntityItemID} entityID
 * @param {string} eventName
 * @param {object} handler 
*/
this.Script.removeEventHandler = function(entityID, eventName, handler){};
/** 
 * @slot
 * @function loadURL
 * @memberof Script
 * @param {QUrl} scriptURL
 * @param {bool} reload 
*/
this.Script.loadURL = function(scriptURL, reload){};
/** 
 * @slot
 * @function stop
 * @memberof Script 
*/
this.Script.stop = function(){};
/** 
 * @slot
 * @function evaluate
 * @memberof Script
 * @param {string} program
 * @param {string} fileName
 * @param {number} lineNumber
 * @returns {object} 
*/
this.Script.evaluate = function(program, fileName, lineNumber){};
/** 
 * @slot
 * @function setInterval
 * @memberof Script
 * @param {object} func
 * @param {number} intervalMS
 * @returns {object} 
*/
this.Script.setInterval = function(_function, intervalMS){};
/** 
 * @slot
 * @function setTimeout
 * @memberof Script
 * @param {object} func
 * @param {number} timeoutMS
 * @returns {object} 
*/
this.Script.setTimeout = function(_function, timeoutMS){};
/** 
 * @slot
 * @function clearInterval
 * @memberof Script
 * @param {object} timer 
*/
this.Script.clearInterval = function(timer){};
/** 
 * @slot
 * @function clearTimeout
 * @memberof Script
 * @param {object} timer 
*/
this.Script.clearTimeout = function(timer){};
/** 
 * @slot
 * @function include
 * @memberof Script
 * @param {string[]} includeFiles
 * @param {object} callback 
*/
this.Script.include = function(includeFiles, callback){};
/** 
 * @slot
 * @function include
 * @memberof Script
 * @param {string} includeFile
 * @param {object} callback 
*/
this.Script.include = function(includeFile, callback){};
/** 
 * @slot
 * @function load
 * @memberof Script
 * @param {string} loadfile 
*/
this.Script.load = function(loadfile){};
/** 
 * @slot
 * @function print
 * @memberof Script
 * @param {string} message 
*/
this.Script.print = function(message){};
/** 
 * @slot
 * @function resolvePath
 * @memberof Script
 * @param {string} path
 * @returns {QUrl} 
*/
this.Script.resolvePath = function(path){};
/** 
 * @slot
 * @function nodeKilled
 * @memberof Script
 * @param {SharedNodePointer} node 
*/
this.Script.nodeKilled = function(node){};
/** 
 * @signal
 * @function scriptLoaded
 * @memberof Script
 * @param {string} scriptFilename 
*/
this.Script.scriptLoaded = function(scriptFilename){};
/** 
 * @signal
 * @function errorLoadingScript
 * @memberof Script
 * @param {string} scriptFilename 
*/
this.Script.errorLoadingScript = function(scriptFilename){};
/** 
 * @signal
 * @function update
 * @memberof Script
 * @param {number} deltaTime 
*/
this.Script.update = function(deltaTime){};
/** 
 * @signal
 * @function scriptEnding
 * @memberof Script 
*/
this.Script.scriptEnding = function(){};
/** 
 * @signal
 * @function finished
 * @memberof Script
 * @param {string} fileNameString 
*/
this.Script.finished = function(fileNameString){};
/** 
 * @signal
 * @function cleanupMenuItem
 * @memberof Script
 * @param {string} menuItemString 
*/
this.Script.cleanupMenuItem = function(menuItemString){};
/** 
 * @signal
 * @function printedMessage
 * @memberof Script
 * @param {string} message 
*/
this.Script.printedMessage = function(message){};
/** 
 * @signal
 * @function errorMessage
 * @memberof Script
 * @param {string} message 
*/
this.Script.errorMessage = function(message){};
/** 
 * @signal
 * @function runningStateChanged
 * @memberof Script 
*/
this.Script.runningStateChanged = function(){};
/** 
 * @signal
 * @function evaluationFinished
 * @memberof Script
 * @param {object} result
 * @param {bool} isException 
*/
this.Script.evaluationFinished = function(result, isException){};
/** 
 * @signal
 * @function loadScript
 * @memberof Script
 * @param {string} scriptName
 * @param {bool} isUserLoaded 
*/
this.Script.loadScript = function(scriptName, isUserLoaded){};
/** 
 * @signal
 * @function reloadScript
 * @memberof Script
 * @param {string} scriptName
 * @param {bool} isUserLoaded 
*/
this.Script.reloadScript = function(scriptName, isUserLoaded){};
/** 
 * @signal
 * @function doneRunning
 * @memberof Script 
*/
this.Script.doneRunning = function(){};/** 
 * @namespace  
*/
this.LODManager = {};
/** 
 * @function setAutomaticLODAdjust
 * @memberof LODManager
 * @param {bool} value 
*/
this.LODManager.setAutomaticLODAdjust = function(value){};
/** 
 * @function getAutomaticLODAdjust
 * @memberof LODManager
 * @returns {bool} 
*/
this.LODManager.getAutomaticLODAdjust = function(){};
/** 
 * @function setDesktopLODDecreaseFPS
 * @memberof LODManager
 * @param {number} value 
*/
this.LODManager.setDesktopLODDecreaseFPS = function(value){};
/** 
 * @function getDesktopLODDecreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getDesktopLODDecreaseFPS = function(){};
/** 
 * @function getDesktopLODIncreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getDesktopLODIncreaseFPS = function(){};
/** 
 * @function setHMDLODDecreaseFPS
 * @memberof LODManager
 * @param {number} value 
*/
this.LODManager.setHMDLODDecreaseFPS = function(value){};
/** 
 * @function getHMDLODDecreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getHMDLODDecreaseFPS = function(){};
/** 
 * @function getHMDLODIncreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getHMDLODIncreaseFPS = function(){};
/** 
 * @function getAvatarLODDistanceMultiplier
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getAvatarLODDistanceMultiplier = function(){};
/** 
 * @function getLODFeedbackText
 * @memberof LODManager
 * @returns {string} 
*/
this.LODManager.getLODFeedbackText = function(){};
/** 
 * @function setOctreeSizeScale
 * @memberof LODManager
 * @param {number} sizeScale 
*/
this.LODManager.setOctreeSizeScale = function(sizeScale){};
/** 
 * @function getOctreeSizeScale
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getOctreeSizeScale = function(){};
/** 
 * @function setBoundaryLevelAdjust
 * @memberof LODManager
 * @param {number} boundaryLevelAdjust 
*/
this.LODManager.setBoundaryLevelAdjust = function(boundaryLevelAdjust){};
/** 
 * @function getBoundaryLevelAdjust
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getBoundaryLevelAdjust = function(){};
/** 
 * @function getLODDecreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getLODDecreaseFPS = function(){};
/** 
 * @function getLODIncreaseFPS
 * @memberof LODManager
 * @returns {number} 
*/
this.LODManager.getLODIncreaseFPS = function(){};
/** 
 * @signal
 * @function LODIncreased
 * @memberof LODManager 
*/
this.LODManager.LODIncreased = function(){};
/** 
 * @signal
 * @function LODDecreased
 * @memberof LODManager 
*/
this.LODManager.LODDecreased = function(){};/** 
 * @namespace  
*/
this.UndoStack = {};
/** 
 * @slot
 * @function pushCommand
 * @memberof UndoStack
 * @param {object} undoFunction
 * @param {object} undoData
 * @param {object} redoFunction
 * @param {object} redoData 
*/
this.UndoStack.pushCommand = function(undoFunction, undoData, redoFunction, redoData){};/** 
 * @namespace  
*/
this.SpeechRecognizer = {};
/** 
 * @slot
 * @function setEnabled
 * @memberof SpeechRecognizer
 * @param {bool} enabled 
*/
this.SpeechRecognizer.setEnabled = function(enabled){};
/** 
 * @slot
 * @function addCommand
 * @memberof SpeechRecognizer
 * @param {string} command 
*/
this.SpeechRecognizer.addCommand = function(command){};
/** 
 * @slot
 * @function removeCommand
 * @memberof SpeechRecognizer
 * @param {string} command 
*/
this.SpeechRecognizer.removeCommand = function(command){};
/** 
 * @signal
 * @function commandRecognized
 * @memberof SpeechRecognizer
 * @param {string} command 
*/
this.SpeechRecognizer.commandRecognized = function(command){};
/** 
 * @signal
 * @function enabledUpdated
 * @memberof SpeechRecognizer
 * @param {bool} enabled 
*/
this.SpeechRecognizer.enabledUpdated = function(enabled){};/** 
 * @namespace 
 * @property {string} username
 * @property {string} findableBy 
*/
this.GlobalServices = {};
/** 
 * @slot
 * @function getDownloadInfo
 * @memberof GlobalServices
 * @returns {DownloadInfoResult} 
*/
this.GlobalServices.getDownloadInfo = function(){};
/** 
 * @slot
 * @function updateDownloadInfo
 * @memberof GlobalServices 
*/
this.GlobalServices.updateDownloadInfo = function(){};
/** 
 * @slot
 * @function editFriends
 * @memberof GlobalServices 
*/
this.GlobalServices.editFriends = function(){};
/** 
 * @signal
 * @function connected
 * @memberof GlobalServices 
*/
this.GlobalServices.connected = function(){};
/** 
 * @signal
 * @function disconnected
 * @memberof GlobalServices
 * @param {string} reason 
*/
this.GlobalServices.disconnected = function(reason){};
/** 
 * @signal
 * @function myUsernameChanged
 * @memberof GlobalServices
 * @param {string} username 
*/
this.GlobalServices.myUsernameChanged = function(username){};
/** 
 * @signal
 * @function downloadInfoChanged
 * @memberof GlobalServices
 * @param {DownloadInfoResult} info 
*/
this.GlobalServices.downloadInfoChanged = function(info){};
/** 
 * @signal
 * @function findableByChanged
 * @memberof GlobalServices
 * @param {string} discoverabilityMode 
*/
this.GlobalServices.findableByChanged = function(discoverabilityMode){};/** 
 * @namespace  
*/
this.Controller = {};
/** 
 * @slot
 * @function getAllActions
 * @memberof Controller
 * @returns {UserInputMapper.Action[]} 
*/
this.Controller.getAllActions = function(){};
/** 
 * @slot
 * @function getInputChannelsForAction
 * @memberof Controller
 * @param {UserInputMapper.Action} action
 * @returns {UserInputMapper.InputChannel[]} 
*/
this.Controller.getInputChannelsForAction = function(action){};
/** 
 * @slot
 * @function getDeviceName
 * @memberof Controller
 * @param {number} device
 * @returns {string} 
*/
this.Controller.getDeviceName = function(device){};
/** 
 * @slot
 * @function getAllInputsForDevice
 * @memberof Controller
 * @param {number} device
 * @returns {UserInputMapper.InputChannel[]} 
*/
this.Controller.getAllInputsForDevice = function(device){};
/** 
 * @slot
 * @function addInputChannel
 * @memberof Controller
 * @param {UserInputMapper.InputChannel} inputChannel
 * @returns {bool} 
*/
this.Controller.addInputChannel = function(inputChannel){};
/** 
 * @slot
 * @function removeInputChannel
 * @memberof Controller
 * @param {UserInputMapper.InputChannel} inputChannel
 * @returns {bool} 
*/
this.Controller.removeInputChannel = function(inputChannel){};
/** 
 * @slot
 * @function getAvailableInputs
 * @memberof Controller
 * @param {number} device
 * @returns {UserInputMapper.InputPair[]} 
*/
this.Controller.getAvailableInputs = function(device){};
/** 
 * @slot
 * @function resetAllDeviceBindings
 * @memberof Controller 
*/
this.Controller.resetAllDeviceBindings = function(){};
/** 
 * @slot
 * @function resetDevice
 * @memberof Controller
 * @param {number} device 
*/
this.Controller.resetDevice = function(device){};
/** 
 * @slot
 * @function findDevice
 * @memberof Controller
 * @param {string} name
 * @returns {number} 
*/
this.Controller.findDevice = function(name){};
/** 
 * @slot
 * @function isPrimaryButtonPressed
 * @memberof Controller
 * @returns {bool} 
*/
this.Controller.isPrimaryButtonPressed = function(){};
/** 
 * @slot
 * @function getPrimaryJoystickPosition
 * @memberof Controller
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getPrimaryJoystickPosition = function(){};
/** 
 * @slot
 * @function getNumberOfButtons
 * @memberof Controller
 * @returns {number} 
*/
this.Controller.getNumberOfButtons = function(){};
/** 
 * @slot
 * @function isButtonPressed
 * @memberof Controller
 * @param {number} buttonIndex
 * @returns {bool} 
*/
this.Controller.isButtonPressed = function(buttonIndex){};
/** 
 * @slot
 * @function getNumberOfTriggers
 * @memberof Controller
 * @returns {number} 
*/
this.Controller.getNumberOfTriggers = function(){};
/** 
 * @slot
 * @function getTriggerValue
 * @memberof Controller
 * @param {number} triggerIndex
 * @returns {number} 
*/
this.Controller.getTriggerValue = function(triggerIndex){};
/** 
 * @slot
 * @function getNumberOfJoysticks
 * @memberof Controller
 * @returns {number} 
*/
this.Controller.getNumberOfJoysticks = function(){};
/** 
 * @slot
 * @function getJoystickPosition
 * @memberof Controller
 * @param {number} joystickIndex
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getJoystickPosition = function(joystickIndex){};
/** 
 * @slot
 * @function getNumberOfSpatialControls
 * @memberof Controller
 * @returns {number} 
*/
this.Controller.getNumberOfSpatialControls = function(){};
/** 
 * @slot
 * @function getSpatialControlPosition
 * @memberof Controller
 * @param {number} controlIndex
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getSpatialControlPosition = function(controlIndex){};
/** 
 * @slot
 * @function getSpatialControlVelocity
 * @memberof Controller
 * @param {number} controlIndex
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getSpatialControlVelocity = function(controlIndex){};
/** 
 * @slot
 * @function getSpatialControlNormal
 * @memberof Controller
 * @param {number} controlIndex
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getSpatialControlNormal = function(controlIndex){};
/** 
 * @slot
 * @function getSpatialControlRawRotation
 * @memberof Controller
 * @param {number} controlIndex
 * @returns {{x: number, y: number, z: number, w: number}} 
*/
this.Controller.getSpatialControlRawRotation = function(controlIndex){};
/** 
 * @slot
 * @function getSpatialControlRawAngularVelocity
 * @memberof Controller
 * @param {number} controlIndex
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getSpatialControlRawAngularVelocity = function(controlIndex){};
/** 
 * @slot
 * @function captureKeyEvents
 * @memberof Controller
 * @param {KeyEvent} event 
*/
this.Controller.captureKeyEvents = function(event){};
/** 
 * @slot
 * @function releaseKeyEvents
 * @memberof Controller
 * @param {KeyEvent} event 
*/
this.Controller.releaseKeyEvents = function(event){};
/** 
 * @slot
 * @function captureMouseEvents
 * @memberof Controller 
*/
this.Controller.captureMouseEvents = function(){};
/** 
 * @slot
 * @function releaseMouseEvents
 * @memberof Controller 
*/
this.Controller.releaseMouseEvents = function(){};
/** 
 * @slot
 * @function captureTouchEvents
 * @memberof Controller 
*/
this.Controller.captureTouchEvents = function(){};
/** 
 * @slot
 * @function releaseTouchEvents
 * @memberof Controller 
*/
this.Controller.releaseTouchEvents = function(){};
/** 
 * @slot
 * @function captureWheelEvents
 * @memberof Controller 
*/
this.Controller.captureWheelEvents = function(){};
/** 
 * @slot
 * @function releaseWheelEvents
 * @memberof Controller 
*/
this.Controller.releaseWheelEvents = function(){};
/** 
 * @slot
 * @function captureActionEvents
 * @memberof Controller 
*/
this.Controller.captureActionEvents = function(){};
/** 
 * @slot
 * @function releaseActionEvents
 * @memberof Controller 
*/
this.Controller.releaseActionEvents = function(){};
/** 
 * @slot
 * @function captureJoystick
 * @memberof Controller
 * @param {number} joystickIndex 
*/
this.Controller.captureJoystick = function(joystickIndex){};
/** 
 * @slot
 * @function releaseJoystick
 * @memberof Controller
 * @param {number} joystickIndex 
*/
this.Controller.releaseJoystick = function(joystickIndex){};
/** 
 * @slot
 * @function getViewportDimensions
 * @memberof Controller
 * @returns {{x: number, y: number, z: number}} 
*/
this.Controller.getViewportDimensions = function(){};
/** 
 * Factory to create an <ref refid="class_input_controller" kindref="compound" >InputController</ref>
 * 
 * @slot
 * @function createInputController
 * @memberof Controller
 * @param {string} deviceName
 * @param {string} tracker
 * @returns {AbstractInputController} 
*/
this.Controller.createInputController = function(deviceName, tracker){};
/** 
 * @slot
 * @function releaseInputController
 * @memberof Controller
 * @param {AbstractInputController} input 
*/
this.Controller.releaseInputController = function(input){};/** 
 * @namespace 
 * @property {string} resources 
*/
this.Paths = {};/** 
 * @namespace  
*/
this.ScriptDiscoveryService = {};
/** 
 * @signal
 * @function stopScriptName
 * @memberof ScriptDiscoveryService
 * @param {string} name
 * @param {bool} restart 
*/
this.ScriptDiscoveryService.stopScriptName = function(name, restart){};
/** 
 * @slot
 * @function scriptStopped
 * @memberof ScriptDiscoveryService
 * @param {string} scriptName 
*/
this.ScriptDiscoveryService.scriptStopped = function(scriptName){};
/** 
 * @slot
 * @function getRunning
 * @memberof ScriptDiscoveryService
 * @returns {Array} 
*/
this.ScriptDiscoveryService.getRunning = function(){};
/** 
 * @slot
 * @function getPublic
 * @memberof ScriptDiscoveryService
 * @returns {Array} 
*/
this.ScriptDiscoveryService.getPublic = function(){};
/** 
 * @slot
 * @function getLocal
 * @memberof ScriptDiscoveryService
 * @returns {Array} 
*/
this.ScriptDiscoveryService.getLocal = function(){};/** 
 * @namespace 
 * @property {bool} magnifier
 * @property {bool} active 
*/
this.HMD = {};
/** 
 * @slot
 * @function toggleMagnifier
 * @memberof HMD 
*/
this.HMD.toggleMagnifier = function(){};/** 
 * @namespace  
*/
this.SoundCache = {};
/** 
 * @function getSound
 * @memberof SoundCache
 * @param {QUrl} url
 * @returns {SharedSoundPointer} 
*/
this.SoundCache.getSound = function(url){};/** 
 * @namespace 
 * @property {number} innerWidth
 * @property {number} innerHeight
 * @property {number} x
 * @property {number} y
 * @property {bool} cursorVisible 
*/
this.Window = {};
/** 
 * @slot
 * @function getCursorPositionX
 * @memberof Window
 * @returns {object} 
*/
this.Window.getCursorPositionX = function(){};
/** 
 * @slot
 * @function getCursorPositionY
 * @memberof Window
 * @returns {object} 
*/
this.Window.getCursorPositionY = function(){};
/** 
 * @slot
 * @function setCursorPosition
 * @memberof Window
 * @param {number} x
 * @param {number} y 
*/
this.Window.setCursorPosition = function(x, y){};
/** 
 * @slot
 * @function setCursorVisible
 * @memberof Window
 * @param {bool} visible 
*/
this.Window.setCursorVisible = function(visible){};
/** 
 * @slot
 * @function hasFocus
 * @memberof Window
 * @returns {object} 
*/
this.Window.hasFocus = function(){};
/** 
 * @slot
 * @function setFocus
 * @memberof Window 
*/
this.Window.setFocus = function(){};
/** 
 * @slot
 * @function raiseMainWindow
 * @memberof Window 
*/
this.Window.raiseMainWindow = function(){};
/** 
 * @slot
 * @function alert
 * @memberof Window
 * @param {string} message
 * @returns {object} 
*/
this.Window.alert = function(message){};
/** 
 * @slot
 * @function confirm
 * @memberof Window
 * @param {string} message
 * @returns {object} 
*/
this.Window.confirm = function(message){};
/** 
 * @slot
 * @function form
 * @memberof Window
 * @param {string} title
 * @param {object} array
 * @returns {object} 
*/
this.Window.form = function(title, array){};
/** 
 * @slot
 * @function prompt
 * @memberof Window
 * @param {string} message
 * @param {string} defaultText
 * @returns {object} 
*/
this.Window.prompt = function(message, defaultText){};
/** 
 * @slot
 * @function browse
 * @memberof Window
 * @param {string} title
 * @param {string} directory
 * @param {string} nameFilter
 * @returns {object} 
*/
this.Window.browse = function(title, directory, nameFilter){};
/** 
 * @slot
 * @function save
 * @memberof Window
 * @param {string} title
 * @param {string} directory
 * @param {string} nameFilter
 * @returns {object} 
*/
this.Window.save = function(title, directory, nameFilter){};
/** 
 * @slot
 * @function s3Browse
 * @memberof Window
 * @param {string} nameFilter
 * @returns {object} 
*/
this.Window.s3Browse = function(nameFilter){};
/** 
 * @slot
 * @function nonBlockingForm
 * @memberof Window
 * @param {string} title
 * @param {object} array 
*/
this.Window.nonBlockingForm = function(title, array){};
/** 
 * @slot
 * @function reloadNonBlockingForm
 * @memberof Window
 * @param {object} array 
*/
this.Window.reloadNonBlockingForm = function(array){};
/** 
 * @slot
 * @function getNonBlockingFormResult
 * @memberof Window
 * @param {object} array
 * @returns {object} 
*/
this.Window.getNonBlockingFormResult = function(array){};
/** 
 * @slot
 * @function peekNonBlockingFormResult
 * @memberof Window
 * @param {object} array
 * @returns {object} 
*/
this.Window.peekNonBlockingFormResult = function(array){};
/** 
 * @signal
 * @function domainChanged
 * @memberof Window
 * @param {string} domainHostname 
*/
this.Window.domainChanged = function(domainHostname){};
/** 
 * @signal
 * @function inlineButtonClicked
 * @memberof Window
 * @param {string} name 
*/
this.Window.inlineButtonClicked = function(name){};
/** 
 * @signal
 * @function nonBlockingFormClosed
 * @memberof Window 
*/
this.Window.nonBlockingFormClosed = function(){};
/** 
 * @signal
 * @function svoImportRequested
 * @memberof Window
 * @param {string} url 
*/
this.Window.svoImportRequested = function(url){};
/** 
 * @signal
 * @function domainConnectionRefused
 * @memberof Window
 * @param {string} reason 
*/
this.Window.domainConnectionRefused = function(reason){};/** 
 * @namespace  
*/
this.Clipboard = {};
/** 
 * @signal
 * @function readyToImport
 * @memberof Clipboard 
*/
this.Clipboard.readyToImport = function(){};
/** 
 * @slot
 * @function getClipboardContentsLargestDimension
 * @memberof Clipboard
 * @returns {number} 
*/
this.Clipboard.getClipboardContentsLargestDimension = function(){};
/** 
 * returns the largest dimension of everything on the clipboard
 * 
 * @slot
 * @function importEntities
 * @memberof Clipboard
 * @param {string} filename
 * @returns {bool} 
*/
this.Clipboard.importEntities = function(filename){};
/** 
 * @slot
 * @function exportEntities
 * @memberof Clipboard
 * @param {string} filename
 * @param {EntityItemID[]} entityIDs
 * @returns {bool} 
*/
this.Clipboard.exportEntities = function(filename, entityIDs){};
/** 
 * @slot
 * @function exportEntities
 * @memberof Clipboard
 * @param {string} filename
 * @param {number} x
 * @param {number} y
 * @param {number} z
 * @param {number} s
 * @returns {bool} 
*/
this.Clipboard.exportEntities = function(filename, x, y, z, s){};
/** 
 * @slot
 * @function pasteEntities
 * @memberof Clipboard
 * @param {{x: number, y: number, z: number}} position
 * @returns {EntityItemID[]} 
*/
this.Clipboard.pasteEntities = function(position){};/** 
 * @namespace  
*/
this.AvatarManager = {};
/** 
 * @function setLocalLights
 * @memberof AvatarManager
 * @param {AvatarManager.LocalLight[]} localLights 
*/
this.AvatarManager.setLocalLights = function(localLights){};
/** 
 * @function getLocalLights
 * @memberof AvatarManager
 * @returns {AvatarManager.LocalLight[]} 
*/
this.AvatarManager.getLocalLights = function(){};
/** 
 * @slot
 * @function setShouldShowReceiveStats
 * @memberof AvatarManager
 * @param {bool} shouldShowReceiveStats 
*/
this.AvatarManager.setShouldShowReceiveStats = function(shouldShowReceiveStats){};
/** 
 * @slot
 * @function updateAvatarRenderStatus
 * @memberof AvatarManager
 * @param {bool} shouldRenderAvatars 
*/
this.AvatarManager.updateAvatarRenderStatus = function(shouldRenderAvatars){};/** 
 * @namespace  
*/
this.Menu = {};
/** 
 * @slot
 * @function addMenu
 * @memberof Menu
 * @param {string} menuName 
*/
this.Menu.addMenu = function(menuName){};
/** 
 * @slot
 * @function removeMenu
 * @memberof Menu
 * @param {string} menuName 
*/
this.Menu.removeMenu = function(menuName){};
/** 
 * @slot
 * @function menuExists
 * @memberof Menu
 * @param {string} menuName
 * @returns {bool} 
*/
this.Menu.menuExists = function(menuName){};
/** 
 * @slot
 * @function addSeparator
 * @memberof Menu
 * @param {string} menuName
 * @param {string} separatorName 
*/
this.Menu.addSeparator = function(menuName, separatorName){};
/** 
 * @slot
 * @function removeSeparator
 * @memberof Menu
 * @param {string} menuName
 * @param {string} separatorName 
*/
this.Menu.removeSeparator = function(menuName, separatorName){};
/** 
 * @slot
 * @function addMenuItem
 * @memberof Menu
 * @param {MenuItemProperties} properties 
*/
this.Menu.addMenuItem = function(properties){};
/** 
 * @slot
 * @function addMenuItem
 * @memberof Menu
 * @param {string} menuName
 * @param {string} menuitem
 * @param {string} shortcutKey 
*/
this.Menu.addMenuItem = function(menuName, menuitem, shortcutKey){};
/** 
 * @slot
 * @function addMenuItem
 * @memberof Menu
 * @param {string} menuName
 * @param {string} menuitem 
*/
this.Menu.addMenuItem = function(menuName, menuitem){};
/** 
 * @slot
 * @function removeMenuItem
 * @memberof Menu
 * @param {string} menuName
 * @param {string} menuitem 
*/
this.Menu.removeMenuItem = function(menuName, menuitem){};
/** 
 * @slot
 * @function menuItemExists
 * @memberof Menu
 * @param {string} menuName
 * @param {string} menuitem
 * @returns {bool} 
*/
this.Menu.menuItemExists = function(menuName, menuitem){};
/** 
 * @slot
 * @function isOptionChecked
 * @memberof Menu
 * @param {string} menuOption
 * @returns {bool} 
*/
this.Menu.isOptionChecked = function(menuOption){};
/** 
 * @slot
 * @function setIsOptionChecked
 * @memberof Menu
 * @param {string} menuOption
 * @param {bool} isChecked 
*/
this.Menu.setIsOptionChecked = function(menuOption, isChecked){};
/** 
 * @signal
 * @function menuItemEvent
 * @memberof Menu
 * @param {string} menuItem 
*/
this.Menu.menuItemEvent = function(menuItem){};/** 
 * @namespace 
 * @property {bool} shouldRenderAvatars
 * @property {bool} shouldRenderEntities 
*/
this.Scene = {};
/** 
 * @function setStageOrientation
 * @memberof Scene
 * @param {{x: number, y: number, z: number, w: number}} orientation 
*/
this.Scene.setStageOrientation = function(orientation){};
/** 
 * @function setStageLocation
 * @memberof Scene
 * @param {number} longitude
 * @param {number} latitude
 * @param {number} altitude 
*/
this.Scene.setStageLocation = function(longitude, latitude, altitude){};
/** 
 * @function getStageLocationLongitude
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getStageLocationLongitude = function(){};
/** 
 * @function getStageLocationLatitude
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getStageLocationLatitude = function(){};
/** 
 * @function getStageLocationAltitude
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getStageLocationAltitude = function(){};
/** 
 * @function setStageDayTime
 * @memberof Scene
 * @param {number} hour 
*/
this.Scene.setStageDayTime = function(hour){};
/** 
 * @function getStageDayTime
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getStageDayTime = function(){};
/** 
 * @function setStageYearTime
 * @memberof Scene
 * @param {number} day 
*/
this.Scene.setStageYearTime = function(day){};
/** 
 * @function getStageYearTime
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getStageYearTime = function(){};
/** 
 * @function setStageSunModelEnable
 * @memberof Scene
 * @param {bool} isEnabled 
*/
this.Scene.setStageSunModelEnable = function(isEnabled){};
/** 
 * @function isStageSunModelEnabled
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.isStageSunModelEnabled = function(){};
/** 
 * @function setKeyLightColor
 * @memberof Scene
 * @param {{x: number, y: number, z: number}} color 
*/
this.Scene.setKeyLightColor = function(color){};
/** 
 * @function getKeyLightColor
 * @memberof Scene
 * @returns {{x: number, y: number, z: number}} 
*/
this.Scene.getKeyLightColor = function(){};
/** 
 * @function setKeyLightIntensity
 * @memberof Scene
 * @param {number} intensity 
*/
this.Scene.setKeyLightIntensity = function(intensity){};
/** 
 * @function getKeyLightIntensity
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getKeyLightIntensity = function(){};
/** 
 * @function setKeyLightAmbientIntensity
 * @memberof Scene
 * @param {number} intensity 
*/
this.Scene.setKeyLightAmbientIntensity = function(intensity){};
/** 
 * @function getKeyLightAmbientIntensity
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getKeyLightAmbientIntensity = function(){};
/** 
 * @function setKeyLightDirection
 * @memberof Scene
 * @param {{x: number, y: number, z: number}} direction 
*/
this.Scene.setKeyLightDirection = function(direction){};
/** 
 * @function getKeyLightDirection
 * @memberof Scene
 * @returns {{x: number, y: number, z: number}} 
*/
this.Scene.getKeyLightDirection = function(){};
/** 
 * @function setBackgroundMode
 * @memberof Scene
 * @param {string} mode 
*/
this.Scene.setBackgroundMode = function(mode){};
/** 
 * @function getBackgroundMode
 * @memberof Scene
 * @returns {string} 
*/
this.Scene.getBackgroundMode = function(){};
/** 
 * @function setShouldRenderAvatars
 * @memberof Scene
 * @param {bool} shouldRenderAvatars 
*/
this.Scene.setShouldRenderAvatars = function(shouldRenderAvatars){};
/** 
 * @function shouldRenderAvatars
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.shouldRenderAvatars = function(){};
/** 
 * @function setShouldRenderEntities
 * @memberof Scene
 * @param {bool} shouldRenderEntities 
*/
this.Scene.setShouldRenderEntities = function(shouldRenderEntities){};
/** 
 * @function shouldRenderEntities
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.shouldRenderEntities = function(){};
/** 
 * @function setEngineRenderOpaque
 * @memberof Scene
 * @param {bool} renderOpaque 
*/
this.Scene.setEngineRenderOpaque = function(renderOpaque){};
/** 
 * @function doEngineRenderOpaque
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineRenderOpaque = function(){};
/** 
 * @function setEngineRenderTransparent
 * @memberof Scene
 * @param {bool} renderTransparent 
*/
this.Scene.setEngineRenderTransparent = function(renderTransparent){};
/** 
 * @function doEngineRenderTransparent
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineRenderTransparent = function(){};
/** 
 * @function setEngineCullOpaque
 * @memberof Scene
 * @param {bool} cullOpaque 
*/
this.Scene.setEngineCullOpaque = function(cullOpaque){};
/** 
 * @function doEngineCullOpaque
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineCullOpaque = function(){};
/** 
 * @function setEngineCullTransparent
 * @memberof Scene
 * @param {bool} cullTransparent 
*/
this.Scene.setEngineCullTransparent = function(cullTransparent){};
/** 
 * @function doEngineCullTransparent
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineCullTransparent = function(){};
/** 
 * @function setEngineSortOpaque
 * @memberof Scene
 * @param {bool} sortOpaque 
*/
this.Scene.setEngineSortOpaque = function(sortOpaque){};
/** 
 * @function doEngineSortOpaque
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineSortOpaque = function(){};
/** 
 * @function setEngineSortTransparent
 * @memberof Scene
 * @param {bool} sortTransparent 
*/
this.Scene.setEngineSortTransparent = function(sortTransparent){};
/** 
 * @function doEngineSortTransparent
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineSortTransparent = function(){};
/** 
 * @function getEngineNumDrawnOpaqueItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumDrawnOpaqueItems = function(){};
/** 
 * @function getEngineNumDrawnTransparentItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumDrawnTransparentItems = function(){};
/** 
 * @function getEngineNumDrawnOverlay3DItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumDrawnOverlay3DItems = function(){};
/** 
 * @function getEngineNumFeedOpaqueItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumFeedOpaqueItems = function(){};
/** 
 * @function getEngineNumFeedTransparentItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumFeedTransparentItems = function(){};
/** 
 * @function getEngineNumFeedOverlay3DItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineNumFeedOverlay3DItems = function(){};
/** 
 * @function setEngineMaxDrawnOpaqueItems
 * @memberof Scene
 * @param {number} count 
*/
this.Scene.setEngineMaxDrawnOpaqueItems = function(count){};
/** 
 * @function getEngineMaxDrawnOpaqueItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineMaxDrawnOpaqueItems = function(){};
/** 
 * @function setEngineMaxDrawnTransparentItems
 * @memberof Scene
 * @param {number} count 
*/
this.Scene.setEngineMaxDrawnTransparentItems = function(count){};
/** 
 * @function getEngineMaxDrawnTransparentItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineMaxDrawnTransparentItems = function(){};
/** 
 * @function setEngineMaxDrawnOverlay3DItems
 * @memberof Scene
 * @param {number} count 
*/
this.Scene.setEngineMaxDrawnOverlay3DItems = function(count){};
/** 
 * @function getEngineMaxDrawnOverlay3DItems
 * @memberof Scene
 * @returns {number} 
*/
this.Scene.getEngineMaxDrawnOverlay3DItems = function(){};
/** 
 * @function setEngineDisplayItemStatus
 * @memberof Scene
 * @param {bool} display 
*/
this.Scene.setEngineDisplayItemStatus = function(display){};
/** 
 * @function doEngineDisplayItemStatus
 * @memberof Scene
 * @returns {bool} 
*/
this.Scene.doEngineDisplayItemStatus = function(){};
/** 
 * @signal
 * @function shouldRenderAvatarsChanged
 * @memberof Scene
 * @param {bool} shouldRenderAvatars 
*/
this.Scene.shouldRenderAvatarsChanged = function(shouldRenderAvatars){};
/** 
 * @signal
 * @function shouldRenderEntitiesChanged
 * @memberof Scene
 * @param {bool} shouldRenderEntities 
*/
this.Scene.shouldRenderEntitiesChanged = function(shouldRenderEntities){};/** 
 * @namespace 
 * @property {bool} isPlaying
 * @property {number} loudness 
*/
this.ScriptAudioInjector = {};
/** 
 * @slot
 * @function restart
 * @memberof ScriptAudioInjector 
*/
this.ScriptAudioInjector.restart = function(){};
/** 
 * @slot
 * @function stop
 * @memberof ScriptAudioInjector 
*/
this.ScriptAudioInjector.stop = function(){};
/** 
 * @slot
 * @function setOptions
 * @memberof ScriptAudioInjector
 * @param {AudioInjectorOptions} options 
*/
this.ScriptAudioInjector.setOptions = function(options){};
/** 
 * @slot
 * @function getLoudness
 * @memberof ScriptAudioInjector
 * @returns {number} 
*/
this.ScriptAudioInjector.getLoudness = function(){};
/** 
 * @slot
 * @function isPlaying
 * @memberof ScriptAudioInjector
 * @returns {bool} 
*/
this.ScriptAudioInjector.isPlaying = function(){};
/** 
 * @signal
 * @function finished
 * @memberof ScriptAudioInjector 
*/
this.ScriptAudioInjector.finished = function(){};/** 
 * @namespace  
*/
this.AvatarList = {};
/** 
 * @slot
 * @function isAvatarInRange
 * @memberof AvatarList
 * @param {{x: number, y: number, z: number}} position
 * @param {number} range
 * @returns {bool} 
*/
this.AvatarList.isAvatarInRange = function(position, range){};/** 
 * @namespace  
*/
this.Entities = {};
/** 
 * @slot
 * @function canAdjustLocks
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.canAdjustLocks = function(){};
/** 
 * @slot
 * @function canRez
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.canRez = function(){};
/** 
 * adds a model with the specific properties
 * 
 * @slot
 * @function addEntity
 * @memberof Entities
 * @param {EntityItemProperties} properties
 * @returns {QUuid} 
*/
this.Entities.addEntity = function(properties){};
/** 
 * gets the current model properties for a specific model this function will not find return results in
 * script engine contexts which don't have access to models
 * 
 * @slot
 * @function getEntityProperties
 * @memberof Entities
 * @param {QUuid} entityID
 * @returns {EntityItemProperties} 
*/
this.Entities.getEntityProperties = function(entityID){};
/** 
 * edits a model updating only the included properties, will return the identified <ref
 * refid="class_entity_item_i_d" kindref="compound" >EntityItemID</ref>
 * 
 * @slot
 * @function editEntity
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {EntityItemProperties} properties
 * @returns {QUuid} 
*/
this.Entities.editEntity = function(entityID, properties){};
/** 
 * deletes a model
 * 
 * @slot
 * @function deleteEntity
 * @memberof Entities
 * @param {QUuid} entityID 
*/
this.Entities.deleteEntity = function(entityID){};
/** 
 * finds the closest model to the center point, within the radius will return a EntityItemID.isKnownID
 * = false if no models are in the radius this function will not find any models in script engine
 * contexts which don't have access to models
 * 
 * @slot
 * @function findClosestEntity
 * @memberof Entities
 * @param {{x: number, y: number, z: number}} center
 * @param {number} radius
 * @returns {QUuid} 
*/
this.Entities.findClosestEntity = function(center, radius){};
/** 
 * finds models within the search sphere specified by the center point and radius this function will
 * not find any models in script engine contexts which don't have access to models
 * 
 * @slot
 * @function findEntities
 * @memberof Entities
 * @param {{x: number, y: number, z: number}} center
 * @param {number} radius
 * @returns {QUuid[]} 
*/
this.Entities.findEntities = function(center, radius){};
/** 
 * finds models within the search sphere specified by the center point and radius this function will
 * not find any models in script engine contexts which don't have access to models
 * 
 * @slot
 * @function findEntitiesInBox
 * @memberof Entities
 * @param {{x: number, y: number, z: number}} corner
 * @param {{x: number, y: number, z: number}} dimensions
 * @returns {QUuid[]} 
*/
this.Entities.findEntitiesInBox = function(corner, dimensions){};
/** 
 * If the scripting context has visible entities, this will determine a ray intersection, the results
 * may be inaccurate if the engine is unable to access the visible entities, in which case
 * result.accurate will be false.
 * 
 * @slot
 * @function findRayIntersection
 * @memberof Entities
 * @param {PickRay} ray
 * @param {bool} precisionPicking
 * @returns {RayToEntityIntersectionResult} 
*/
this.Entities.findRayIntersection = function(ray, precisionPicking){};
/** 
 * If the scripting context has visible entities, this will determine a ray intersection, and will
 * block in order to return an accurate result.
 * 
 * @slot
 * @function findRayIntersectionBlocking
 * @memberof Entities
 * @param {PickRay} ray
 * @param {bool} precisionPicking
 * @returns {RayToEntityIntersectionResult} 
*/
this.Entities.findRayIntersectionBlocking = function(ray, precisionPicking){};
/** 
 * @slot
 * @function setLightsArePickable
 * @memberof Entities
 * @param {bool} value 
*/
this.Entities.setLightsArePickable = function(value){};
/** 
 * @slot
 * @function getLightsArePickable
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.getLightsArePickable = function(){};
/** 
 * @slot
 * @function setZonesArePickable
 * @memberof Entities
 * @param {bool} value 
*/
this.Entities.setZonesArePickable = function(value){};
/** 
 * @slot
 * @function getZonesArePickable
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.getZonesArePickable = function(){};
/** 
 * @slot
 * @function setDrawZoneBoundaries
 * @memberof Entities
 * @param {bool} value 
*/
this.Entities.setDrawZoneBoundaries = function(value){};
/** 
 * @slot
 * @function getDrawZoneBoundaries
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.getDrawZoneBoundaries = function(){};
/** 
 * @slot
 * @function setSendPhysicsUpdates
 * @memberof Entities
 * @param {bool} value 
*/
this.Entities.setSendPhysicsUpdates = function(value){};
/** 
 * @slot
 * @function getSendPhysicsUpdates
 * @memberof Entities
 * @returns {bool} 
*/
this.Entities.getSendPhysicsUpdates = function(){};
/** 
 * @slot
 * @function setVoxelSphere
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {{x: number, y: number, z: number}} center
 * @param {number} radius
 * @param {number} value
 * @returns {bool} 
*/
this.Entities.setVoxelSphere = function(entityID, center, radius, value){};
/** 
 * @slot
 * @function setVoxel
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {{x: number, y: number, z: number}} position
 * @param {number} value
 * @returns {bool} 
*/
this.Entities.setVoxel = function(entityID, position, value){};
/** 
 * @slot
 * @function setAllVoxels
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {number} value
 * @returns {bool} 
*/
this.Entities.setAllVoxels = function(entityID, value){};
/** 
 * @slot
 * @function setAllPoints
 * @memberof Entities
 * @param {QUuid} entityID
 * @param Arraypoints
 * @returns {bool} 
*/
this.Entities.setAllPoints = function(entityID, points){};
/** 
 * @slot
 * @function appendPoint
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {{x: number, y: number, z: number}} point
 * @returns {bool} 
*/
this.Entities.appendPoint = function(entityID, point){};
/** 
 * @slot
 * @function dumpTree
 * @memberof Entities 
*/
this.Entities.dumpTree = function(){};
/** 
 * @slot
 * @function addAction
 * @memberof Entities
 * @param {string} actionTypeString
 * @param {QUuid} entityID
 * @param {object} arguments
 * @returns {QUuid} 
*/
this.Entities.addAction = function(actionTypeString, entityID, args){};
/** 
 * @slot
 * @function updateAction
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {QUuid} actionID
 * @param {object} arguments
 * @returns {bool} 
*/
this.Entities.updateAction = function(entityID, actionID, args){};
/** 
 * @slot
 * @function deleteAction
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {QUuid} actionID
 * @returns {bool} 
*/
this.Entities.deleteAction = function(entityID, actionID){};
/** 
 * @slot
 * @function getActionIDs
 * @memberof Entities
 * @param {QUuid} entityID
 * @returns {QUuid[]} 
*/
this.Entities.getActionIDs = function(entityID){};
/** 
 * @slot
 * @function getActionArguments
 * @memberof Entities
 * @param {QUuid} entityID
 * @param {QUuid} actionID
 * @returns {object} 
*/
this.Entities.getActionArguments = function(entityID, actionID){};
/** 
 * @signal
 * @function entityCollisionWithEntity
 * @memberof Entities
 * @param {EntityItemID} idA
 * @param {EntityItemID} idB
 * @param {Collision} collision 
*/
this.Entities.entityCollisionWithEntity = function(idA, idB, collision){};
/** 
 * @signal
 * @function collisionWithEntity
 * @memberof Entities
 * @param {EntityItemID} idA
 * @param {EntityItemID} idB
 * @param {Collision} collision 
*/
this.Entities.collisionWithEntity = function(idA, idB, collision){};
/** 
 * @signal
 * @function canAdjustLocksChanged
 * @memberof Entities
 * @param {bool} canAdjustLocks 
*/
this.Entities.canAdjustLocksChanged = function(canAdjustLocks){};
/** 
 * @signal
 * @function canRezChanged
 * @memberof Entities
 * @param {bool} canRez 
*/
this.Entities.canRezChanged = function(canRez){};
/** 
 * @signal
 * @function mousePressOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.mousePressOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function mouseMoveOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.mouseMoveOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function mouseReleaseOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.mouseReleaseOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function clickDownOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.clickDownOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function holdingClickOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.holdingClickOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function clickReleaseOnEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.clickReleaseOnEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function hoverEnterEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.hoverEnterEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function hoverOverEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.hoverOverEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function hoverLeaveEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID
 * @param {MouseEvent} event 
*/
this.Entities.hoverLeaveEntity = function(entityItemID, event){};
/** 
 * @signal
 * @function enterEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID 
*/
this.Entities.enterEntity = function(entityItemID){};
/** 
 * @signal
 * @function leaveEntity
 * @memberof Entities
 * @param {EntityItemID} entityItemID 
*/
this.Entities.leaveEntity = function(entityItemID){};
/** 
 * @signal
 * @function deletingEntity
 * @memberof Entities
 * @param {EntityItemID} entityID 
*/
this.Entities.deletingEntity = function(entityID){};
/** 
 * @signal
 * @function addingEntity
 * @memberof Entities
 * @param {EntityItemID} entityID 
*/
this.Entities.addingEntity = function(entityID){};
/** 
 * @signal
 * @function clearingEntities
 * @memberof Entities 
*/
this.Entities.clearingEntities = function(){};/** 
 * @namespace  
*/
this.Vec3 = {};
/** 
 * @slot
 * @function reflect
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.reflect = function(v1, v2){};
/** 
 * @slot
 * @function cross
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.cross = function(v1, v2){};
/** 
 * @slot
 * @function dot
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {number} 
*/
this.Vec3.dot = function(v1, v2){};
/** 
 * @slot
 * @function multiply
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {number} f
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.multiply = function(v1, f){};
/** 
 * @slot
 * @function multiply
 * @memberof Vec3
 * @param {number} f
 * @param {{x: number, y: number, z: number}} v1
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.multiply = function(f, v1){};
/** 
 * @slot
 * @function multiplyQbyV
 * @memberof Vec3
 * @param {{x: number, y: number, z: number, w: number}} q
 * @param {{x: number, y: number, z: number}} v
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.multiplyQbyV = function(q, v){};
/** 
 * @slot
 * @function sum
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.sum = function(v1, v2){};
/** 
 * @slot
 * @function subtract
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.subtract = function(v1, v2){};
/** 
 * @slot
 * @function length
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v
 * @returns {number} 
*/
this.Vec3.length = function(v){};
/** 
 * @slot
 * @function distance
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {number} 
*/
this.Vec3.distance = function(v1, v2){};
/** 
 * @slot
 * @function orientedAngle
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @param {{x: number, y: number, z: number}} v3
 * @returns {number} 
*/
this.Vec3.orientedAngle = function(v1, v2, v3){};
/** 
 * @slot
 * @function normalize
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.normalize = function(v){};
/** 
 * @slot
 * @function mix
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @param {number} m
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.mix = function(v1, v2, m){};
/** 
 * @slot
 * @function print
 * @memberof Vec3
 * @param {string} lable
 * @param {{x: number, y: number, z: number}} v 
*/
this.Vec3.print = function(lable, v){};
/** 
 * @slot
 * @function equal
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v1
 * @param {{x: number, y: number, z: number}} v2
 * @returns {bool} 
*/
this.Vec3.equal = function(v1, v2){};
/** 
 * @slot
 * @function toPolar
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} v
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.toPolar = function(v){};
/** 
 * @slot
 * @function fromPolar
 * @memberof Vec3
 * @param {{x: number, y: number, z: number}} polar
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.fromPolar = function(polar){};
/** 
 * @slot
 * @function fromPolar
 * @memberof Vec3
 * @param {number} elevation
 * @param {number} azimuth
 * @returns {{x: number, y: number, z: number}} 
*/
this.Vec3.fromPolar = function(elevation, azimuth){};
})();


Vec3.length({x: 10, y: 10});

Vec3.toPolar({});


























