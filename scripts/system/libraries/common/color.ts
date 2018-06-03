//  color.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html


// Describes the Color object returned by Hifi APIs. 
export interface NativeColor {
    red: number;
    green: number;
    blue: number;
}

export class Color implements NativeColor {
    red: number;
    green: number;
    blue: number;

    // TBD
}
