//  quat.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
import { enforceType } from './enforce';
import { Color, NativeColor } from './color';
import { Vec3, NativeVec3 } from './vec3';

// Describes the vec3 object (converted glm::vec3) returned by Hifi APIs.
export interface NativeQuat {
    x: number;
    y: number;
    z: number;
    w: number;
}

export class Quat implements NativeQuat {
    public x: number;
    public y: number;
    public z: number;
    public w: number;

    // TBD
}
