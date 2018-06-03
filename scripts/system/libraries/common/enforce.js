"use strict";
//  enforce.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
Object.defineProperty(exports, "__esModule", { value: true });
function enforcementOf(exception) {
    return function (condition, messageDelegate, exceptionOverride) {
        if (exceptionOverride === void 0) { exceptionOverride = null; }
        if (!condition) {
            throw new (exceptionOverride || exception)(messageDelegate());
        }
    };
}
exports.enforcementOf = enforcementOf;
exports.enforce = enforcementOf(Error);
exports.enforceType = enforcementOf(TypeError);
