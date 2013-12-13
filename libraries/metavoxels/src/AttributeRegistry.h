//
//  AttributeRegistry.h
//  metavoxels
//
//  Created by Andrzej Kapolka on 12/6/13.
//  Copyright (c) 2013 High Fidelity, Inc. All rights reserved.
//

#ifndef __interface__AttributeRegistry__
#define __interface__AttributeRegistry__

#include <QColor>
#include <QHash>
#include <QSharedPointer>
#include <QString>

#include "Bitstream.h"

class Attribute;

typedef QSharedPointer<Attribute> AttributePointer;

/// Maintains information about metavoxel attribute types.
class AttributeRegistry {
public:
    
    /// Returns a pointer to the singleton registry instance.
    static AttributeRegistry* getInstance() { return &_instance; }
    
    AttributeRegistry();
    
    /// Registers an attribute with the system.  The registry assumes ownership of the object.
    /// \return either the pointer passed as an argument, if the attribute wasn't already registered, or the existing
    /// attribute
    AttributePointer registerAttribute(Attribute* attribute) { return registerAttribute(AttributePointer(attribute)); }
    
    /// Registers an attribute with the system.
    /// \return either the pointer passed as an argument, if the attribute wasn't already registered, or the existing
    /// attribute
    AttributePointer registerAttribute(AttributePointer attribute);
    
    /// Retrieves an attribute by name.
    AttributePointer getAttribute(const QString& name) const { return _attributes.value(name); }
    
    /// Returns a reference to the standard QRgb "color" attribute.
    const AttributePointer& getColorAttribute() const { return _colorAttribute; }
    
    /// Returns a reference to the standard QRgb "normal" attribute.
    const AttributePointer& getNormalAttribute() const { return _normalAttribute; }
    
    /// Returns a reference to the standard "voxelizer" attribute.
    const AttributePointer& getVoxelizerAttribute() const { return _voxelizerAttribute; }
    
private:

    static AttributeRegistry _instance;

    QHash<QString, AttributePointer> _attributes;
    AttributePointer _colorAttribute;
    AttributePointer _normalAttribute;
    AttributePointer _voxelizerAttribute;
};

/// Converts a value to a void pointer.
template<class T> inline void* encodeInline(T value) {
    return *(void**)&value;
}

/// Extracts a value from a void pointer.
template<class T> inline T decodeInline(void* value) {
    return *(T*)&value;
}

/// Pairs an attribute value with its type.
class AttributeValue {
public:
    
    AttributeValue(const AttributePointer& attribute = AttributePointer());
    AttributeValue(const AttributePointer& attribute, void* value);
    
    AttributePointer getAttribute() const { return _attribute; }
    void* getValue() const { return _value; }
    
    template<class T> void setInlineValue(T value) { _value = encodeInline(value); }
    template<class T> T getInlineValue() const { return decodeInline<T>(_value); }
    
    template<class T> T* getPointerValue() const { return static_cast<T*>(_value); }
    
    void* copy() const;

    bool isDefault() const;

    bool operator==(const AttributeValue& other) const;
    bool operator==(void* other) const;
    
protected:
    
    AttributePointer _attribute;
    void* _value;
};

// Assumes ownership of an attribute value.
class OwnedAttributeValue : public AttributeValue {
public:
    
    OwnedAttributeValue(const AttributePointer& attribute = AttributePointer());
    OwnedAttributeValue(const AttributePointer& attribute, void* value);
    OwnedAttributeValue(const AttributeValue& other);
    ~OwnedAttributeValue();
    
    OwnedAttributeValue& operator=(const AttributeValue& other);
};

/// Represents a registered attribute.
class Attribute {
public:

    static const int AVERAGE_COUNT = 8;
    
    Attribute(const QString& name);
    virtual ~Attribute();

    const QString& getName() const { return _name; }

    void* create() const { return create(getDefaultValue()); }
    virtual void* create(void* copy) const = 0;
    virtual void destroy(void* value) const = 0;

    virtual bool read(Bitstream& in, void*& value) const = 0;
    virtual bool write(Bitstream& out, void* value) const = 0;

    virtual bool equal(void* first, void* second) const = 0;

    virtual void* createAveraged(void* values[]) const = 0;

    virtual void* getDefaultValue() const = 0;

private:

    QString _name;
};

/// A simple attribute class that stores its values inline.
template<class T, int bits> class InlineAttribute : public Attribute {
public:
    
    InlineAttribute(const QString& name, T defaultValue = T()) : Attribute(name), _defaultValue(encodeInline(defaultValue)) { }
    
    virtual void* create(void* copy) const { return copy; }
    virtual void destroy(void* value) const { /* no-op */ }
    
    virtual bool read(Bitstream& in, void*& value) const { value = getDefaultValue(); in.read(&value, bits); return false; }
    virtual bool write(Bitstream& out, void* value) const { out.write(&value, bits); return false; }

    virtual bool equal(void* first, void* second) const { return first == second; }

    virtual void* createAveraged(void* values[]) const;

    virtual void* getDefaultValue() const { return _defaultValue; }

private:
    
    void* _defaultValue;
};

template<class T, int bits> inline void* InlineAttribute<T, bits>::createAveraged(void* values[]) const {
    T total = T();
    for (int i = 0; i < AVERAGE_COUNT; i++) {
        total += decodeInline<T>(values[i]);
    }
    total /= AVERAGE_COUNT;
    return encodeInline(total);
}

/// Provides appropriate averaging for RGBA values.
class QRgbAttribute : public InlineAttribute<QRgb, 32> {
public:
    
    QRgbAttribute(const QString& name, QRgb defaultValue = QRgb());
    
    virtual void* createAveraged(void* values[]) const;
};

/// An attribute class that stores pointers to its values.
template<class T> class PointerAttribute : public Attribute {
public:
    
    PointerAttribute(const QString& name, T defaultValue = T()) : Attribute(name), _defaultValue(defaultValue) { }
    
    virtual void* create(void* copy) const { new T(*static_cast<T*>(copy)); }
    virtual void destroy(void* value) const { delete static_cast<T*>(value); }
    
    virtual bool read(Bitstream& in, void*& value) const { in >> *static_cast<T*>(value); return true; }
    virtual bool write(Bitstream& out, void* value) const { out << *static_cast<T*>(value); return true; }

    virtual bool equal(void* first, void* second) const { return *static_cast<T*>(first) == *static_cast<T*>(second); }

    virtual void* createAveraged(void* values[]) const;

    virtual void* getDefaultValue() const { return const_cast<void*>((void*)&_defaultValue); }

private:
    
    T _defaultValue;
}; 

template<class T> inline void* PointerAttribute<T>::createAveraged(void* values[]) const {
    T* total = new T();
    for (int i = 0; i < AVERAGE_COUNT; i++) {
        *total += *static_cast<T*>(values[i]);
    }
    *total /= AVERAGE_COUNT;
    return total;
}

#endif /* defined(__interface__AttributeRegistry__) */
