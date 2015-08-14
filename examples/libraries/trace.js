//
//  uiwidgets.js
//  examples/libraries
//
//  Created by Seiji Emery, 8/14/15
//  Copyright 2015 High Fidelity, Inc
//
//	Implements manual tracebacks (ie. Error.stack), since this functionality is missing from QScriptEngine.
//	Usage:
//		Script.include('trace.js');
//		useTracebacks();	// or noTracebacks();
//	
//		// decorate functions with tracebacks
//		var myFunc = function (...) { 
//			// ... 
//		}.traced();
//
//		// Catch bugs at runtime
//		try {
//			// do stuff...
//		} catch (e) {
//			// print error using e.trace();			
//		}
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

(function(){

this.useTracebacks = function (optionalLineFormatting) {
	// Define a traced function, which decorates an existing function w/ a manual stacktrace.
	// Takes optional file and line parameters (fragile).
	//
	//	usage: var myFcn = traced(function (...) { ... });
	//
	this.traced = (function () {
	    var __trace = [];
	    var fmtLine = optionalLineFormatting || function (functionBody, optionalFile, optionalLine) {
	    	return functionBody;
	    };
	    return function (f, file, line) {
	        var fmt = function (fbody) { return fmtLine(fbody, file, line); };
	        return function () {
	            try {
	                __trace.push(f);
	                var rv = f.apply(this, arguments);
	                __trace.pop();
	                return rv;
	            } catch (e) {
	                if (!e.stack)
	                    e.stack = __trace.map(fmt).join('\n');
	                throw e;
	            }
	        }
	    }
	})();
	
	// Register a method on Function, which does the same thing but is slightly more convenient.
	//
	//  usage: var myFcn = function (...) { ... }.trace();
	//
	Function.prototype.traced = function () {
	    return traced(this);
	};
};
// useTracebacks();

// Zero-overhead impl:
this.noTracebacks = function () {
	this.traced = function (f) { return f; }
	Function.prototype.traced = function () {
		return this;
	}
}
})();



