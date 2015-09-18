//
//  Created by Seiji Emery on 9/18/15
//  Copyright 2015 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

Script.include('perfTest.js');
Script.include('../../libraries/three/Three.js');
Script.include('../../libraries/three/math/Vector3.js');
Script.include('../../libraries/three/math/Quaternion.js');

tryCatch(function () {
    var tests = {};
    var jsVec3 = THREE.Vector3;
    var jsQuat = THREE.Quaternion;

    tests.hfVec3 = new TestRunner();
    tests.jsVec3 = new TestRunner();

    var hf_setupAdd = function () {
        this.a = { x: 10, y: 12, z: 3 };
        this.b = { x: 1, y: 2, z: 4 };
    }
    tests.hfVec3.addTestCase('Vec3 immutable add')
        .before(hf_setupAdd)
        .run(function(){
            this.r = Vec3.sum(this.a, this.b);
        })
    tests.hfVec3.addTestCase('Vec3 mutable add')
        .before(hf_setupAdd)
        .run(function(){
            this.a = Vec3.sum(this.a, this.b);
        })
    var js_setupAdd = function () {
        this.a = new jsVec3(10, 12, 3);
        this.b = new jsVec3(1, 2, 4);
    }
    tests.jsVec3.addTestCase('THREE.Vector3 mutable add')
        .before(js_setupAdd)
        .run(function(){
            this.a.add(this.b);
        })
    tests.jsVec3.addTestCase('THREE.Vector3 immutable add (clone)')
        .before(js_setupAdd)
        .run(function(){
            this.r = this.a.clone().add(this.b);
        })
    tests.jsVec3.addTestCase('THREE.Vector3 immutable add (addVectors)')
        .before(function(){
            js_setupAdd.call(this);
            this.r = new jsVec3();
        })
        .run(function(){
            this.r.addVectors(this.a, this.b);
        })
    tests.jsVec3.addTestCase('THREE.Vector3 immutable add (addVectors, new Vector3)')
        .before(js_setupAdd)
        .run(function(){
            this.r = new jsVec3().addVectors(this.a, this.b);
        })

    var hf_setupDist = function () {
        this.a = { x: 12309, y: -1289, z: 20891 };
        this.b = { x: 102, y: 12908, z: -1209 };
    }
    var js_setupDist = function () {
        this.a = new jsVec3(12309, -1289, 20891);
        this.b = new jsVec3(102, 12908, -1209);
    }
    tests.jsVec3.addTestCase('THREE.Vector3 distance')
        .before(js_setupDist)
        .run(function() {
            this.r = this.a.distanceTo(this.b);
        })
    tests.hfVec3.addTestCase('Vec3 distance')
        .before(hf_setupDist)
        .run(function(){
            this.r = Vec3.distance(this.a, this.b);
        })

    tests.hfQuat = new TestRunner();
    tests.jsQuat = new TestRunner();

    var randRange = function(min, max) { return (max - min) * Math.random() + min; }

    var quat_a = new jsQuat(randRange(-1, 1), randRange(-1, 1), randRange(-1, 1), randRange(-1, 1));
    var quat_b = new jsQuat(randRange(-1, 1), randRange(-1, 1), randRange(-1, 1), randRange(-1, 1));

    function setupMul(){
        this.a = quat_a.clone();
        this.b = quat_b.clone();
    }
    tests.hfQuat.addTestCase('Quat multiply')
        .before(setupMul)
        .run(function(){
            this.r = Quat.multiply(this.a, this.b);
        })
    tests.jsQuat.addTestCase('THREE.Quaternion multiply (mutable)')
        .before(setupMul)
        .run(function(){
            this.a.multiply(this.b);
        })
    tests.jsQuat.addTestCase('THREE.Quaternion multiply (immutable)')
        .before(function() { setupMul.call(this); this.r = new jsQuat(); })
        .run(function(){
            this.r.multiplyQuaternions(this.a, this.b);
        })

    tests.jsVec3.runAllTestsWithIterations([1e3, 1e4, 1e5, 1e6], 1e6, 10);
    tests.hfVec3.runAllTestsWithIterations([1e3, 1e4, 1e5], 1e4, 10);

    tests.jsQuat.runAllTestsWithIterations([1e3, 1e4, 1e5, 1e6], 1e6, 10);
    tests.hfQuat.runAllTestsWithIterations([1e3, 1e4, 1e5], 1e4, 10);
})
function tryCatch(fcn) {
    try {
        fcn();
    } catch(err) {
        print(err);
        throw err;
    }
}




