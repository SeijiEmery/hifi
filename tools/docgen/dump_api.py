
import os
from scanner import DoxygenScanner, autobuild

def dump_property(prop):
	print("\t%s %s: %s"%(prop['kind'], prop['name'], prop['type']))
	if prop['read']:
		print("\t\tREAD:  %s"%(prop['read']))
	if prop['write']:
		print("\t\tWRITE: %s"%(prop['write']))
	if prop['description']['brief']:
		print("\t\tbrief: %s"%(prop['description']['brief']))
	if prop['description']['details']:
		print("\t\tdescr: %s"%(prop['description']['details']))
	if prop['description']['inbody']:
		print("\t\tinbody description: %s"%(prop['description']['inbody']))
	print("\t(%s, line %s)"%(prop['file'], prop['line']))
	print("")


def dump_method(method):
	print("\t%s %s:  %s (%s)"%(method['kind'], method['name'], method['type'], 
		', '.join([ '%s %s'%(p['type'].replace('Q_INVOKABLE', ''), p['name']) for p in method['params'] ])))
	if method['description']['brief']:
		print("\t\tbrief: %s"%(method['description']['brief']))
	if method['description']['details']:
		print("\t\tdescr: %s"%(method['description']['details']))
	if method['description']['inbody']:
		print("\t\tinbody description: %s"%(method['description']['inbody']))
	print("\t(%s, line %s)"%(method['file'], method['line']))
	print("")

def dump_class(cls, jsname):
	print("class %s %s"%(cls['name'], 'exposed as %s'%jsname if jsname else ''))
	if cls['description']['brief']:
		print("\tbrief: %s"%(cls['description']['brief']))
	if cls['description']['details']:
		print("\tdescr: %s"%(cls['description']['details']))
	if cls['description']['inbody']:
		print("\tinbody description: %s"%(cls['description']['inbody']))
	if not cls['scriptable']:
		print("Not scriptable")
	else:
		print("%s methods, %s properties"%(len(cls['scriptable']['methods']), len(cls['scriptable']['properties'])))
		for prop in cls['scriptable']['properties']:
			dump_property(prop)
		for method in cls['scriptable']['methods']:
			dump_method(method)
	print("")





def dump_scriptable_info(scan_output, api):
	print("")
	print("-- Api dump --")
	print("")
	for item in scan_output['items'].itervalues():
		name = api[item['name']] if item['name'] in api else None
		if item['kind'] in ('struct', 'class'):
			dump_class(item, name)


if __name__ == '__main__':
	os.chdir('../../')	# Navigate to root hifi directory
	autobuild()

	scanner = DoxygenScanner('docs/xml')
	scanner.loadIndex()

	script_api = {
		"ScriptEngine": "Script",
		"AudioScriptingInterface": "Audio",
		"ControllerScriptingInterface": "Controller",
		"EntityScriptingInterface": "Entities",
		"Quat": "Quat",
		"Vec3": "Vec3",
		"AnimationCache": "AnimationCache",
		"MyAvatar": "MyAvatar",
		"AvatarHashMap": "AvatarList",
		"Camera": "Camera",
		"SpeechRecognizer": "SpeechRecognizer",
		"ClipboardScriptingInterface": "Clipboard",
		"Overlays": "Overlays",
		"WindowScriptingInterface": "Window",
		#"location": property LocationScriptingInterface::locationGetter/locationSetter
		"WebWindowClass::constructor": "WebWindow",
		"MenuScriptingInterface": "Menu",
		"SettingsScriptingInterface": "Settings",
		"AudioDeviceScriptingInterface": "AudioDevice",
		"AnimationCache": "AnimationCache",
		"SoundCache": "SoundCache",
		"AccountScriptingInterface": "Account",
		"GlobalServicesScriptingInterface": "GlobalServices",
		"AvatarManager": "AvatarManager",
		"UndoStackScriptingInterface": "UndoStack",
		"LODManager": "LODManager",
		"PathUtils": "Paths",
		"HMDScriptingInterface": "HMD",
		#"HMDScriptingInterface::getHUDLookAtPosition2D": "getHudLookAtPosition2D",
		#"HMDScriptingInterface::getHUDLookAtPosition3D": "getHUDLookAtPosition3D",
		"SceneScriptingInterface": "Scene",
		"RunningScriptsWidget": "ScriptDiscoveryService",
		"XMLHttpRequestClass::constructor": "XMLHttpRequest",
		"AudioEffectOptions::constructor": "AudioEffectOptions",
		#"ScriptEngine::debugPrint": "print",

		#"": "version",		builtin
		#"": "gc",			builtin
		#"": "ArrayBuffer",
		#"": "DataView",
		#"": "Int8Array",
		#"": "Uint8Array",
		#"": "Uint8ClampedArray",
		#"": "Int16Array",
		#"": "Uint16Array",
		#"": "Int32Array",
		#"": "Uint32Array",
		#"": "Float32Array",
		#"": "Float64Array",
	}

	rs = scanner.runScriptTrace(script_api.keys())
	dump_scriptable_info(rs, script_api)




