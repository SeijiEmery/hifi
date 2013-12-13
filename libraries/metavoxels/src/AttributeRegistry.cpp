//
//  AttributeRegistry.cpp
//  metavoxels
//
//  Created by Andrzej Kapolka on 12/6/13.
//  Copyright (c) 2013 High Fidelity, Inc. All rights reserved.
//

#include "AttributeRegistry.h"

AttributeRegistry AttributeRegistry::_instance;

AttributeRegistry::AttributeRegistry() :
    _colorAttribute(registerAttribute(new QRgbAttribute("color"))),
    _normalAttribute(registerAttribute(new QRgbAttribute("normal", qRgb(0, 127, 0)))),
    _voxelizerAttribute(registerAttribute(new PointerAttribute<bool>("voxelizer", false))) {
}

AttributePointer AttributeRegistry::registerAttribute(AttributePointer attribute) {
    AttributePointer& pointer = _attributes[attribute->getName()];
    if (!pointer) {
        pointer = attribute;
    }
    return pointer;
}

AttributeValue::AttributeValue(const AttributePointer& attribute) :
    _attribute(attribute), _value(attribute ? attribute->getDefaultValue() : NULL) {
}

AttributeValue::AttributeValue(const AttributePointer& attribute, void* value) :
    _attribute(attribute), _value(value) {
}

void* AttributeValue::copy() const {
    return _attribute->create(_value);
}

bool AttributeValue::isDefault() const {
    return !_attribute || _attribute->equal(_value, _attribute->getDefaultValue());
}

bool AttributeValue::operator==(const AttributeValue& other) const {
    return _attribute == other._attribute && (!_attribute || _attribute->equal(_value, other._value));
}

bool AttributeValue::operator==(void* other) const {
    return _attribute && _attribute->equal(_value, other);
}

OwnedAttributeValue::OwnedAttributeValue(const AttributePointer& attribute) :
    AttributeValue(attribute, attribute ? attribute->create() : NULL) {
}

OwnedAttributeValue::OwnedAttributeValue(const AttributePointer& attribute, void* value) :
    AttributeValue(attribute, attribute ? attribute->create(value) : NULL) {
}

OwnedAttributeValue::OwnedAttributeValue(const AttributeValue& other) :
    AttributeValue(other.getAttribute(), other.getAttribute() ? other.copy() : NULL) {
}

OwnedAttributeValue::~OwnedAttributeValue() {
    if (_attribute) {
        _attribute->destroy(_value);
    }
}

OwnedAttributeValue& OwnedAttributeValue::operator=(const AttributeValue& other) {
    if (_attribute) {
        _attribute->destroy(_value);
    }
    if ((_attribute = other.getAttribute())) {
        _value = _attribute->create(other.getValue());
    }
}

Attribute::Attribute(const QString& name) : _name(name) {
}

Attribute::~Attribute() {
}

QRgbAttribute::QRgbAttribute(const QString& name, QRgb defaultValue) :
    InlineAttribute<QRgb, 32>(name, defaultValue) {
}
 
void* QRgbAttribute::createAveraged(void* values[]) const {
    int totalRed = 0;
    int totalGreen = 0;
    int totalBlue = 0;
    int totalAlpha = 0;
    for (int i = 0; i < AVERAGE_COUNT; i++) {
        QRgb value = decodeInline<QRgb>(values[i]);
        totalRed += qRed(value);
        totalGreen += qGreen(value);
        totalBlue += qBlue(value);
        totalAlpha += qAlpha(value);
    }
    return encodeInline(qRgba(totalRed / AVERAGE_COUNT, totalGreen / AVERAGE_COUNT,
        totalBlue / AVERAGE_COUNT, totalAlpha / AVERAGE_COUNT));
} 

