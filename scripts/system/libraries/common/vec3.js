"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
//  vec3.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
var enforce_1 = require("./enforce");
var quat_1 = require("./quat");
// Helper functions - move out later...
function assert(condition, message) {
    if (!condition) {
        throw new Error(message);
    }
}
function warnAPI(source, message) {
    console.warn("API warning (" + source + "): " + message);
}
function clamp(x, min, max) {
    assert(min < max, "" + min + " > " + max + "!");
    return x < min ? min : x > max ? max : x;
}
var Vec3 = /** @class */ (function () {
    // Constructs a new Vec3 from either x / y / z values,
    // or an existing object w/ x / y / z attributes. 
    // All of these are optional and default to 0.
    function Vec3(arg0, y, z) {
        switch (typeof (arg0)) {
            case 'object':
                {
                    var other = arg0;
                    this.x = other.x || 0.0;
                    this.y = other.y || 0.0;
                    this.z = other.z || 0.0;
                }
                break;
            case 'number':
                {
                    var x = arg0;
                    this.x = x || 0.0;
                    this.y = y || 0.0;
                    this.z = z || 0.0;
                }
                break;
            default: {
                throw new Error("Invalid argument passed to new Vec3(): " + typeof (arg0) + ": " + arg0);
            }
        }
    }
    //
    // Explicit constructors
    //
    // Constructs + returns a new Vec3 from any vec3-like value.
    Vec3.fromVec3 = function (other) {
        return new Vec3(other);
    };
    // Constructs a Vec3 from a Hifi RGB color value.
    Vec3.fromColor = function (color) {
        return new Vec3(color.red / 255.0, color.green / 255.0, color.blue / 255.0);
    };
    // TBD: Constructors from Quat value
    //
    // New API methods
    //
    Vec3.prototype.add = function (other) {
        return new Vec3(this.x + other.x, this.y + other.y, this.z + other.z);
    };
    Vec3.prototype.subtract = function (other) {
        return new Vec3(this.x - other.x, this.y - other.y, this.z - other.z);
    };
    Vec3.prototype.scale = function (other) {
        return new Vec3(this.x * other, this.y * other, this.z * other);
    };
    Vec3.prototype.negated = function () {
        return new Vec3(-this.x, -this.y, -this.z);
    };
    Vec3.prototype.inverse = function () {
        return new Vec3(1.0 / this.x, 1.0 / this.y, 1.0 / this.z);
    };
    Vec3.prototype.multiplyVector = function (other) {
        return new Vec3(this.x * other.x, this.y * other.y, this.z * other.z);
    };
    Vec3.prototype.multiply = function (other) {
        if (typeof (other) === 'number') {
            return this.scale(other);
        }
        else if (other instanceof quat_1.Quat) {
            assert(false, "TBD");
            return Vec3.ZERO;
        } //return (<Quat>other).multiply(this); }
        else if (other instanceof Vec3) {
            return this.multiplyVector(other);
        }
        else {
            throw new TypeError("Expected number | Quat | Vec3, not " + typeof (other));
        }
    };
    Vec3.prototype.divide = function (other) {
        return new Vec3(this.x / other, this.y / other, this.z / other);
    };
    Vec3.prototype.dot = function (other) {
        return this.x * other.x +
            this.y * other.y +
            this.z * other.z;
    };
    Vec3.prototype.cross = function (other) {
        return new Vec3(this.y * other.z - this.z * other.y, this.z * other.x - this.x * other.z, this.x * other.y - this.y * other.x);
    };
    Vec3.prototype.magnitudeSquared = function () {
        return this.dot(this);
    };
    Vec3.prototype.magnitude = function () {
        return Math.sqrt(this.magnitudeSquared());
    };
    Vec3.prototype.normalized = function () {
        return this.divide(this.magnitude());
    };
    Vec3.prototype.isNormalized = function () {
        return this.magnitude() == 1.0;
    };
    Vec3.prototype.distance = function (other) {
        return this.subtract(other).magnitude();
    };
    Vec3.prototype.equals = function (other, epsilon) {
        return epsilon ?
            Math.abs(this.x - other.x) <= epsilon &&
                Math.abs(this.y - other.y) <= epsilon &&
                Math.abs(this.z - other.z) <= epsilon :
            this.x == other.x &&
                this.y == other.y &&
                this.z == other.z;
    };
    Vec3.prototype.toString = function () {
        return "Vec3(" + this.x + ", " + this.y + ", " + this.z + ")";
    };
    Vec3.prototype.toPolar = function () {
        assert(false, "TBD");
        return Vec3.ZERO;
    };
    Vec3.prototype.fromPolar = function () {
        assert(false, "TBD");
        return Vec3.ZERO;
    };
    Vec3.prototype.reflect = function () {
        assert(false, "TBD");
        return Vec3.ZERO;
    };
    Vec3.prototype.angle = function (other) {
        var cosTheta = this.dot(other) / this.magnitude() / other.magnitude();
        var angle = Math.acos(cosTheta);
        assert(false, "TBD: Map range from [0, π] to [-π, +π]!");
        return angle;
    };
    Vec3.prototype.lerp = function (other, factor) {
        if (factor > 1.0 || factor < 0.0) {
            warnAPI("Vec3.lerp", "factor " + factor + " not bounded by [0, 1]");
            factor = clamp(factor, 0.0, 1.0);
        }
        factor = clamp(factor, 0.0, 1.0);
        return this.multiply(1 - factor).add(other.multiply(factor));
    };
    Vec3.prototype.slerp = function (other, factor) {
        assert(false, "TBD");
        return Vec3.ZERO;
    };
    Vec3.prototype.interpolate = function (other, factor) {
        return this.lerp(other, factor);
    };
    //
    // Wrapper functions implementing the old API using new methods.
    // Should unittest to ensure that behavior is the same (TBD)
    //
    Vec3.sum = function (a, b) {
        return a.add(b);
    };
    Vec3.subtract = function (a, b) {
        return a.subtract(b);
    };
    Vec3.multiply = function (a, b) {
        // Dynamic typechecking
        enforce_1.enforce(
        // condition
        (typeof (a) === 'object') != (typeof (b) === 'object'), 
        // error message is wrapped in a function so it is lazily evaluated
        function () {
            return "invalid argument(s) passed to Vec3.multiply(): "
                + Array.prototype.map.apply(arguments, function (x) { return typeof (x); }).join(", ");
        }, 
        // Exception to throw, default Error
        TypeError);
        // Function should thus be dispatched correctly for both cases:
        //        Vec3.multiply(1, { x: 10, y: 12, z: 13 })
        // and    Vec3.multiply({ x: 10, y: 12, z: 13 }, 1)
        return typeof (a) === 'object' ?
            a.multiply(b) :
            b.multiply(a);
    };
    Vec3.multiplyVbyV = function (a, b) {
        return a.multiplyVector(b);
    };
    Vec3.multiplyQbyV = function (q, v) {
        // return q.multiply(v);
        assert(false, "TBD");
        return Vec3.ZERO;
    };
    Vec3.equal = function (a, b) {
        return a.equals(b, null);
    };
    Vec3.withinEpsilon = function (a, b, epsilon) {
        return a.equals(b, epsilon);
    };
    Vec3.print = function (label, v) {
        console.log(label + v);
    };
    Vec3.orientedAngle = function (a, b, reference) {
        assert(false, "TBD");
        return 0.0;
    };
    Vec3.normalize = function (v) {
        return v.normalized();
    };
    Vec3.cross = function (a, b) {
        return a.cross(b);
    };
    Vec3.getAngle = function (a, b) {
        return a.angle(b);
    };
    Vec3.mix = function (a, b, factor) {
        return a.lerp(b, factor);
    };
    // Typescript error:
    //    Static property 'length' conflicts with built-in property 'Function.length' of constructor function 'Vec3'.
    // Will have to rename this...
    //
    // static length (a: Vec3) : number {
    //     return a.magnitude();
    // }
    Vec3.dot = function (a, b) {
        return a.dot(b);
    };
    Vec3.distance = function (a, b) {
        return a.distance(b);
    };
    Vec3.ZERO = new Vec3(0.0, 0.0, 0.0);
    Vec3.ONE = new Vec3(1.0, 1.0, 1.0);
    Vec3.TWO = Vec3.ONE.scale(2.0);
    Vec3.HALF = Vec3.ONE.scale(0.5);
    Vec3.FLOAT_MAX = Vec3.ONE.scale(3.402823e+38);
    Vec3.FLOAT_MIN = Vec3.ONE.scale(-3.402823e+38);
    Vec3.UNIT_X = new Vec3(1.0, 0.0, 0.0);
    Vec3.UNIT_Y = new Vec3(0.0, 1.0, 0.0);
    Vec3.UNIT_Z = new Vec3(0.0, 0.0, 1.0);
    Vec3.UNIT_NEG_X = Vec3.ZERO.subtract(Vec3.UNIT_X);
    Vec3.UNIT_NEG_Y = Vec3.ZERO.subtract(Vec3.UNIT_Y);
    Vec3.UNIT_NEG_Z = Vec3.ZERO.subtract(Vec3.UNIT_Z);
    Vec3.UNIT_XY = Vec3.UNIT_X.add(Vec3.UNIT_Y).normalized();
    Vec3.UNIT_XZ = Vec3.UNIT_X.add(Vec3.UNIT_Z).normalized();
    Vec3.UNIT_YZ = Vec3.UNIT_Y.add(Vec3.UNIT_Z).normalized();
    Vec3.UNIT_XYZ = Vec3.ONE.normalized();
    Vec3.RIGHT = Vec3.UNIT_X;
    Vec3.LEFT = Vec3.UNIT_NEG_X;
    Vec3.UP = Vec3.UNIT_Y;
    Vec3.DOWN = Vec3.UNIT_NEG_Y;
    Vec3.BACK = Vec3.UNIT_Z;
    Vec3.FRONT = Vec3.UNIT_NEG_Y;
    return Vec3;
}());
exports.Vec3 = Vec3;
