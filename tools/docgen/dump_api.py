
import os
import sys
from scanner import DoxygenScanner, autobuild



def filterNotEmpty(ls):
	return [ x for x in ls if x ]


def convertType(knowntypes, builtintypes):
	def toJsType(cpptype):
		cpptype = cpptype.replace('Q_INVOKABLE', '').replace('const', '').replace('&', '').strip()
		# print(cpptype)
		if '<' in cpptype:
			# print("TEMPLATE")
			template, params = cpptype.strip('>').split('<')
			params = params.split(',')
			template, params = toJsType(template), map(toJsType, params)
			if template == 'Array':
				return '%s[]'%(', '.join(params))
			return '%s.<%s>'%(template, ', '.join(params))
		if cpptype in builtintypes:
			return builtintypes[cpptype]
		if '::' in cpptype:
			return '.'.join(filterNotEmpty(map(toJsType, cpptype.split('::'))))
		if cpptype in knowntypes:
			return cpptype
		# print("UNKNOWN TYPE: %s"%(cpptype))
		return cpptype
		# return "??%s"%(cpptype)
	return toJsType

def toJsType(cpptype, knowntypes):
	_toJsType = lambda t: toJsType(t, knowntypes)
	cpptype = cpptype.replace('Q_INVOKABLE', '').replace('const', '').replace('&', '').strip()
	# print(cpptype)
	if '<' in cpptype:
		# print("TEMPLATE")
		template, params = cpptype.strip('>').split('<')
		params = params.split(',')
		template, params = toJsType(template), map(_toJsType, params)
		if template == 'Array':
			return '%s[]'%(', '.join(params))
		return '%s.<%s>'%(template, ', '.join(params))
	if '::' in cpptype:
		return '.'.join(filterNotEmpty(map(_toJsType, cpptype.split('::'))))
	type_mappings = {
		'QVector': 'Array',
		'QString': 'string',
		'QStringList': 'string[]',
		'int':   'number',
		'unsigned int': 'number',
		'float': 'number',
		'std': '',
		'string': 'string',
		'vector': 'Array'
	}
	if cpptype in type_mappings:
		# print("BUILTIN TYPE")
		return type_mappings[cpptype]
	if not cpptype in knowntypes:
		print("UNKNOWN TYPE: %s"%(cpptype))
		return "??(%s)"%(cpptype)
	return cpptype

def toJsTypeWithApi(api):
	keys = set(api.keys())
	def convert(cpptype):
		return toJsType(cpptype, keys)
	return convert

def dump_scriptable_info(scan_output, api):
	print("")
	print("-- Api dump --")
	print("")

	def dump_items():
		for item in scan_output['items'].itervalues():
			name = api[item['name']] if item['name'] in api else None
			if item['kind'] in ('struct', 'class'):
				dump_class(item, name)
			else:
				print("Don't know how to dump %s %s"%(item['kind'], item['name']))
				print("")

	toJsType = convertType(knowntypes=set(api.keys()), builtintypes={
		'QVector': 'Array',
		'QString': 'string',
		'QStringList': 'string[]',
		'int':   'number',
		'unsigned int': 'number',
		'float': 'number',
		'bool': 'bool',
		'std::string': 'string',
		'std::vector': 'Array',
		'glm::vec3': 'glm::vec3',
		'glm::quat': 'glm::quat',
		'glm::vec2': 'glm::vec2',
		'void': None
	})

	def dump_property(prop):	
		print("\t%s %s"%(prop['kind'], prop['name']))
		print("\tcpp type: %s"%(prop['type']))
		print("\tjs type: {%s}"%(toJsType(prop['type'])))
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
		print("\t%s %s"%(method['kind'], method['name']))
		print('\tcpp type: %s (%s)'%(method['type'], ', '.join([ '%s %s'%(p['type'], p['name']) for p in method['params'] ])))
		type_ = toJsType(method['type'])
		print('\tjs type: %s(%s)'%('{%s} '%(type_) if type_ else '', ', '.join([
			'{%s} %s'%(toJsType(p['type']), p['name']) for p in method['params'] ])))
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

	dump_items()


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




