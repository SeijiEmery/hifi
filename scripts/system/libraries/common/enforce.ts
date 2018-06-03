//  enforce.ts
//
//  Created by Seiji Emery on 2018-5-20
//  Copyright 2018 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html

export interface IEnforcer {
    (condition: boolean, messageDelegate: () => string, exception: any | null)
}
export function enforcementOf (exception: any) : IEnforcer {
    return function (condition, messageDelegate, exceptionOverride: any | null = null) {
        if (!condition) {
            throw new (exceptionOverride || exception)(messageDelegate());
        }    
    }
}
export let enforce : IEnforcer = enforcementOf(Error);
export let enforceType : IEnforcer = enforcementOf(TypeError);
