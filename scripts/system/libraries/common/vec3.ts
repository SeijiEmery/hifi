//  vec3.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
import { enforce, enforceType } from './enforce';
import { Color, NativeColor } from './color';
import { Quat, NativeQuat } from './quat';


// Helper functions - move out later...
function assert (condition: boolean, message: string) {
    if (!condition) {
        throw new Error(message);
    }
}
function warnAPI (source: string, message: string) {
    console.warn("API warning ("+source+"): "+message);
}
function clamp (x: number, min: number, max: number) {
    assert(min < max, ""+min+" > "+max+"!");
    return x < min ? min : x > max ? max : x;
}

// Describes the vec3 object (converted glm::vec3) returned by Hifi APIs.
export interface NativeVec3 {
    x: number;
    y: number;
    z: number;
}


export class Vec3 implements NativeVec3 {
    public x: number;
    public y: number;
    public z: number;

    // Constructs a new Vec3 from either x / y / z values,
    // or an existing object w/ x / y / z attributes. 
    // All of these are optional and default to 0.
    constructor (arg0: (NativeVec3 | number), y?: number, z?: number) {
        switch (typeof(arg0)) {
            case 'object': {
                let other = <NativeVec3>arg0;
                this.x = other.x || 0.0;
                this.y = other.y || 0.0;
                this.z = other.z || 0.0;
            } break;
            case 'number': {
                let x = <number>arg0;
                this.x = x || 0.0;
                this.y = y || 0.0;
                this.z = z || 0.0;
            } break;
            default: {
                throw new Error("Invalid argument passed to new Vec3(): "+typeof(arg0)+": "+arg0);
            }
        }
    }

    //
    // Explicit constructors
    //

    // Constructs + returns a new Vec3 from any vec3-like value.
    static fromVec3 (other: NativeVec3) : Vec3 {
        return new Vec3(other);
    }

    // Constructs a Vec3 from a Hifi RGB color value.
    static fromColor (color: NativeColor) : Vec3 {
        return new Vec3(color.red / 255.0, color.green / 255.0, color.blue / 255.0);
    }

    // TBD: Constructors from Quat value

    //
    // New API methods
    //

    add (other: Vec3) : Vec3 {
        return new Vec3( 
            this.x + other.x,
            this.y + other.y,
            this.z + other.z,
        );
    }
    subtract (other: Vec3) : Vec3 {
        return new Vec3(
            this.x - other.x,
            this.y - other.y,
            this.z - other.z,
        );
    }
    scale (other: number) : Vec3 {
        return new Vec3(
            this.x * other,
            this.y * other,
            this.z * other,
        );
    }
    negated () : Vec3 {
        return new Vec3(
            -this.x,
            -this.y,
            -this.z,
        );
    }
    inverse () : Vec3 {
        return new Vec3(
            1.0 / this.x,
            1.0 / this.y,
            1.0 / this.z,
        );
    }
    multiplyVector (other: Vec3) : Vec3 {
        return new Vec3(
            this.x * other.x,
            this.y * other.y,
            this.z * other.z,
        );
    }
    multiply (other: number | Quat | Vec3) : Vec3 {
        if (typeof(other) === 'number') { return this.scale(<number>other); }
        else if (other instanceof Quat) { assert(false, "TBD"); return Vec3.ZERO; }//return (<Quat>other).multiply(this); }
        else if (other instanceof Vec3) { return this.multiplyVector(<Vec3>other); }
        else { throw new TypeError("Expected number | Quat | Vec3, not "+typeof(other)); }
    }
    divide (other: number) : Vec3 {
        return new Vec3(
            this.x / other,
            this.y / other,
            this.z / other,
        );
    }
    dot (other: Vec3) : number {
        return this.x * other.x +
            this.y * other.y + 
            this.z * other.z;
    }
    cross (other: Vec3) : Vec3 {
        return new Vec3(
            this.y * other.z - this.z * other.y,
            this.z * other.x - this.x * other.z,
            this.x * other.y - this.y * other.x,
        );
    }
    magnitudeSquared () : number {
        return this.dot(this);
    }
    magnitude () : number {
        return Math.sqrt(this.magnitudeSquared());
    }
    normalized () : Vec3 {
        return this.divide(this.magnitude());
    }
    isNormalized () : boolean {
        return this.magnitude() == 1.0;
    }
    distance (other: Vec3) : number {
        return this.subtract(other).magnitude();
    }
    equals (other: Vec3, epsilon: number | null) : boolean {
        return epsilon ?
            Math.abs(this.x - other.x) <= epsilon &&
            Math.abs(this.y - other.y) <= epsilon &&
            Math.abs(this.z - other.z) <= epsilon :
            this.x == other.x &&
            this.y == other.y &&
            this.z == other.z;            
    }
    toString () : string {
        return "Vec3("+this.x+", "+this.y+", "+this.z+")";
    }
    toPolar () : Vec3 {
        assert(false, "TBD");
        return Vec3.ZERO;
    }
    fromPolar () : Vec3 {
        assert(false, "TBD");
        return Vec3.ZERO;
    }
    reflect () : Vec3 {
        assert(false, "TBD");
        return Vec3.ZERO;
    }
    angle (other: Vec3) : number {
        let cosTheta = this.dot(other) / this.magnitude() / other.magnitude();
        let angle = Math.acos(cosTheta);

        assert(false, "TBD: Map range from [0, π] to [-π, +π]!");
        return angle;
    }
    lerp (other: Vec3, factor: number) : Vec3 {
        if (factor > 1.0 || factor < 0.0) {
            warnAPI("Vec3.lerp", "factor "+factor+" not bounded by [0, 1]");
            factor = clamp(factor, 0.0, 1.0);
        }
        factor = clamp(factor, 0.0, 1.0);
        return this.multiply(1 - factor).add(other.multiply(factor));
    }
    slerp (other: Vec3, factor: number) : Vec3 {
        assert(false, "TBD");
        return Vec3.ZERO;
    }
    interpolate (other: Vec3, factor: number) : Vec3 {
        return this.lerp(other, factor);
    }

    //
    // Wrapper functions implementing the old API using new methods.
    // Should unittest to ensure that behavior is the same (TBD)
    //

    static sum (a: Vec3, b: Vec3) : Vec3 {
        return a.add(b);
    }
    static subtract (a: Vec3, b: Vec3) : Vec3 {
        return a.subtract(b);
    }
    static multiply (a: (Vec3 | number), b: (Vec3 | number)) : Vec3 {
        // Dynamic typechecking
        enforce(
            // condition
            (typeof(a) === 'object') != (typeof(b) === 'object'),

            // error message is wrapped in a function so it is lazily evaluated
            function(){ return "invalid argument(s) passed to Vec3.multiply(): "
                + Array.prototype.map.apply(arguments, 
                    function(x) { return typeof(x); }).join(", "); },

            // Exception to throw, default Error
            TypeError
        );

        // Function should thus be dispatched correctly for both cases:
        //        Vec3.multiply(1, { x: 10, y: 12, z: 13 })
        // and    Vec3.multiply({ x: 10, y: 12, z: 13 }, 1)
        return typeof(a) === 'object' ?
            (<Vec3>a).multiply(<number>b) :
            (<Vec3>b).multiply(<number>a);
    }
    static multiplyVbyV (a: Vec3, b: Vec3) : Vec3 {
        return a.multiplyVector(b);
    }
    static multiplyQbyV (q: Quat, v: Vec3) : Vec3 {
        // return q.multiply(v);
        assert(false, "TBD");
        return Vec3.ZERO;
    }
    static equal (a: Vec3, b: Vec3) : boolean {
        return a.equals(b, null);
    }
    static withinEpsilon (a: Vec3, b: Vec3, epsilon: number) : boolean {
        return a.equals(b, epsilon);
    }
    static print (label: string, v: Vec3) {
        console.log(label + v);
    }
    static orientedAngle (a: Vec3, b: Vec3, reference: Vec3) : number {
        assert(false, "TBD");
        return 0.0;
    }
    static normalize (v: Vec3) : Vec3 {
        return v.normalized();
    }
    static cross (a: Vec3, b: Vec3) : Vec3 {
        return a.cross(b);
    }
    static getAngle (a: Vec3, b: Vec3) : number {
        return a.angle(b);
    }
    static mix (a: Vec3, b: Vec3, factor: number) : Vec3 {
        return a.lerp(b, factor);
    }
    // Typescript error:
    //    Static property 'length' conflicts with built-in property 'Function.length' of constructor function 'Vec3'.
    // Will have to rename this...
    //
    // static length (a: Vec3) : number {
    //     return a.magnitude();
    // }
    static dot (a: Vec3, b: Vec3) : number {
        return a.dot(b);
    }
    static distance (a: Vec3, b: Vec3) : number {
        return a.distance(b);
    }

    static ZERO       : Vec3 = new Vec3(0.0, 0.0, 0.0);
    static ONE        : Vec3 = new Vec3(1.0, 1.0, 1.0);
    static TWO        : Vec3 = Vec3.ONE.scale(2.0);
    static HALF       : Vec3 = Vec3.ONE.scale(0.5);
    static FLOAT_MAX  : Vec3 = Vec3.ONE.scale(3.402823e+38);
    static FLOAT_MIN  : Vec3 = Vec3.ONE.scale(-3.402823e+38);

    static UNIT_X     : Vec3 = new Vec3(1.0, 0.0, 0.0);
    static UNIT_Y     : Vec3 = new Vec3(0.0, 1.0, 0.0);
    static UNIT_Z     : Vec3 = new Vec3(0.0, 0.0, 1.0);

    static UNIT_NEG_X : Vec3 = Vec3.ZERO.subtract(Vec3.UNIT_X);
    static UNIT_NEG_Y : Vec3 = Vec3.ZERO.subtract(Vec3.UNIT_Y);
    static UNIT_NEG_Z : Vec3 = Vec3.ZERO.subtract(Vec3.UNIT_Z);

    static UNIT_XY    : Vec3 = Vec3.UNIT_X.add(Vec3.UNIT_Y).normalized();
    static UNIT_XZ    : Vec3 = Vec3.UNIT_X.add(Vec3.UNIT_Z).normalized();
    static UNIT_YZ    : Vec3 = Vec3.UNIT_Y.add(Vec3.UNIT_Z).normalized();

    static UNIT_XYZ   : Vec3 = Vec3.ONE.normalized();

    static RIGHT : Vec3 = Vec3.UNIT_X;
    static LEFT  : Vec3 = Vec3.UNIT_NEG_X;
    static UP    : Vec3 = Vec3.UNIT_Y;
    static DOWN  : Vec3 = Vec3.UNIT_NEG_Y;
    static BACK  : Vec3 = Vec3.UNIT_Z;
    static FRONT : Vec3 = Vec3.UNIT_NEG_Y;
}
