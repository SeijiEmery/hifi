//cookie-tester.js
//
//
// Created by Bridget Went, 7/7/2015
//  
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html

Script.include('./utilities/tools/cookies.js');

var panel = new Panel(600, 400);

panel.newCheckbox("Enable Sun Model", 
    function(value) { Scene.setStageSunModelEnable((value != 0)); },
    function() { return Scene.isStageSunModelEnabled(); },
    function(value) { return (value); }
);

var subPanel = panel.newSubPanel("Distances:");

subPanel.newSlider("Moon: Distance", -180, 180,
    function(value) { Scene.setStageLocation(value, Scene.getStageLocationLatitude(), Scene.getStageLocationAltitude()); },
    function() { return Scene.getStageLocationLongitude(); },
    function(value) { return value.toFixed(0) + " deg"; }
);

subPanel.newSlider("Sun: Distance", -180, 180,
    function(value) { Scene.setStageLocation(value, Scene.getStageLocationLatitude(), Scene.getStageLocationAltitude()); },
    function() { return Scene.getStageLocationLongitude(); },
    function(value) { return value.toFixed(0) + " deg"; }
);

var subsub = subPanel.newSubPanel("Hello");

subsub.newSlider("Satellite: Distance", -180, 180,
    function(value) { Scene.setStageLocation(value, Scene.getStageLocationLatitude(), Scene.getStageLocationAltitude()); },
    function() { return Scene.getStageLocationLongitude(); },
    function(value) { return value.toFixed(0) + " deg"; }
);


panel.newSlider("Origin Altitude", 0, 1000,
    function(value) { Scene.setStageLocation(Scene.getStageLocationLongitude(), Scene.getStageLocationLatitude(), value); },
    function() { return Scene.getStageLocationAltitude(); },
    function(value) { return (value).toFixed(0) + " km"; }
);


// for (var i in panel.items) {
//     print(JSON.stringify(panel.items[i]));
//     print("");
// }
//print(JSON.stringify(panel.items));
//print("number of items:" + Object.keys(panel.items).length);


Controller.mouseMoveEvent.connect(function panelMouseMoveEvent(event) { return panel.mouseMoveEvent(event); });
Controller.mousePressEvent.connect( function panelMousePressEvent(event) { return panel.mousePressEvent(event); });
Controller.mouseDoublePressEvent.connect( function panelMouseDoublePressEvent(event) { return panel.mouseDoublePressEvent(event); });
Controller.mouseReleaseEvent.connect(function(event) { return panel.mouseReleaseEvent(event); });

function scriptEnding() {
    Menu.removeMenu("Developer > Scene");
    panel.destroy();
}
Script.scriptEnding.connect(scriptEnding);