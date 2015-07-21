//
//  cookies.js
//
//  version 2.0
//
//  Created by Sam Gateau, 4/1/2015
//  A simple ui panel that present a list of porperties and the proper widget to edit it
//  
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//
// The Slider class
(function () {
    var Slider = function(x,y,width,thumbSize) {
        this.background = Overlays.addOverlay("text", {
                        backgroundColor: { red: 200, green: 200, blue: 255 },
                        x: x,
                        y: y,
                        width: width,
                        height: thumbSize,
                        alpha: 1.0,
                        backgroundAlpha: 0.5,
                        visible: true
                    });
        this.thumb = Overlays.addOverlay("text", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        x: x,
                        y: y,
                        width: thumbSize,
                        height: thumbSize,
                        alpha: 1.0,
                        backgroundAlpha: 1.0,
                        visible: true
                    });
    
    
        this.thumbSize = thumbSize;
        this.thumbHalfSize = 0.5 * thumbSize;
    
        this.minThumbX = x + this.thumbHalfSize;
        this.maxThumbX = x + width - this.thumbHalfSize;
        this.thumbX = this.minThumbX;
    
        this.minValue = 0.0;
        this.maxValue = 1.0;
    
        this.clickOffsetX = 0;
        this.isMoving = false;
    };
    
    Slider.prototype.updateThumb = function() { 
            var thumbTruePos = this.thumbX - 0.5 * this.thumbSize;
            Overlays.editOverlay(this.thumb, { x: thumbTruePos } );
        };
    
    Slider.prototype.isClickableOverlayItem = function(item) {
            return (item == this.thumb) || (item == this.background);
        };
    
    Slider.prototype.onMouseMoveEvent = function(event) { 
            if (this.isMoving) {
                var newThumbX = event.x - this.clickOffsetX;
                if (newThumbX < this.minThumbX) {
                    newThumbX = this.minThumbX;
                }
                if (newThumbX > this.maxThumbX) {
                    newThumbX = this.maxThumbX;
                }
                this.thumbX = newThumbX;
                this.updateThumb();
                this.onValueChanged(this.getValue());
            }
        };
    
    Slider.prototype.onMousePressEvent = function(event, clickedOverlay) {
            if (!this.isClickableOverlayItem(clickedOverlay)) {
                this.isMoving = false;
                return;
            }
            this.isMoving = true;
            var clickOffset = event.x - this.thumbX;
            if ((clickOffset > -this.thumbHalfSize) && (clickOffset < this.thumbHalfSize)) {
                this.clickOffsetX = clickOffset;
            } else {
                this.clickOffsetX = 0;
                this.thumbX = event.x;
                this.updateThumb();
                this.onValueChanged(this.getValue());
            }
    
        };
    
    Slider.prototype.onMouseReleaseEvent = function(event) {
            this.isMoving = false;
        };
    
        // Public members:
    Slider.prototype.setNormalizedValue = function(value) {
            if (value < 0.0) {
                this.thumbX = this.minThumbX;
            } else if (value > 1.0) {
                this.thumbX = this.maxThumbX;
            } else {
                this.thumbX = value * (this.maxThumbX - this.minThumbX) + this.minThumbX;
            }
            this.updateThumb();
        };
    Slider.prototype.getNormalizedValue = function() {
            return (this.thumbX - this.minThumbX) / (this.maxThumbX - this.minThumbX);
        };
    
    Slider.prototype.setValue = function(value) {
            var normValue = (value - this.minValue) / (this.maxValue - this.minValue);
            this.setNormalizedValue(normValue);
        };
    
    Slider.prototype.reset = function(resetValue) {
            this.setValue(resetValue);
            this.onValueChanged(resetValue);
        };
    
    Slider.prototype.getValue = function() {
            return this.getNormalizedValue() * (this.maxValue - this.minValue) + this.minValue;
        };
    
    Slider.prototype.getHeight = function() {
            return 1.5 * this.thumbSize;
        };
    
    Slider.prototype.onValueChanged = function(value) {};
    
    Slider.prototype.destroy = function() {
            Overlays.deleteOverlay(this.background);
            Overlays.deleteOverlay(this.thumb);
        };
    
    Slider.prototype.setThumbColor = function(color) {
            Overlays.editOverlay(this.thumb, {backgroundColor: { red: color.x*255, green: color.y*255, blue: color.z*255 }});
        };
    Slider.prototype.setBackgroundColor = function(color) {
            Overlays.editOverlay(this.background, {backgroundColor: { red: color.x*255, green: color.y*255, blue: color.z*255 }});
        };
    this.Slider = Slider;
    
    // The Checkbox class
    var Checkbox = function(x,y,width,thumbSize) {
    
        this.background = Overlays.addOverlay("text", {
                        backgroundColor: { red: 125, green: 125, blue: 255 },
                        x: x,
                        y: y,
                        width: width,
                        height: thumbSize,
                        alpha: 1.0,
                        backgroundAlpha: 0.5,
                        visible: true
                    });
    
        this.thumb = Overlays.addOverlay("text", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        textFontSize: 10,
                        x: x,
                        y: y,
                        width: thumbSize,
                        height: thumbSize,
                        alpha: 1.0,
                        backgroundAlpha: 1.0,
                        visible: true
                    });
    
    
        this.thumbSize = thumbSize;
        var checkX = x + (0.25 * thumbSize);
        var checkY = y + (0.25 * thumbSize);
        this.boxCheckStatus = false;
        this.clickedBox = false;
    
        
        this.checkMark = Overlays.addOverlay("text", {
                        backgroundColor: { red: 0, green: 255, blue: 0 },
                        x: checkX,
                        y: checkY,
                        width: thumbSize / 2.0,
                        height: thumbSize / 2.0,
                        alpha: 1.0,
                        visible: true
                    });
    
        this.unCheckMark = Overlays.addOverlay("image", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        x: checkX + 1.0,
                        y: checkY + 1.0,
                        width: thumbSize / 2.5,
                        height: thumbSize / 2.5,
                        alpha: 1.0,
                        visible: !this.boxCheckStatus
                    });
    };
    
    Checkbox.prototype.updateThumb = function() { 
            if(!this.clickedBox) {
                return;
            }  
            if (this.boxCheckStatus) {
                Overlays.editOverlay(this.unCheckMark, { visible: false });
            } else {
                Overlays.editOverlay(this.unCheckMark, { visible: true });
            }
            
        };
    
    Checkbox.prototype.isClickableOverlayItem = function(item) {
            return (item == this.thumb) || (item == this.checkMark) || (item == this.unCheckMark);
        };
        
    Checkbox.prototype.onMousePressEvent = function(event, clickedOverlay) {
            if (!this.isClickableOverlayItem(clickedOverlay)) {
                this.isMoving = false;
                this.clickedBox = false;
                return;
            }
    
            this.setValue(!this.getValue());
            this.clickedBox = true;  
        };
    
    
    Checkbox.prototype.onMouseReleaseEvent = function(event) {
            this.clickedBox = false;
        };
    
    
        // Public members:
    Checkbox.prototype.setNormalizedValue = function(value) {
            this.boxCheckStatus = value;
            this.onValueChanged(this.getValue());
            this.updateThumb();
        };
    
    Checkbox.prototype.getNormalizedValue = function() {
            return this.boxCheckStatus; 
        };
    
    Checkbox.prototype.setValue = function(value) {
            this.setNormalizedValue(value);
        };
    
    Checkbox.prototype.reset = function(resetValue) {
            this.setValue(resetValue);
        };
    
    Checkbox.prototype.getValue = function() {
            return this.boxCheckStatus;
        };
    
    Checkbox.prototype.getHeight = function() {
            return 1.5 * this.thumbSize;
        };
    
    Checkbox.prototype.setterFromWidget = function(value) {
            var status = this.boxCheckStatus;
            this.onValueChanged(this.boxCheckStatus);
            this.updateThumb();
        };
    
    Checkbox.prototype.onValueChanged = function(value) {};
    
    Checkbox.prototype.destroy = function() {
            Overlays.deleteOverlay(this.background);
            Overlays.deleteOverlay(this.thumb);
            Overlays.deleteOverlay(checkMark);
            Overlays.deleteOverlay(unCheckMark);
        };
    
    Checkbox.prototype.setThumbColor = function(color) {
            Overlays.editOverlay(this.thumb, { red: 255, green: 255, blue: 255 } );
        };
    Checkbox.prototype.setBackgroundColor = function(color) {
            Overlays.editOverlay(this.background, { red: 125, green: 125, blue: 255  });
        };
    this.Checkbox = Checkbox;
    
    // The ColorBox class
    var ColorBox = function(x,y,width,thumbSize) {
        var self = this;
        
        var slideHeight = thumbSize / 3;
        var sliderWidth = width;
        this.red = new Slider(x, y, width, slideHeight);
        this.green = new Slider(x, y + slideHeight, width, slideHeight);
        this.blue = new Slider(x, y + 2 * slideHeight, width, slideHeight);
        this.red.setBackgroundColor({x: 1, y: 0, z: 0});
        this.green.setBackgroundColor({x: 0, y: 1, z: 0});
        this.blue.setBackgroundColor({x: 0, y: 0, z: 1});
        
        this.red.onValueChanged = this.setterFromWidget;
        this.green.onValueChanged = this.setterFromWidget;
        this.blue.onValueChanged = this.setterFromWidget;
    };
    
    ColorBox.prototype.isClickableOverlayItem = function(item) {
            return this.red.isClickableOverlayItem(item) 
                || this.green.isClickableOverlayItem(item)
                || this.blue.isClickableOverlayItem(item);
        };
    
    ColorBox.prototype.onMouseMoveEvent = function(event) { 
            this.red.onMouseMoveEvent(event);
            this.green.onMouseMoveEvent(event);
            this.blue.onMouseMoveEvent(event);
        };
    
    ColorBox.prototype.onMousePressEvent = function(event, clickedOverlay) {
            this.red.onMousePressEvent(event, clickedOverlay);
            if (this.red.isMoving) {
                return;
            }
    
            this.green.onMousePressEvent(event, clickedOverlay);
            if (this.green.isMoving) {
                return;
            }
            
            this.blue.onMousePressEvent(event, clickedOverlay);
        };
    
    
    ColorBox.prototype.onMouseReleaseEvent = function(event) {
            this.red.onMouseReleaseEvent(event);
            this.green.onMouseReleaseEvent(event);
            this.blue.onMouseReleaseEvent(event);
        };
    
    ColorBox.prototype.setterFromWidget = function(value) {
            var color = this.getValue();
            this.onValueChanged(color);
            this.updateRGBSliders(color);
        };
    
    ColorBox.prototype.updateRGBSliders = function(color) {
            this.red.setThumbColor({x: color.x, y: 0, z: 0});
            this.green.setThumbColor({x: 0, y: color.y, z: 0});
            this.blue.setThumbColor({x: 0, y: 0, z: color.z});
        };
    
        // Public members:
    ColorBox.prototype.setValue = function(value) {
            this.red.setValue(value.x);
            this.green.setValue(value.y);
            this.blue.setValue(value.z);
            this.updateRGBSliders(value);  
        };
    
    ColorBox.prototype.reset = function(resetValue) {
            this.setValue(resetValue);
            this.onValueChanged(resetValue);
        };
    
    ColorBox.prototype.getValue = function() {
            var value = {x:this.red.getValue(), y:this.green.getValue(),z:this.blue.getValue()};
            return value;
        };
    
    ColorBox.prototype.getHeight = function() {
            return 1.5 * this.thumbSize;
        };
    
    ColorBox.prototype.destroy = function() {
            this.red.destroy();
            this.green.destroy();
            this.blue.destroy();
        };
    
    ColorBox.prototype.onValueChanged = function(value) {};
    this.ColorBox = ColorBox;
    
    // The DirectionBox class
    var DirectionBox = function(x,y,width,thumbSize) {
        var self = this;
        
        var slideHeight = thumbSize / 2;
        var sliderWidth = width;
        this.yaw = new Slider(x, y, width, slideHeight);
        this.pitch = new Slider(x, y + slideHeight, width, slideHeight);
    
       
        
        this.yaw.setThumbColor({x: 1, y: 0, z: 0});
        this.yaw.minValue = -180;
        this.yaw.maxValue = +180;
    
        this.pitch.setThumbColor({x: 0, y: 0, z: 1});
        this.pitch.minValue = -1;
        this.pitch.maxValue = +1;
        
        this.yaw.onValueChanged = this.setterFromWidget;
        this.pitch.onValueChanged = this.setterFromWidget;
    };
    
    DirectionBox.prototype.isClickableOverlayItem = function(item) {
            return this.yaw.isClickableOverlayItem(item) 
                || this.pitch.isClickableOverlayItem(item);
        };
    
    DirectionBox.prototype.onMouseMoveEvent = function(event) { 
            this.yaw.onMouseMoveEvent(event);
            this.pitch.onMouseMoveEvent(event);
        };
    
    DirectionBox.prototype.onMousePressEvent = function(event, clickedOverlay) {
            this.yaw.onMousePressEvent(event, clickedOverlay);
            if (this.yaw.isMoving) {
                return;
            }
            this.pitch.onMousePressEvent(event, clickedOverlay);
        };
    
    DirectionBox.prototype.onMouseReleaseEvent = function(event) {
            this.yaw.onMouseReleaseEvent(event);
            this.pitch.onMouseReleaseEvent(event);
        };
    
    DirectionBox.prototype.setterFromWidget = function(value) {
            var yawPitch = this.getValue();
			this.onValueChanged(yawPitch);
        };
    
        // Public members:
    DirectionBox.prototype.setValue = function(direction) {
            var flatXZ = Math.sqrt(direction.x * direction.x + direction.z * direction.z);
            if (flatXZ > 0.0) {
                var flatX = direction.x / flatXZ;
                var flatZ = direction.z / flatXZ;
                var yaw = Math.acos(flatX) * 180 / Math.PI;
                if (flatZ < 0) {
                    yaw = -yaw;
                }
                this.yaw.setValue(yaw);
            }
            this.pitch.setValue(direction.y);
        };
    
    DirectionBox.prototype.reset = function(resetValue) {
            this.setValue(resetValue);
            this.onValueChanged(resetValue);
        };
    
    DirectionBox.prototype.getValue = function() {
            var dirZ = this.pitch.getValue();
            var yaw = this.yaw.getValue() * Math.PI / 180;
            var cosY = Math.sqrt(1 - dirZ*dirZ);
            var value = {x:cosY * Math.cos(yaw), y:dirZ, z: cosY * Math.sin(yaw)};
            return value;
        };
    
    DirectionBox.prototype.getHeight = function() {
            return 1.5 * this.thumbSize;
        };
    
    DirectionBox.prototype.destroy = function() {
            this.yaw.destroy();
            this.pitch.destroy();
        };
    
    DirectionBox.prototype.onValueChanged = function(value) {};
    this.DirectionBox = DirectionBox;
    
    var textFontSize = 12;
    
    // TODO: Make collapsable
    var CollapsablePanelItem = function (name, x, y, textWidth, height) {
        this.name = name;
        this.height = height;
    
        var topMargin = (height - textFontSize);
    
        this.thumb = Overlays.addOverlay("text", {
                        backgroundColor: { red: 220, green: 220, blue: 220 },
                        textFontSize: 10,
                        x: x,
                        y: y,
                        width: rawHeight,
                        height: rawHeight,
                        alpha: 1.0,
                        backgroundAlpha: 1.0,
                        visible: true
                    });
        
        this.title = Overlays.addOverlay("text", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        x: x + rawHeight,
                        y: y,
                        width: textWidth,
                        height: height,
                        alpha: 1.0,
                        backgroundAlpha: 0.5,
                        visible: true,
                        text: name,
                        font: {size: textFontSize},
                        topMargin: topMargin 
                    });
    };
    
    CollapsablePanelItem.prototype.destroy = function() {
        Overlays.deleteOverlay(this.title);
        Overlays.deleteOverlay(this.thumb);
        if (this.widget != null) {
            this.widget.destroy();
        }
    };
    this.CollapsablePanelItem = CollapsablePanelItem;
    
    var PanelItem = function (name, setter, getter, displayer, x, y, textWidth, valueWidth, height) {
        //print("creating panel item: " + name);
        
        this.name = name;
    
        this.displayer = typeof displayer !== 'undefined' ? displayer : function(value) { 
            if(value == true) { 
                return "On";
            } else if (value == false) {
                return "Off";
            }
            return value.toFixed(2); 
        };
    
        var topMargin = (height - textFontSize);
        this.title = Overlays.addOverlay("text", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        x: x,
                        y: y,
                        width: textWidth,
                        height: height,
                        alpha: 1.0,
                        backgroundAlpha: 0.5,
                        visible: true,
                        text: name,
                        font: {size: textFontSize},
                        topMargin: topMargin
                    });
    
        this.value = Overlays.addOverlay("text", {
                        backgroundColor: { red: 255, green: 255, blue: 255 },
                        x: x + textWidth,
                        y: y,
                        width: valueWidth,
                        height: height,
                        alpha: 1.0,
                        backgroundAlpha: 0.5,
                        visible: true,
                        text: this.displayer(getter()),
                        font: {size: textFontSize},
                        topMargin: topMargin
                    });
    
        this.getter = getter;
        this.resetValue = getter();
    
    	this.setter = function(value) {
            
            setter(value);
    
            Overlays.editOverlay(this.value, {text: this.displayer(getter())});
    
            if (this.widget) {
                this.widget.setValue(value);
            } 
    
            //print("successfully set value of widget to " + value);
        };
    	this.setterFromWidget = function(value) {
            setter(value);
            // ANd loop back the value after the final setter has been called
            value = getter();
    
            if (this.widget) {
                this.widget.setValue(value);
            }        
            Overlays.editOverlay(this.value, {text: this.displayer(value)});    
        };   
        this.widget = null;
    };
    
    PanelItem.prototype.destroy = function() {
            Overlays.deleteOverlay(this.title);
            Overlays.deleteOverlay(this.value);
            if (this.widget != null) {
                this.widget.destroy();
            }
        };
    this.PanelItem = PanelItem;
    
    var textWidth = 180;
    var valueWidth = 100;
    var widgetWidth = 300;
    var rawHeight = 20;
    var rawYDelta = rawHeight * 1.5;
    
    var Panel = function(x, y) {
    
        this.x = x;
        this.y = y;
        this.nextY = y;
    
        this.widgetX = x + textWidth + valueWidth; 
    
        this.items = new Array();
        this.activeWidget = null;
        var indentation = 30;
    };
    
    Panel.prototype.mouseMoveEvent = function(event) {
        if (this.activeWidget) {
            this.activeWidget.onMouseMoveEvent(event);
        }
    };
    
    Panel.prototype.mousePressEvent = function(event) {
        // Make sure we quitted previous widget
        if (this.activeWidget) {
            this.activeWidget.onMouseReleaseEvent(event);
        }
        this.activeWidget = null; 
    
        var clickedOverlay = Overlays.getOverlayAtPoint({x: event.x, y: event.y});
    
        // If the user clicked any of the slider background then...
        for (var i in this.items) {
            var widget = this.items[i].widget;
    
            if (widget.isClickableOverlayItem(clickedOverlay)) {
                this.activeWidget = widget;
                this.activeWidget.onMousePressEvent(event, clickedOverlay);        
              
                break;
            }    
        }  
    };
    
        // Reset panel item upon double-clicking
    Panel.prototype.mouseDoublePressEvent = function(event) {
    
        var clickedOverlay = Overlays.getOverlayAtPoint({x: event.x, y: event.y});
        // for (var i in this.items) {
    
        //     var item = this.items[i]; 
        //     var widget = item.widget;
            
        //     if (clickedOverlay == item.title) {
        //         item.activeWidget = widget;
        
        //         item.activeWidget.reset(item.resetValue);
            
        //         break;
        //     }    
        // }  
    }
    
    Panel.prototype.handleReset = function (overlay) {
        for (var i in this.items) {
    
            var item = this.items[i]; 
            var widget = item.widget;
    
            if (item.isSubPanel && widget) {
                widget.handleReset(overlay);
            }
            
            if (overlay == item.title) {
                item.activeWidget = widget;
    
                item.activeWidget.reset(item.resetValue);
            
                break;
            }    
        }
    };
    
    
    
    Panel.prototype.mouseReleaseEvent = function(event) {
        if (this.activeWidget) {
            this.activeWidget.onMouseReleaseEvent(event);
        }
        this.activeWidget = null;
    };
    
    Panel.prototype.onMousePressEvent = function(event, clickedOverlay) {
        for (var i in this.items) {
            var item = this.items[i];
            if(item.widget.isClickableOverlayItem(clickedOverlay)) {
                item.activeWidget = item.widget;
                item.activeWidget.onMousePressEvent(event,clickedOverlay);
            }
        }
    };
    
    Panel.prototype.reset = function(event) {
        for (var i in this.items) {
            var item = this.items[i];
            if (item.activeWidget) {
                item.activeWidget.reset(item.resetValue); 
            }
        }
    };
    
    Panel.prototype.onMouseMoveEvent = function(event) {
        for (var i in this.items) {
            var item = this.items[i];
            if (item.activeWidget) {
                item.activeWidget.onMouseMoveEvent(event);
            }
        }
    };
    
    Panel.prototype.onMouseReleaseEvent = function(event, clickedOverlay) {
        for (var i in this.items) {
            var item = this.items[i];
            if (item.activeWidget) {
                item.activeWidget.onMouseReleaseEvent(event);
            }
            item.activeWidget = null;
        }
    };
    
    Panel.prototype.onMouseDoublePressEvent = function(event, clickedOverlay) {
        for (var i in this.items) {
            var item = this.items[i];
            if (item.activeWidget) {
                item.activeWidget.onMouseDoublePressEvent(event);
            }
        }
    };
    
    Panel.prototype.newSlider = function(name, minValue, maxValue, setValue, getValue, displayValue) {
        this.nextY = this.y + this.getHeight();
        var item = new PanelItem(name, setValue, getValue, displayValue, this.x, this.nextY, textWidth, valueWidth, rawHeight);
    
        var slider = new Slider(this.widgetX, this.nextY, widgetWidth, rawHeight);
        slider.minValue = minValue;
        slider.maxValue = maxValue;
    
        item.widget = slider;
        item.widget.onValueChanged = function(value) { item.setterFromWidget(value); };
        item.setter(getValue());      
        this.items[name] = item;
        this.nextY += rawYDelta; 
    };
    
    Panel.prototype.newCheckbox = function(name, setValue, getValue, displayValue) {
        var display;
        if (displayValue == true) {
            display = function() {return "On";};
        } else if (displayValue == false) {
            display = function() {return "Off";};
        }
    
        this.nextY = this.y + this.getHeight();
    
        var item = new PanelItem(name, setValue, getValue, display, this.x, this.nextY, textWidth, valueWidth, rawHeight);
    
        var checkbox = new Checkbox(this.widgetX, this.nextY, widgetWidth, rawHeight);
    
        item.widget = checkbox;
        item.widget.onValueChanged = function(value) { item.setterFromWidget(value); };
        item.setter(getValue()); 
        this.items[name] = item;
        
        //print("created Item... checkbox=" + name);     
    };
    
    Panel.prototype.newColorBox = function(name, setValue, getValue, displayValue) {
        this.nextY = this.y + this.getHeight();
    
        var item = new PanelItem(name, setValue, getValue, displayValue, this.x, this.nextY, textWidth, valueWidth, rawHeight);
    
        var colorBox = new ColorBox(this.widgetX, this.nextY, widgetWidth, rawHeight);
    
        item.widget = colorBox;
        item.widget.onValueChanged = function(value) { item.setterFromWidget(value); };
        item.setter(getValue());      
        this.items[name] = item;
        this.nextY += rawYDelta;
      //  print("created Item... colorBox=" + name);     
    };
    
    Panel.prototype.newDirectionBox = function(name, setValue, getValue, displayValue) {
        this.nextY = this.y + this.getHeight();
    
        var item = new PanelItem(name, setValue, getValue, displayValue, this.x, this.nextY, textWidth, valueWidth, rawHeight);
    
        var directionBox = new DirectionBox(this.widgetX, this.nextY, widgetWidth, rawHeight);
    
        item.widget = directionBox;
        item.widget.onValueChanged = function(value) { item.setterFromWidget(value); };
        item.setter(getValue());      
        this.items[name] = item;
        this.nextY += rawYDelta;
      //  print("created Item... directionBox=" + name);     
    };
    
        
    
    Panel.prototype.newSubPanel = function(name) {
        //TODO: make collapsable, fix double-press event
        this.nextY = this.y + this.getHeight();
    
        var item = new CollapsablePanelItem(name, this.x, this.nextY, textWidth, rawHeight, panel);
        item.isSubPanel = true;
    
         this.nextY += 1.5 * item.height;
    
        var subPanel = new Panel(this.x + this.indentation, this.nextY);
    
        item.widget = subPanel;
        this.items[name] = item;
        return subPanel;
    //    print("created Item... subPanel=" + name);
    };
    
    Panel.prototype.onValueChanged = function(value) {
        for (var i in this.items) {
            this.items[i].widget.onValueChanged(value);
        }
    };
    
    Panel.prototype.destroy = function() {
        for (var i in this.items) {
            this.items[i].destroy();  
        } 
    };
    Panel.prototype.set = function(name, value) {
        var item = this.items[name];
        if (item != null) {
            return item.setter(value);
        }
        return null;
    };
    
    Panel.prototype.get = function(name) {
        var item = this.items[name];
        if (item != null) {
            return item.getter();
        }
        return null;
    };
    
    Panel.prototype.update = function(name) {
        var item = this.items[name];
        if (item != null) {
            return item.setter(item.getter());
        }
        return null;
    };
    
    Panel.prototype.isClickableOverlayItem = function(item) {
        for (var i in this.items) {
            if (this.items[i].widget.isClickableOverlayItem(item)) {
                return true;
            }
        }
        return false;
    };
    
    Panel.prototype.getHeight = function() {
        var height = 0;
    
        for (var i in this.items) {
            height += this.items[i].widget.getHeight(); 
            if(this.items[i].isSubPanel) {
                height += 1.5 * rawHeight;
            } 
        }
    
        return height;
    };
    this.Panel = Panel;
})();


