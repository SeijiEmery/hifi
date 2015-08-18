//
// cicadas.js
// 
//
// Created by Seiji Emery on 8/14/15
// Copyright 2015 High Fidelity, Inc.
//
// Distributed under the Apache License, Version 2.0.
// See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

Script.include('http://public.highfidelity.io/scripts/libraries/uiwidgets.js');

// Cicadas script
(function () {

var NUM_CICADAS = 20;
var RADIUS = 10.0;
var cicadaTimer = {
	min: 1.0,
	max: 4.0
};
var SOUNDS_URL = "http://public.highfidelity.io/sounds/Animals/cicadas/";

var LOG_ENTITY_CREATION_MESSAGES = false;
var USE_DEBUG_ENTITIES = true;
var USE_AUDIO = true;

// Status / logging UI
(function () {
	var color = function (r, g, b) {
		return { 
			red: parseInt(r, 16),
			green: parseInt(g, 16),
			blue: parseInt(b, 16)
		};
	}
	UI.rgb = function (c) {
		return color(c[1] + c[2], c[3] + c[4], c[5] + c[6]);
	}
	var COLORS = this.COLORS = {
		'GREEN': UI.rgb("#2D870C"),
		'RED': UI.rgb("#AF1E07"),
		'LIGHT_GRAY': UI.rgb("#CCCCCC"),
		'DARK_GRAY': UI.rgb("#4E4E4E")
	};

	var LINE_WIDTH = 400;
	var LINE_HEIGHT = 20;

	var lines = [];
	var lineIndex = 0;
	for (var i = 0; i < 20; ++i) {
		lines.push(new UI.Label({ 
			text: " ", visible: false, 
			width: LINE_WIDTH, height: LINE_HEIGHT,
	 	}));
	}
	var title = new UI.Label({
		text: "cicadas.js", visible: true,
		width: LINE_WIDTH, height: LINE_HEIGHT,
	});

	var overlay = new UI.Box({
		visible: true,
		width: LINE_WIDTH, height: 0,
		backgroundColor: COLORS.DARK_GRAY,
		backgroundAlpha: 0.3
	});
	overlay.setPosition(280, 10);
	relayoutFrom(0);
	UI.updateLayout();

	function relayoutFrom (n) {
		var layoutPos = {
			x: overlay.position.x,
			y: overlay.position.y
		};

		title.setPosition(layoutPos.x, layoutPos.y);
		layoutPos.y += LINE_HEIGHT;

		// for (var i = n; i >= 0; --i) {
		for (var i = n + 1; i < lines.length; ++i) {
			if (lines[i].visible) {
				lines[i].setPosition(layoutPos.x, layoutPos.y);
				layoutPos.y += LINE_HEIGHT;
			}
		}
		// for (var i = lines.length - 1; i > n; --i) {
		for (var i = 0; i <= n; ++i) {
			if (lines[i].visible) {
				lines[i].setPosition(layoutPos.x, layoutPos.y);
				layoutPos.y += LINE_HEIGHT;
			}
		}
		overlay.height = (layoutPos.y - overlay.position.y + 10);
		overlay.getOverlay().update({
			height: overlay.height
		});
	}

	this.logMessage = function (text, color, alpha) {
		lines[lineIndex].setVisible(true);
		relayoutFrom(lineIndex);

		lines[lineIndex].getOverlay().update({
			text: text,
			visible: true,
			color: color || COLORS.LIGHT_GRAY,
			alpha: alpha !== undefined ? alpha : 1.0,
			x: lines[lineIndex].position.x,
			y: lines[lineIndex].position.y
		});
		lineIndex = (lineIndex + 1) % lines.length;
		UI.updateLayout();
	}

	// UI.debug.setVisible(true);
	// this.teardownLog = function () {
	// 	lines.forEach(function (textOverlay) {
	// 		textOverlay.destroy();
	// 	});
	// 	overlay.destroy();
	// }

	var dragStart = null;
	var initialPos = null;
	overlay.addAction('onMouseDown', function (event) {
		dragStart  = { x: event.x, y: event.y };
		initialPos = { x: overlay.position.x, y: overlay.position.y };
	});
	// overlay.addAction('onMouseOver', function (event) {
	// 	overlay.setPosition(overlay.position.x, overlay.position.y + 10);
	// 	relayoutFrom(lineIndex);
	// 	UI.updateLayout();
	// });
	overlay.addAction('onDragBegin', function () {});
	overlay.addAction('onDragUpdate', function (event) {
		print("Dragged");
		overlay.setPosition(
			initialPos.x + event.x - dragStart.x,
			initialPos.y + event.y - dragStart.y);
		relayoutFrom(lineIndex);
		UI.updateLayout();
		// lines.forEach(function(textOverlay) {
		// 	textOverlay.update({
		// 		x: textOverlay.position.x,
		// 		y: textOverlay.position.y
		// 	})
		// })
	});
	overlay.addAction('onMouseUp', function () {
		dragStart = initialPos = null;
	});
})();

// Audio
(function () {
	var CricketAudio = this.CricketAudio = function (position) {
		position = position || MyAvatar.position;

		this.sound = this.getRandom();
		this.position = { x: position.x, y: position.y, z: position.z };
		this.audioInjector = null;
	}
	CricketAudio.prototype.playRandom = function () {
		// if (this.audioInjector && Audio.isInjectorPlaying(this.sound)) {
		if (this.isPlaying()) {
			logMessage("Stopping audio injector to play random");
			// Audio.stopInjector(this.audioInjector);
			this.audioInjector.stop();
		}
		this.sound = this.getRandom();
		this.play();
	}
	CricketAudio.prototype.play = function () {
		if (!this.isPlaying()) {
			if (this.audioInjector) {
				this.audioInjector.stop();
				// Audio.stopInjector(this.audioInjector);
			}
			this.audioInjector = Audio.playSound(this.sound, {
				position: this.position,
				loop: false
			});
		} else {
			logMessage("Called .play() on already running audio injector -- ignoring");
		}
	}
	CricketAudio.prototype.isPlaying = function () {
		return this.audioInjector && this.audioInjector.isPlaying;
	}
	CricketAudio.prototype.destroy = function () {
		if (this.audioInjector) {
			this.audioInjector.stop();
			// Audio.stopInjector(this.audioInjector);
		}
	}
	var cricketSounds = [];
	for (var i = 1; i < 8; ++i) {
		cricketSounds.push(SOUNDS_URL + "cicada" + i + ".wav");
	}
	CricketAudio.prototype.getRandom = function () {
		var n = Math.floor(Math.random() * cricketSounds.length);
		return SoundCache.getSound(cricketSounds[n]);
	}
})();

// UI utils
(function () {
	this.makeDraggable = function(widget, target) {
		target = widget || target;
		if (widget) {
			var dragStart = null;
			var initial   = null;

			widget.addAction('onMouseDown', function () {
				dragStart = { x: event.x, y: event.y };
				initial   = { x: target.position.x, y: target.position.y };
			});
			widget.addAction('onDragUpdate', function (event) {
				target.setPosition(
					initial.x + event.x - dragStart.x,
					initial.y + event.y - dragStart.y
				);
				UI.updateLayout();
			});
			widget.addAction('onMouseUp', function () {
				dragStart = dragEnd = null;
			});
		}
	}
})();


// Controls UI
(function () {
	var layout = new UI.WidgetStack({ dir: '+y' });
})();

// Utils
(function () {
	// Utility function
	this.withDefaults = function (properties, defaults) {
		// logMessage("withDefaults: " + JSON.stringify(properties) + JSON.stringify(defaults));
		properties = properties || {};
		if (defaults) {
			for (var k in defaults) {
				properties[k] = defaults[k];
			}
		}
		return properties;
	}

	// Math utils
	if (typeof(Math.randRange) === 'undefined') {
		Math.randRange = function (min, max) {
			return Math.random() * (max - min) + min;
		}
	}
	if (typeof(Math.randInt) === 'undefined') {
		Math.randInt = function (n) {
			return Math.floor(Math.random() * n) | 0;
		}
	}

	// Get a random point within a circle on the xz plane with radius r.
	this.randomCirclePoint = function (r, pos) {
		var a = Math.random(), b = Math.random();
		if (b < a) {
			var tmp = b;
			b = a;
			a = tmp;
			// b ^= (a ^ (a=b));
		}
		var point = {
			x: pos.x + b * r * Math.cos(2 * Math.PI * a / b),
			y: pos.y,
			z: pos.z + b * r * Math.sin(2 * Math.PI * a / b)
		};
		if (LOG_ENTITY_CREATION_MESSAGES) {
			// logMessage("input params: " + JSON.stringify({ radius: r, position: pos }), COLORS.GREEN);
			// logMessage("a = " + a + ", b = " + b);
			logMessage("generated point: " + JSON.stringify(point), COLORS.RED);
		}
		return point;
	}

	// Entity utils
	var makeEntity = this.makeEntity = function (properties) {
		if (LOG_ENTITY_CREATION_MESSAGES) {
			logMessage("Creating entity: " + JSON.stringify(properties));
		}
		var entity = Entities.addEntity(properties);
		return {
			update: function (properties) {
				Entities.editEntity(entity, properties);
			},
			destroy: function () {
				Entities.deleteEntity(entity)
			}
		};
	}
	this.makeLight = function (properties) {
		return makeEntity(withDefaults(properties, {
			type: "Light",
			isSpotlight: false,
			diffuseColor: { red: 255, green: 100, blue: 100 },
			ambientColor: { red: 200, green: 80, blue: 80 }
		}));
	}
	this.makeBox = function (properties) {
		// logMessage("Creating box: " + JSON.stringify(properties));
		return makeEntity(withDefaults(properties, {
			type: "Box"
		}));
	}
})();

DEFAULT_COLOR = {
	red: 255, green: 200, blue: 200,
	clone: function () {
		return { red: this.red, green: this.green, blue: this.blue };
	}
};

// Cicada class
(function () {
	var Cicada = this.Cicada = function (position) {
		this.position = position;
		this.timer = Math.randRange(cicadaTimer.min, cicadaTimer.max); 

		if (USE_DEBUG_ENTITIES) {
			this.boxColor = DEFAULT_COLOR.clone();
			this.box = makeBox({
				dimensions: { x: 0.1, y: 0.1, z: 0.1 },
				color: this.boxColor,
				position: position
				// x: position.x, y: position.y, z: position.z
			});
		}
		if (USE_AUDIO) {
			this.audio = new CricketAudio();
		}
		// Used to track state changes -- still needed for debug entities even if audio is disabled
		this.playingSound = false;
	}

	var lastUpdate = 0.0;
	Cicada.prototype.update = function (dt) {
		// print("update");
		// logMessage("update", COLORS.GREEN);
		// logMessage("" + this.timer.remaining + " - " + dt);
		// logMessage(" = " + (this.timer.remaining - dt), COLORS.RED);
		// logMessage("fire? " + (this.timer.remaining - dt < 0.0), (this.timer.remaining < dt) ? COLORS.LIGHT_GRAY : COLORS.GREEN);

		if (this.playingSound) {
			if (!USE_AUDIO || !this.audio.isPlaying()) {
				this.playingSound = false;
				if (USE_DEBUG_ENTITIES) {
					this.box.update({
						'color': this.boxColor
					});
				}
			}
			return;
		}

		if ((this.timer -= dt) < 0.0) {
			// print("update");
			// this.fireSound();
			if (USE_DEBUG_ENTITIES) {
				this.boxColor.red   = DEFAULT_COLOR.red;
				this.boxColor.green = DEFAULT_COLOR.green;
				this.boxColor.blue  = DEFAULT_COLOR.blue;
			}
			// logMessage("fire", this.boxColor);
			this.timer = Math.randRange(cicadaTimer.min, cicadaTimer.max);
			this.fireSound();
		} else {
			if (USE_DEBUG_ENTITIES) {
				this.boxColor.red   -= 10.0 * dt;
				this.boxColor.green -= 40.0 * dt;
				this.boxColor.blue  -= 50.0 * dt;
				this.box.update({
					'color': this.boxColor
				});

				// if ((lastUpdate -= dt) < 0.0) {
				// 	logMessage("update", { 
				// 		red: this.boxColor.red,
				// 		green: this.boxColor.green,
				// 		blue: this.boxColor.blue
				// 	});
				// 	lastUpdate = 0.5;
				// }				
			}
		}
	}
	Cicada.prototype.fireSound = function () {
		if (USE_AUDIO) {
			this.playingSound = true;
			this.audio.playRandom();
		}
		if (USE_DEBUG_ENTITIES) {
			// Set color to blue while updating
			this.box.update({
				color: {
					red: 100,
					green: 100,
					blue: 200
				}
			});
		}
	}
	Cicada.prototype.destroy = function () {
		if (this.box) {
			this.box.destroy();
			delete this.box;
		}
		if (this.light) {
			this.light.destroy();
			delete this.light;
		}
		if (this.audio) {
			this.audio.destroy();
		}
	}
})();

// Create cicadas + register update and teardown functions
(function () {
	var cicadas = [];
	this.spawnCicadas = function (n, position) {
		// cicadas.push(new Cicada({ x: 10, y: 10, z: 10 }));
		var avgPos = {
			x: 0.0, y: 0.0, z: 0.0
		};
		for (var i = 0; i < n; ++i) {
			var pt = randomCirclePoint(RADIUS, position);
			avgPos.x += pt.x;
			avgPos.y += pt.y;
			avgPos.z += pt.z;
			cicadas.push(new Cicada(pt));
		}
		avgPos.x /= (cicadas.length ? cicadas.length : 1);
		avgPos.y /= (cicadas.length ? cicadas.length : 1);
		avgPos.z /= (cicadas.length ? cicadas.length : 1);

		logMessage("Spawned " + n + " cicadas (within radius " + RADIUS + ")");
		logMessage("average  position: " + JSON.stringify(avgPos));
		logMessage("MyAvatar position: " + JSON.stringify(MyAvatar.position));
		logMessage("diff: " + JSON.stringify({
			x: MyAvatar.position.x - avgPos.x,
			y: MyAvatar.position.y - avgPos.y,
			z: MyAvatar.position.z - avgPos.z
		}));
	};
	var counter = 0;
	this.update = function (dt) {
		var n = 1;
		if ((counter % n) === 0) {
			// logMessage("Update " + (counter / n));

		}
		++counter;
		cicadas.forEach(function (cicada) {
			cicada.update(dt);
		});
	}
	this.teardown = function () {
		cicadas.forEach(function (cicada) {
			cicada.destroy();
		});
		// teardownLog();
		UI.teardown();
	}
})();

function init () {
	if (Entities.canAdjustLocks() && Entities.canRez()) {
		logMessage("initializing...");
		Script.update.disconnect(init);
		Script.update.connect(update);

		if (USE_DEBUG_ENTITIES) {
			logMessage("using debug entities", COLORS.RED);
		} else {
			logMessage("debug entities disabled", COLORS.RED);
		}
		if (!USE_AUDIO) {
			logMessage("audio disabled", COLORS.RED);
		}
		spawnCicadas(NUM_CICADAS, MyAvatar.position);
		logMessage("finished initializing.", COLORS.GREEN);
	}
}
Script.update.connect(init);
Script.scriptEnding.connect(teardown);

Controller.mousePressEvent.connect(UI.handleMousePress);
Controller.mouseMoveEvent.connect(UI.handleMouseMove);
Controller.mouseReleaseEvent.connect(UI.handleMouseRelease);

})();




