import os
import sys
from scanner import DoxygenScanner, autobuild, convertType, script_api
import json


class PrintToFile(object):
	def __init__(self, filepath, writemode='w', duplicate_to_stdout=False):
		self._stdout = sys.stdout
		self._filepath = filepath
		self.duplicate_to_stdout = duplicate_to_stdout
		self.writemode = writemode
	def __enter__(self):
		self._out = open(self._filepath, self.writemode)
		sys.stdout = self._out
	def __exit__(self, type, value, traceback):
		self._out.close()
		sys.stdout = self._stdout
		if self.duplicate_to_stdout:
			with open(self._filepath, 'r') as f:
				print(f.read())


def loadApi(config_file, scanner):
	with open(config_file, 'r') as f:
		config = json.load(f)
	try:
		names = set()
		def checkUniqueName(name, item):
			if name in names:
				print("WARNING: Redefining %s as %s"%(name, item))
			names.add(name)

		interface_blacklist = set()

		additional_type_blackist = set()
		additional_type_whitelist = set()

		manually_defined_stuff = {}

		interfaces = {}
		for [name, cppname, docpage] in config['interfaces']:
			item = {
				'kind': 'global-object',
				'name': name,
				'cppname': cppname,
				'docpage': docpage,
				'loaded': False
			}
			checkUniqueName(name, item)
			interfaces[name] = item

		interface_blacklist = set(config['interface_blacklist'])
		unused_blacklist_names = []
		warn_unused_blacklist = config['warn_unused_interface_blacklist'] \
			if 'warn_unused_interface_blacklist' in config else False
		for name in interface_blacklist:
			if name in interfaces:
				del interfaces[name]
			else:
				unused_blacklist_names.append(name)
		if unused_blacklist_names and warn_unused_blacklist:
			print("WARNING: Unused interface blacklist items: [%s]"%(', '.join(unused_blacklist_names)))
	except KeyError as e:
		print("Bad config file")
		raise e

	interface_cpp = { x['cppname']: x for x in interfaces.itervalues() }

	with PrintToFile('lastrun.log', 'a+', True):
		scan_results = scanner.runScriptTrace(interface_cpp.keys())

	def restricted_dict(d, ks):
		return { k: v for k, v in d.iteritems() if k in ks }

	def convType(t):
		return t

	def getDescription(thing):
		d = thing['description']
		return d if d['brief'] or d['details'] or d['inbody'] else None

	scanned_types = {}
	def parse_scan_results():
		def parse_method(method, name):
			return {
				'name': method['name'].split('::')[-1],
				'isSignal': method['kind'] == 'signal',
				'return': convType(method['type']),
				'params': [{ 'name': p['name'], 'type': convType(p['type']) } for p in method['params'] ],
				'descr': getDescription(method)
			}
		def parse_property(prop, name):
			return {
				'name': prop['name'].split('::')[-1],
				'type': convType(prop['type'])
			}
		def parse_class(cls, name):
			methods = cls['scriptable']['methods'] if cls['scriptable'] else []
			properties = cls['scriptable']['properties'] if cls['scriptable'] else []
			return {
				'methods': [ parse_method(method, name) for method in methods ],
				'properties': [ parse_property(prop, name) for prop in properties ],
				'loaded': True
			}

		for item in scan_results['items'].itervalues():
			if item['name'] in interface_cpp:
				if item['kind'] in ('struct', 'class'):
					name = interface_cpp[item['name']]['name']
					interfaces[name].update(parse_class(item, name))
				else:
					print("Unhandled interface kind '%s': "%(item['kind'], restricted_dict(item, set(['name']))))
			else:
				print("FOUND TYPE %s"%(item['name']))
				if item['kind'] in ('struct', 'class'):
					scanned_types[item['name']] = {
						'name': item['name'],
						'docpage': 'types#%s'%item['name']
					}
				else:
					print("Don't know how to parse '%s'"%(item['kind']))

	parse_scan_results()

	non_loaded = [ x['name'] for x in interfaces.itervalues() if not x['loaded'] ]
	if non_loaded:
		print("WARNING: The following class interfaces were not found:\n\t%s"%', '.join(non_loaded))
		interfaces = { k: v for k, v in interfaces.iteritems() if v['loaded'] }
 
	toJsType = convertType(knowntypes={}, builtintypes={
		'QObject': 'object',
	    'QVector': 'Array',
	    'QString': 'string',
	    'QStringList': 'string[]',
	    'QVariant': 'object',
	    'QVariantList': 'Array',
	    'QVariantMap': 'object',
	    'QScriptValue': 'object',
	    'int': 'number',
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

	typelist = dict(interfaces)
	typelist.update(scanned_types)

	typelist['EntityItemProperties'] = {
		'name': 'EntityItemProperties',
		'docpage': 'entity-properties'
	}

	def fmtType(t):
		t = toJsType(t)
		if t in typelist:
			return '[%s](doc:%s)'%(t, typelist[t]['docpage'])
		return t

	print("")
	print("Generating api-reference.txt")
	with PrintToFile("tools/docgen/generated/api-reference.txt", duplicate_to_stdout=False):
		for cls in interfaces.itervalues():
			print("")
			print("# %s"%cls['name'])
			for method in cls['methods']:
				print("%s [**%s**](%s) (%s)%s"%(
					'function' if not method['isSignal'] else 'signal',
					'%s.%s'%(cls['name'], method['name']),
					'doc:%s#%s'%(cls['docpage'], method['name']),
					', '.join([
							'%s %s'%(fmtType(p['type']), p['name'])
							for p in method['params']
						]),
					' => %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
					))
			for prop in cls['properties']:
				print("property [**%s**](%s): %s"%(
					'%s.%s'%(cls['name'], prop['name']),
					'doc:%s#%s'%(cls['docpage'], prop['name']),
					fmtType(prop['type'])
				))
	for cls in interfaces.itervalues():
		print("Generating stub: %s.txt"%(cls['docpage']))
		with PrintToFile("tools/docgen/generated/%s.txt"%(cls['docpage'])):
			methods = [ method for method in cls['methods'] if not method['isSignal'] ]
			signals = [ method for method in cls['methods'] if method['isSignal'] ]

			''' Print page header / summary '''
			if methods:
				print("### Functions:")
				for method in methods:
					print("function [**%s**](%s) (%s)%s"%(
						'%s.%s'%(cls['name'], method['name']),
						'#%s'%(method['name']),
						', '.join([
							'%s %s'%(fmtType(p['type']), p['name'])
							for p in method['params']
						]),
						' => %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
					))
			if signals:
				print("### Signals:")
				for method in methods:
					print("signal [**%s**](%s) (%s)%s"%(
						'%s.%s'%(cls['name'], method['name']),
						'#%s'%(method['name']),
						', '.join([
							'%s %s'%(fmtType(p['type']), p['name'])
							for p in method['params']
						]),
						' => %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
					))
			if cls['properties']:
				print("### Properties:")
				for prop in cls['properties']:
					print("[**%s**](%s): %s"%(
						'%s.%s'%(cls['name'], prop['name']),
						'doc:%s#%s'%(cls['docpage'], prop['name']),
						fmtType(prop['type'])
					))

			''' Print page contents (stubs) '''
			print("")
			for method in cls['methods']:
				print("# <a id='{0}'>{0}</a>({1}){2}".format(
					method['name'],
					', '.join([
						'%s %s'%(fmtType(p['type']), p['name'])
						for p in method['params']
					]),
					' => %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
				))
				if method['descr']:
					if method['descr']['brief']:
						print(method['descr']['brief'])
					if method['descr']['details']:
						print(method['descr']['details'])
				print("STUB")
				print("")


if __name__ == '__main__':
    os.chdir('../../')  # Navigate to root hifi directory
    autobuild()

    with PrintToFile('lastrun.log'):
    	scanner = DoxygenScanner('docs/xml')
    	scanner.loadIndex()
    loadApi('tools/docgen/hifi-docs.json', scanner)
