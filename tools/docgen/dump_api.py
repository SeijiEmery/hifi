
import os
import sys
from scanner import DoxygenScanner, autobuild, convertType, script_api

def toJsType(cpptype, knowntypes):
	_toJsType = lambda t: toJsType(t, knowntypes)
	cpptype = cpptype.strip().replace('Q_INVOKABLE', '').replace('const', '').replace('&', '').strip()
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

def dump_scriptable_info(scan_output, api, scanner):
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
		'void': 'undefined'
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
		print('\t\tcpp return: %s'%(method['type']))
		print('\t\tcpp params: %s'%(', '.join([ '%s %s'%(p['type'], p['name']) for p in method['params'] ])))
		print('\t\tjs return: {%s}'%(toJsType(method['type'])))
		print('\t\tjs params: %s'%(', '.join([
			'{%s} %s'%(toJsType(p['type']), p['name']) for p in method['params'] ])))
		if method['description']['brief']:
			print("\t\tbrief description:\n\t\t\t%s"%(method['description']['brief'].replace('para>', 'p>')))
		if method['description']['details']:
			print("\t\tdetailed description:\n\t\t\t%s"%(method['description']['details'].replace('para>', 'p>')))
		if method['description']['inbody']:
			print("\t\tinbody description:\n\t\t\t%s"%(method['description']['inbody'].replace('para>', 'p>')))
		if method['referencedby']:
			print("\tCalled from:")
			for ref in method['referencedby']:
				item = scanner.loaded_items[ref] if ref in scanner.loaded_items else None
				if item:
					if item['parent'] and item['parent'] in scanner.loaded_items:
						name = scanner.loaded_items[item['parent']]['name'] + '::' + item['name']
					else:
						name = item['name']
					print("\t\t%s (%s:%s)"%(name, item['file'], item['line']))
				else:
					print("\t<%s>"%(ref))
	
		print("\tfile: %s, line %s"%(method['file'], method['line']))
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

	rs = scanner.runScriptTrace(script_api.keys())

	''' Hijack stdout to write to a file '''
	out_ = sys.stdout
	out_file = 'tools/docgen/api.txt'
	sys.stdout = open(out_file, 'w')

	dump_scriptable_info(rs, script_api, scanner)
	
	sys.stdout.close()
	sys.stdout = out_
	with open (out_file, 'r') as f:
		print(f.read())
	print("output written to %s"%(out_file))

