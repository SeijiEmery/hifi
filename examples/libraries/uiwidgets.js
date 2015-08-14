//
//  uiwidgets.js
//  examples/libraries
//
//  Created by Seiji Emery, 8/10/15
//  Copyright 2015 High Fidelity, Inc
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

(function(){
// Module wrapper
var UIWidgets = this.UIWidgets = {};
print("running in uiwidgets.js");
UIWidgets.load = function (_export) {

print("loading in uiwidgets.js");
_export = _export || this;

// Externals
// var _Script     = _export.Script;
// var _Controller = _export.Controller;

// Internal module system for incremental library loading.
// Catches bugs.
var module = {};
var modules = {};
module.add = function (name, body, test) {
    return modules[name] = { load: body, test: test };
}
module.load = function (func) {
    try {
        func.call(this, _export);
    } catch (e) {
        UIWidgets.abortWithError(e);
    }
}
UIWidgets.abortWithError = function (err) {
    modules.Overlays.load(this);

    var viewDimensions = Controller.getViewportDimensions();
    var width  = viewDimensions.x * 0.75;
    var height = viewDimensions.y * 0.75;

    // UI.teardown();
    message = "Script running uiwidgets.js crashed with error:\n" + err;
    var errorDialog = this.makeTextOverlay.call(this, {
        text: message, width: width, height: height,
        backgroundAlpha: 0.5,
        backgroundColor: { red: 10, green: 10, blue: 10 },
        color: { red: 225, green: 10, blue: 10 },
        alpha: 0.9,
        visible: true,
        x: 100,
        y: 100
    });
    Controller.mousePressEvent.connect(function (event) {
        if (Overlays.getOverlayAtPoint({ x: event.x, y: event.y }) == errorDialog.getId()) {
            errorDialog.destroy();
            // errorDialog.destroy();
        }
    });
    Script.scriptEnding.connect(errorDialog.destroy);
    return errorDialog;
}

/// Rect class used for UI layout.
module.add('Rect', function (_export) {
var Rect = _export.Rect = function (xmin, ymin, xmax, ymax) {
    this.x0 = xmin;
    this.y0 = ymin;
    this.x1 = xmax;
    this.y1 = ymax;
}
Rect.prototype.grow = function (pt) {
    this.x0 = Math.min(this.x0, pt.x);
    this.y0 = Math.min(this.y0, pt.y);
    this.x1 = Math.max(this.x1, pt.x);
    this.y1 = Math.max(this.y1, pt.y);
}
Rect.prototype.getWidth = function () {
    return this.x1 - this.x0;
}
Rect.prototype.getHeight = function () {
    return this.y1 - this.y0;
}
Rect.prototype.getTopLeft = function () {
    return { 'x': this.x0, 'y': this.y0 };
}
Rect.prototype.getBtmRight = function () {
    return { 'x': this.x1, 'y': this.y1 };
}
Rect.prototype.getCenter = function () {
    return { 
        'x': 0.5 * (this.x1 + this.x0),
        'y': 0.5 * (this.y1 + this.y0)
    };
}

}); // module Rect


/// Wraps 2d overlays w/ a small abstraction layer
module.add('Overlays', function (_export) {
var makeOverlay = _export.makeOverlay = function (type, properties) {
    var overlay = Overlays.addOverlay(type, properties);
    return {
        'update': function (properties) {
            Overlays.editOverlay(overlay, properties);
        },
        'destroy': function () {
            Overlays.deleteOverlay(overlay);
        },
        'getId': function () {
            return overlay;
        }
    }
}
/// Wraps TextOverlay
_export.makeTextOverlay = function (properties) {
    if (properties && properties.backgroundColor.alpha !== undefined)
        properties.backgroundAlpha = properties.backgroundColor.alpha;
    if (properties && properties.color.alpha !== undefined)
        properties.alpha = properties.color.alpha;
    return makeOverlay.call(this, 'text', properties);
}
/// Wraps ImageOverlay
_export.makeImageOverlay = function (properties) {
    if (properties && properties.color.alpha !== undefined)
        properties.alpha = properties.color.alpha;
    return makeOverlay.call(this, 'image', properties);
}
}); // module OverlayAbstraction


// We actually use this abstraction to implement module error handling

// UIWidgets.abortWithError("foo");

// var __trace = new Array();
// var __traceDepth = 0;

// var assert = function (cond, expr) {
//     if (!cond) {
//         var callstack = "";
//         var maxRecursion = 10;
//         caller = arguments.callee.caller;
//         while (maxRecursion > 0 && caller) {
//             --maxRecursion;
//             callstack += ">> " + caller.toString();
//             caller = caller.caller;
//         }
//         throw new Error("assertion failed: " + expr + " (" + cond + ")" + "\n" +
//             "Called from: " + callstack + " " +
//             "Traceback: \n\t" + __trace.join("\n\t"));
//     }
// }
// var traceEnter = function(fcn) {
//     var l = __trace.length;
//     // print("TRACE ENTER: " + (l+1));
//     s = "";
//     for (var i = 0; i < __traceDepth+1; ++i)
//         s += "-";
//     ++__traceDepth;
//     __trace.push(s + fcn);
//     __trace.push(__trace.pop() + ":" + this);
//     return {
//         'exit': function () {
//             --__traceDepth;
//             // while (__trace.length != l)
//                 // __trace.pop();
//         }
//     };
// }

module.add('UI', function (_exports) {

var Rect = _exports.Rect;
var makeTextOverlay = _exports.makeTextOverlay;
var makeImageOverlay = _exports.makeImageOverlay;

/// UI namespace
var UI = this.UI = {};

var rgb = UI.rgb = function (r, g, b) {
    if (typeof(r) == 'string') {
        rs = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(r);
        if (rs) {
            r = parseInt(rs[0], 16);
            g = parseInt(rs[1], 16);
            b = parseInt(rs[2], 16);
        }
    }
    if (typeof(r) != 'number' || typeof(g) != 'number' || typeof(b) != 'number') {
        ui.err("Invalid args to UI.rgb (" + r + ", " + g + ", " + b + ")");
        return null;
    }
    return { 'red': r, 'green': g, 'blue': b };
}
var rgba = UI.rgba = function (r, g, b, a) {
    if (typeof(r) == 'string')
        return rgb(r);
    return { 'red': r || 0, 'green': g || 0, 'blue': b || 0, 'alpha': a || 1.0 };
}

/// Protected UI state
var ui = {
    defaultVisible: true,
    widgetList: new Array(),
    attachmentList: new Array()
};

ui.complain = function (msg) {
    print("WARNING (uiwidgets.js): " + msg);
}
// ui.errorHandler = function (err) {
//     print(err);
// }
// ui.assert = function (condition, message) {
//     if (!condition) {
//         message = "FAILED ASSERT (uiwidgets.js): " + message || "(" + condition + ")";
//         ui.errorHandler(message);
//         if (typeof(Error) !== 'undefined')
//             throw new Error(message);
//         throw message;
//     }
// }

UI.setDefaultVisibility = function (visible) {
    ui.defaultVisible = visible;
}

/// Wrapper around the overlays impl

function setDefaults(properties, defaults) {
    if (properties === undefined)
        properties = {};
    for (var k in defaults) {
        if (properties[k] === undefined)
            properties[k] = defaults[k];
    }
    return properties;
}
function extractProperties(obj, propertyList, to) {
    to = to || {};
    propertyList.forEach(function (k) {
        to[k] = obj[k];
    });
    return to;
}
function setProperties(obj, properties, propertyList) {
    propertyList.forEach(function (k) {
        obj[k] = properties[k];
    });
}

var COLOR_WHITE = rgb(255, 255, 255);
var COLOR_GRAY  = rgb(125, 125, 125);

/// Base widget class.
var Widget = function () {};

// Shared methods:
var __widgetId = 0;
Widget.prototype.constructor = function (properties) {
    properties = setDefaults.call(this, properties, {
        position: { x: 0.0, y: 0.0 },
        visible: ui.defaultVisible,
        actions: {}
    });

    this.position = properties.position || { x: 0.0, y: 0.0 };
    this.visible = properties.visible || ui.defaultVisible;
    this.actions = properties.actions || {};

    this.dimensions = null;
    this.parentVisible = null;
    this.parent = null;

    // Set readonly id
    Object.defineProperty(this, 'id', {
        value: __widgetId++,
        writable: false
    });
    // Register into global list (used for relayout)
    ui.widgetList.push(this);
}
Widget.prototype.setPosition = function (x, y) {
    if (arguments.length == 1 && typeof(arguments[0]) == 'object') {
        x = arguments[0].x;
        y = arguments[0].y;
    }
    if (typeof(x) != 'number' || typeof(y) != 'number') {
        ui.complain("invalid arguments to " + this + ".setPosition: '" + arguments + "' (expected (x, y) or (vec2))");
    } else {
        this.position.x = x;
        this.position.y = y;
    }
}
Widget.prototype.setVisible = function (visible) {
    this.visible = visible;
    this.parentVisible = null;  // set dirty
}
Widget.prototype.isVisible = function () {
    if (this.parentVisible === null)
        this.parentVisible = this.parent ? this.parent.isVisible() : true;
    return this.visible && this.parentVisible;
}
// Store lists of actions (multiple callbacks per key)
Widget.prototype.addAction = function (action, callback) {
    if (!this.actions[action])
        this.actions[action] = [ callback ];
    else
        this.actions[action].push(callback);
}
Widget.prototype.clearLayout = function () {
    this.dimensions = null;
    this.parentVisible = null;
}
// Overridden methods:
Widget.prototype.toString = function () {
    return "[Widget " + this.id + " ]";
}
Widget.prototype.getOverlay = function () {
    return null;
}
Widget.prototype.getWidth = function () {
    return 0;
}
Widget.prototype.getHeight = function () {
    return 0;
}
Widget.prototype.hasOverlay = function () {
    return false;
}
Widget.prototype.applyLayout = function () {};
Widget.prototype.updateOverlays = function () {};

/// Implements a simple auto-layouted container of methods.
/// @param properties
///     dir: [string]
///         layout direction. 
///         Can be one of [ '+x', '+y', '-x', '-y' ] for 2d directions.
///     border: { x: _, y: _ } 
///         Adds spacing to the widget on all sides (aka. margin). Defaults to 0.
///     padding: { x: _, y: _ }
///         Padding in between each widget. Only one axis is used (the layout direction).
///     visible: true | false
///         Acts as both a widget (logical) property and is used for overlays.
///         Hiding this will hide all child widgets (non-destructively).
///         Do not access this directly -- use setVisible(value) and isVisible() instead.
///     background: [object] 
///         Properties to use for the background overlay (if defined).
///
var WidgetStack = UI.WidgetStack = function (properties) {
    Widget.prototype.constructor.call(this, properties);

    properties = setDefaults.call(this, properties, {
        dir:     '+y',
        border:  { x: 0.0, y: 0.0 },
        padding: { x: 0.0, y: 0.0 },
    });

    var dir = null;
    switch(properties['dir']) {
        case '+y': dir = { 'x': 0.0, 'y': 1.0 }; break;
        case '-y': dir = { 'x': 0.0, 'y': -1.0 }; break;
        case '+x': dir = { 'x': 1.0, 'y': 0.0 }; break;
        case '-x': dir = { 'x': -1.0, 'y': 0.0 }; break;
        default: ui.complain("Unrecognized UI.WidgetStack property 'dir': \"" + dir + "\"");
    }
    this.layoutDir = dir || { 'x': 1.0, 'y': 0.0 };
    this.border = properties.border;
    this.padding = properties.padding;
    this.widgets = new Array();

    var background = properties.background;
    if (background) {
        setDefaults.call(this, background, {
            backgroundColor: COLOR_GRAY,
            textColor: COLOR_WHITE
        });
        background.x = this.position.x;
        background.y = this.position.y;
        background.width = 1;
        background.height = 1;
        background.visible = false;
        this.backgroundOverlay = makeTextOverlay.call(this, background);
    } else {
        this.backgroundOverlay = null;
    }
}
WidgetStack.prototype = new Widget();
WidgetStack.prototype.constructor = WidgetStack;

WidgetStack.prototype.toString = function () {
    return "[WidgetStack " + this.id + " ]";
}

WidgetStack.prototype.add = function (widget) {
    this.widgets.push(widget);
    widget.parent = this;
    return widget;
}
WidgetStack.prototype.hasOverlay = function (overlayId) {
    return this.backgroundOverlay && this.backgroundOverlay.getId() === overlayId;
}
WidgetStack.prototype.getOverlay = function () {
    return this.backgroundOverlay;
}
WidgetStack.prototype.destroy = function () {
    if (this.backgroundOverlay) {
        this.backgroundOverlay.destroy();
        this.backgroundOverlay = null;
    }
}
var sumOf = function (list, f) {
    var sum = 0.0;
    list.forEach(function (elem) {
        sum += f(elem);
    });
    return sum;
}
WidgetStack.prototype.calculateDimensions = function () {
    var totalWidth = 0.0, maxWidth = 0.0;
    var totalHeight = 0.0, maxHeight = 0.0;
    this.widgets.forEach(function (widget) {
        totalWidth += widget.getWidth() + this.padding.x;
        maxWidth = Math.max(maxWidth, widget.getWidth());

        totalHeight += widget.getHeight() + this.padding.y;
        maxHeight = Math.max(maxHeight, widget.getHeight());
    }, this);

    this.dimensions = {
        x: this.border.x * 2 + Math.max(totalWidth * this.layoutDir.x - this.padding.x, maxWidth),
        y: this.border.y * 2 + Math.max(totalHeight * this.layoutDir.y - this.padding.y, maxHeight)
    };
}
WidgetStack.prototype.getWidth = function () {
    if (!this.dimensions)
        this.calculateDimensions();
    return this.dimensions.x;
}
WidgetStack.prototype.getHeight = function () {
    if (!this.dimensions)
        this.calculateDimensions();
    return this.dimensions.y;
}
WidgetStack.prototype.applyLayout = function () {
    var x = this.position.x + this.border.x;
    var y = this.position.y + this.border.y;

    this.widgets.forEach(function (widget) {
        widget.setPosition(x, y);
        x += (widget.getWidth()  + this.padding.x) * this.layoutDir.x;
        y += (widget.getHeight() + this.padding.y) * this.layoutDir.y;
        widget._parentVisible = this.isVisible();
    }, this);
}
WidgetStack.prototype.updateOverlays = function () {
    if (this.backgroundOverlay) {
        this.backgroundOverlay.update({
            width:  this.getWidth(),
            height: this.getHeight(),
            x: this.position.x,
            y: this.position.y,
            visible: this.isVisible()
        });
    }
}

/// GUI Textured Rect
var Image = UI.Image = function (properties) {
    Widget.prototype.constructor.call(this, properties);
    setDefaults.call(this, properties, {
        width: 1.0, height: 1.0,
        color: COLOR_WHITE,
    });
    this.width = properties.width;
    this.height = properties.height;

    properties.visible = this.isVisible();
    properties.x = this.position.x;
    properties.y = this.position.y;

    this.imageOverlay = makeImageOverlay(properties);
}
Image.prototype = new Widget();
Image.prototype.constructor = Image;
Image.prototype.toString = function () {
    return "[UI.Image " + this.id + " ]";
}
Image.prototype.getHeight = function () {
    return this.height;
}
Image.prototype.getWidth = function () {
    return this.width;
}
Image.prototype.hasOverlay = function (overlayId) {
    return this.imageOverlay.getId() === overlayId;
}
Image.prototype.getOverlay = function () {
    return this.imageOverlay;
}
Image.prototype.destroy = function () {
    if (this.imageOverlay) {
        this.imageOverlay.destroy();
        this.imageOverlay = null;
    }
}
Image.prototype.setColor = function (color) {
    if (arguments.length != 1) {
        color = rgba.apply(arguments);
    }
    this.imageOverlay.update({
        'color': color,
        'alpha': color.alpha
    });
}

Image.prototype.getWidth = function () {
    return this.width;
}
Image.prototype.getHeight = function () {
    return this.height;
}
Image.prototype.updateOverlays = function () {
    this.imageOverlay.update({
        width: this.width,
        height: this.height,
        x: this.position.x,
        y: this.position.y,
        visible: this.isVisible()
    });
}


/// GUI Rect. Internally implemented using a text overlay.
var Box = UI.Box = function (properties) {
    Widget.prototype.constructor.call(this, properties);

    properties = setDefaults.call(this, properties, {
        width: 10,
        height: 10
    });
    this.width = properties.width;
    this.height = properties.height;

    properties.x = this.position.x;
    properties.y = this.position.y;
    properties.visible = this.isVisible();

    this.overlay = makeTextOverlay.call(this, properties);
};
Box.prototype = new Widget();
Box.prototype.constructor = Box;
Box.prototype.toString = function () {
    return "[UI.Box " + this.id + " ]";
}
Box.prototype.getWidth = function () {
    return this.width;
}
Box.prototype.getHeight = function () {
    return this.height;
}
Box.prototype.destroy = function () {
    if (this.overlay) { 
        this.overlay.destroy();
        this.overlay = null;
    }
}
Box.prototype.hasOverlay = function (overlayId) {
    return this.overlay && this.overlay.getId() === overlayId;
}
Box.prototype.getOverlay = function () {
    return this.overlay;
}
Box.prototype.updateOverlays = function () {
    this.overlay.update({
        x: this.position.x,
        y: this.position.y,
        width: this.width,
        height: this.height,
        visible: this.isVisible()
    });
}

var Label = UI.Label = function (properties) {
    properties = setDefaults.call(this, properties, {
        text: "", width: 220, height: 20,
        color: COLOR_WHITE
    });
    Box.prototype.constructor.call(this, properties);
};
Label.prototype = new Box();
Label.prototype.constructor = Label;
Label.prototype.toString = function () {
    return "[UI.Label " + this.id + " ]";
}
Label.prototype.setText = function (text) {
    this.text = text;
    this.overlay.update({
        text: text
    });
}

/// Slider widget.
/// @param properties:
///     onValueChanged
var Slider = UI.Slider = function (properties) {
    Box.prototype.constructor.call(this, properties);

    properties = setDefaults.call(this, {
        value: 0.0, maxValue: 1.0, minValue: -1.0,
        padding: { x: 4, y: 4 },
        onValueChanged: function () {},
        slider: {}
    });
    extractProperties(properties, ['value', 'maxValue', 'minValue', 'padding', 'onValueChanged'], this);

    properties.slider.visible = false;
    properties.slider.width  = Math.max(this.width  - this.padding.x, 0.0);
    properties.slider.height = Math.max(this.height - this.padding.y, 0.0);

    this.slider = new Box(properties.slider);
    this.slider.visible = true;
    this.slider.parent = this;
    this.applyLayout();

    // Register slider drag actions
    var widget = this;
    var dragSlider = function (event) {
        var rx = Math.max(event.x * 1.0 - widget.position.x - widget.slider.width * 0.5, 0.0);
        var width = Math.max(widget.width - widget.slider.width - widget.padding.x * 2.0, 0.0);
        var v = Math.min(rx, width) / (width || 1);
        widget.value = widget.minValue + (
            widget.maxValue - widget.minValue) * v;
        widget.onValueChanged(widget.value);
        UI.updateLayout();
    }
    this.addAction('onMouseDown', dragSlider);
    this.addAction('onDrag', dragSlider);
    this.slider.addAction('onMouseDown', dragSlider);
    this.slider.addAction('onDrag', dragSlider);
};
Slider.prototype = new Box();
Slider.prototype.constructor = Slider;

Slider.prototype.toString = function () {
    return "[UI.Slider " + this.id + " ]";
}
Slider.prototype.applyLayout = function () {
    if (!this.slider) {
        ui.complain("Slider.applyLayout on " + this + " failed");
        return;
    }
    var val = (this.value - this.minValue) / (this.maxValue - this.minValue);
    this.slider.position.x = this.position.x + this.padding.x + (this.width - this.slider.width - this.padding.x * 2.0) * val;
    this.slider.position.y = this.position.y + /*this.padding.y +*/ (this.height - this.slider.height) * 0.5;
}
Slider.prototype.getValue = function () {
    return this.value;
}
Slider.prototype.setValue = function (value) {
    this.value = value;
    this.onValueChanged(value);
    UI.updateLayout();
}


var Checkbox = UI.Checkbox = function (properties) {
    Box.prototype.constructor.call(this, properties);

    properties = setDefaults.call(this, properties, {
        checked: true,
        square: true,
        padding: { x: 4, y: 4 },
        checkMark: {}
    });

    setDefaults.call(this, properties.checkMark, {
        backgroundColor: rgba(77, 185, 77, 1.0),
    });
    properties.checkMark.visible = this.checked;
    properties.checkMark.position = {
        x: this.position.x + (this.width - this.checkMark.width) * 0.5,
        y: this.position.y + (this.height - this.checkMark.height) * 0.5
    };
    if (properties.square) { 
        // Constrain inner checkbox to be square (irrespective of outer dimensions)
        var r = Math.min(this.width - this.padding.x * 2.0, this.height - this.padding.y * 2.0);
        properties.checkMark.width = properties.checkMark.height = Math.max(r, 1.0);
    } else {
        // Inner checkbox can be rectangular
        properties.checkMark.width = Math.max(this.width - this.padding.x * 2.0, 1.0);
        properties.checkMark.height = Math.max(this.width - this.padding.y * 2.0, 1.0);
    }
    this.checkMark = new Box(properties.checkMark);
    this.checkMark.parent = this;
    this.onValueChanged = properties.onValueChanged;

    this.addAction('onClick', function (event, widget) {
        widget.setChecked(!widget.isChecked());
    });
    this.checkMark.addAction('onClick', function (event, widget) {
        widget.setChecked(!widget.isChecked());
    });
};
Checkbox.prototype = new Box();
Checkbox.prototype.constructor = Checkbox;
Checkbox.prototype.toString = function () {
    return "[UI.Checkbox " + this.id + "]";
}
Checkbox.prototype.isChecked = function () {
    return this.checked;
}
Checkbox.prototype.setChecked = function (value) {
    this.checked = value;
    this.checkMark.setVisible(this.checked);

    this.onValueChanged(value);
    UI.updateLayout();
}
Checkbox.prototype.applyLayout = function () {
    this.checkMark && this.checkMark.setPosition(
        this.position.x + (this.width - this.checkMark.width) * 0.5,
        this.position.y + (this.height - this.checkMark.height) * 0.5
    );
}

UI.addAttachment = function (target, rel, update) {
    attachment = {
        target: target,
        rel: rel,
        applyLayout: update
    };
    ui.attachmentList.push(attachment);
    return attachment;
}


UI.updateLayout = function () {
    if (ui.visible)
        ui.updateDebugUI();

    // Recalc dimensions
    ui.widgetList.forEach(function (widget) {
        widget.clearLayout();
    });

    function insertAndPush (list, index, elem) {
        if (list[index])
            list[index].push(elem);
        else
            list[index] = [ elem ];
    }

    // Generate attachment lookup
    var attachmentDeps = {};
    ui.attachmentList.forEach(function(attachment) {
        insertAndPush(attachmentDeps, attachment.target.id, {
            dep: attachment.rel,
            eval: attachment.applyLayout
        });
    });
    updated = {};

    // Walk the widget list and relayout everything
    function recalcLayout (widget) {
        // Short circuit if we've already updated
        if (updated[widget.id])
            return;

        // Walk up the tree + update top level first
        if (widget.parent)
            recalcLayout(widget.parent);

        // Resolve and apply attachment dependencies
        if (attachmentDeps[widget.id]) {
            attachmentDeps[widget.id].forEach(function (attachment) {
                recalcLayout(attachment.dep);
                attachment.eval(widget, attachment.dep);
            });
        }

        widget.applyLayout();
        updated[widget.id] = true;
    }
    ui.widgetList.forEach(recalcLayout);

    ui.widgetList.forEach(function (widget) {
        widget.updateOverlays();
    });
}

UI.setDefaultVisibility = function(visibility) {
    ui.defaultVisible = visibility;
};

function dispatchEvent(actions, widget, event) {
    var _TRACE = traceEnter.call(this, "UI.dispatchEvent()");
    actions.forEach(function(action) {
        action.call(widget, event);
    });
    _TRACE.exit();
}

// Debugging ui
var statusPos = { x: 15, y: 20 };
var statusDim = { x: 500, y: 20 };
function makeStatusWidget(defaultText, alpha) {
    var label = new Box({
        text: defaultText,
        width: statusDim.x,
        height: statusDim.y,
        color: COLOR_WHITE,
        alpha: alpha || 0.98,
        backgroundAlpha: 0.0,
        visible: ui.debug.visible
    });
    label.updateText = function (text) {
        label.getOverlay().update({
            text: text
        });
    }
    label.setPosition(statusPos.x, statusPos.y);
    statusPos.y += statusDim.y;
    return label;
}

ui.debug = {};
ui.debug.visible = false;
ui.focusStatus = makeStatusWidget("<UI focus>");
ui.eventStatus = makeStatusWidget("<UI events>", 0.85);

UI.debug = {
    eventList: {
        position: { x: 20, y: 20 }, width: 1, height: 1
    },
    widgetList: {
        position: { x: 500, y: 20 }, width: 1, height: 1
    },
    setVisible: function (visible) {
        if (ui.debug.visible != visible) {
            ui.focusStatus.setVisible(visible);
            ui.eventStatus.setVisible(visible);
            if (visible) {
                ui.debug.showWidgetList(UI.debug.widgetList.position.x, UI.debug.widgetList.position.y);
            } else {
                ui.debug.hideWidgetList();
            }
            UI.updateLayout();
        }
        ui.debug.visible = visible;
    },
    isVisible: function () {
        return ui.debug.visible;
    }
}

// Add debug list of all widgets + attachments
var widgetListHeader = makeStatusWidget("Widgets: ", 0.98);
var widgetList = makeStatusWidget("<widget list>", 0.85);
var attachmentListHeader = makeStatusWidget("Attachments: ", 0.98);
var attachmentList = makeStatusWidget("<attachment list>", 0.85);
var lineHeight = 20;

ui.debug.relayout = function () {
    var x = UI.debug.widgetList.position.x, y = UI.debug.widgetList.position.y;

    widgetListHeader.setPosition(x, y); y += lineHeight;
    widgetList.updateText(ui.widgetList.map(function (widget) {
        return "" + widget + " actions: " + (Object.keys(widget.actions).join(", ") || "none");
    }).join("\n") || "no widgets");
    widgetList.setPosition(x, y);
    y += lineHeight * (ui.widgetList.length || 1);

    attachmentListHeader.setPosition(x, y); y += lineHeight;
    attachmentList.updateText(ui.attachmentList.map(function (attachment) {
        return "[attachment target: " + attachment.target + ", to: " + attachment.rel + "]";
    }).join('\n') || "no attachments");
    attachmentList.setPosition(x, y);
    y += lineHeight * (ui.widgetList.length || 1);
    // UI.updateLayout();
}

var defaultX = 500;
var defaultY = 20;
ui.debug.showWidgetList = function (x, y) {
    widgetListHeader.setVisible(true);
    widgetList.setVisible(true);
    attachmentListHeader.setVisible(true);
    attachmentList.setVisible(true);
    ui.debug.relayout(x || defaultX, y || defaultY);
}
ui.debug.hideWidgetList = function () {
    widgetListHeader.setVisible(false);
    widgetList.setVisible(false);
    attachmentListHeader.setVisible(false);
    attachmentList.setVisible(false);
}

ui.eventStatus.lastPos = { 
    x: ui.eventStatus.position.x, 
    y: ui.eventStatus.position.y 
};
ui.updateDebugUI = function () {
    ui.debug.relayout();

    var dx = ui.eventStatus.position.x - ui.eventStatus.lastPos.x;
    var dy = ui.eventStatus.position.y - ui.eventStatus.lastPos.y;

    ui.focusStatus.position.x += dx;
    ui.focusStatus.position.y += dy;
    ui.eventStatus.position.x += dx;
    ui.eventStatus.position.y += dy;

    ui.eventStatus.lastPos.x = ui.eventStatus.position.x;
    ui.eventStatus.lastPos.y = ui.eventStatus.position.y;
}

var eventList = [];
var maxEvents = 8;

ui.logEvent = function (event) {
    eventList.push(event);
    if (eventList.length >= maxEvents)
        eventList.shift();
    ui.eventStatus.updateText(eventList.join('\n'));
}


// Tries to find a widget with an overlay matching overlay.
// Used by getFocusedWidget(), dispatchEvent(), etc
var getWidgetWithOverlay = function (overlay) {
    var foundWidget = null;
    ui.widgetList.forEach(function(widget) {
        if (widget.hasOverlay(overlay)) {
            foundWidget = widget;
            return;
        }
    });

    ui.focusStatus.updateText("Widget focus: " + foundWidget);
    return foundWidget;
}

var getFocusedWidget = function (event) {
    return getWidgetWithOverlay(Overlays.getOverlayAtPoint({ 'x': event.x, 'y': event.y }));
}

var dispatchEvent = function (action, event, widget) {
    function dispatchActions (actions) {
        actions.forEach(function(action) {
            action(event, widget);
        });
    }

    if (widget.actions[action]) {
        ui.logEvent("Dispatching action '" + action + "'' to " + widget)
        dispatchActions(widget.actions[action]);
    } else {
        for (var parent = widget.parent; parent != null; parent = parent.parent) {
            if (parent.actions[action]) {
                ui.logEvent("Dispatching action '" + action + "'' to parent widget " + widget);
                dispatchActions(parent.actions[action]);
                return;
            }
        }
        ui.logEvent("No action '" + action + "' in " + widget);
    }
}

function handleMouseTransition (focused, event) {
    if (focused != ui.lastFocused) {
        if (ui.lastFocused)
            dispatchEvent('onMouseExit', event, ui.lastFocused);
        if (focused)
            dispatchEvent('onMouseOver', event, focused);
    }
    ui.lastFocused = focused;
}


ui.dragTarget = null;

UI.handleMousePress = function (event) {
    var focused = getFocusedWidget(event);
    handleMouseTransition(focused, event);
    if (focused) {
        dispatchEvent('onMouseDown', event, focused);
    }
    ui.dragTarget = focused && focused.actions['onDrag'] ? focused : null;
}
UI.handleMouseRelease = function (event) {
    var focused = getFocusedWidget(event);
    if (ui.dragTarget) {
        dispatchEvent('onMouseUp', event, ui.dragTarget);
        if (ui.dragTarget == focused) {
            dispatchEvent('onClick', event, ui.dragTarget);
        }
    } 
    handleMouseTransition(focused, event);
    if (!ui.dragTarget) {
        dispatchEvent('onMouseUp', event, focused);
        dispatchEvent('onClick', event, focused);
    }
    ui.dragTarget = null;
}
UI.handleMouseMove = function (event) {
    var focused = getFocusedWidget(event);
    if (ui.dragTarget) {
        dispatchEvent('onDrag', event, ui.dragTarget);
        dispatchEvent('onDrag', event, ui.dragTarget);
    } else {
        handleMouseTransition(focused, event);
    }
}



UI.teardown = function () {
    print("Teardown");
    ui.widgetList.forEach(function(widget) {
        widget.destroy();
    });
    ui.widgetList = [];
    ui.focusedWidget = null;
};
UI.init = function () {
    this.Controller.mousePressEvent.connect(UI.handleMousePress);
    this.Controller.mouseMoveEvent.connect(UI.handleMouseMove);
    this.Controller.mouseReleaseEvent.connect(UI.handleMouseRelease);
    this.Script.scriptEnding.connect(UI.teardown);

    var _Controller = this.Controller;
    var _Overlays = this.Overlays;
    var _Script = this.Script;
    this.Script.errorMessage.connect(function (message) {
        var viewDimensions = _Controller.getViewportDimensions();
        var width  = viewDimensions.x * 0.75;
        var height = viewDimensions.y * 0.75;

        // UI.teardown();
        message = "Script running uiwidgets.js crashed with error:\n" + message;
        var errorDialog = _Overlays.create('text', {
            text: message, width: width, height: height,
            backgroundAlpha: 0.5,
            backgroundColor: rgb(200, 200, 200),
            color: rgb(255, 100, 100),
            alpha: 0.9,
            visible: true,
            x: 100,
            y: 100
            // x: (viewDimensions.x - width) * 0.5, 
            // y: (viewDimensions.y - height) * 0.5
        });
        _Controller.mousePressEvent.connect(function (event) {
            if (_Overlays.getOverlayAtPoint({ x: event.x, y: event.y }) == errorDialog/*.getId()*/) {
                _Overlays.deleteOverlay(errorDialog);
                // errorDialog.destroy();
            }
        });
        _Script.stop();
    });
}

UI.setErrorHandler = function (errorHandler) {
    if (typeof(errorHandler) !== 'function') {
        ui.complain("UI.setErrorHandler -- invalid argument: \"" + errorHandler + "\"");
    } else {
        ui.errorHandler = errorHandler;
    }
}

UI.printWidgets = function () {
    print("widgetlist.length = " + ui.widgetList.length);
    ui.widgetList.forEach(function(widget) {
        print(""+widget + " position=(" + widget.position.x + ", " + widget.position.y + ")" + 
            " parent = " + widget.parent + " visible = " + widget.isVisible() + 
            " width = " + widget.getWidth() + ", height = " + widget.getHeight() +
            " overlay = " + (widget.getOverlay() && widget.getOverlay().getId()) +
            (widget.border ? " border = " + widget.border.x + ", " + widget.border.y : "") + 
            (widget.padding ? " padding = " + widget.padding.x + ", " + widget.padding.y : ""));
    });
}

});

modules.Rect.load.call(this, _export);
modules.Overlays.load.call(this, _export);
modules.UI.load.call(this, _export);

// Register events
// Controller.mousePressEvent.connect(UI.handleMousePress);
// Controller.mouseMoveEvent.connect(UI.handleMouseMove);
// Controller.mouseReleaseEvent.connect(UI.handleMouseRelease);
};

})();


