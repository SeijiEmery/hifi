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
	warnings = []
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
		interface_list = []
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
			interface_list.append(item)

		required_keys = [ 'name', 'kind', 'cppname' ]
		for item in config['custom_interfaces']:
			missing_keys = [ key for key in required_keys if key not in item ]
			if missing_keys:
				warnings += ["WARNING: Interface '%s' defined in 'custom_interfaces' missing keys %s (has keys %s)"%(
					item['name'] if 'name' in item else '<unknown>', missing_keys, item.keys())]
				continue
			if not 'methods' in item:
				item['methods'] = []
			if not 'properties' in item:
				item['properties'] = []
			if not 'docpage' in item:
				item['docpage'] = None
			item['loaded'] = True
			interfaces[name] = item
			interface_list.append(item)

		interface_blacklist = set(config['interface_blacklist'])
		unused_blacklist_names = []
		warn_unused_blacklist = config['warn_unused_interface_blacklist'] \
			if 'warn_unused_interface_blacklist' in config else False

		unused_blacklist = [ x for x in interface_blacklist if not x in interfaces ]
		interface_list   = [ item for item in interface_list if not item['name'] in interface_blacklist ]
		if warn_unused_blacklist and len(unused_blacklist) != 0:
			warnings += ["WARNING: Unused interface blacklist items: [%s]"%(', '.join(unused_blacklist))]
	except KeyError as e:
		print("Bad config file")
		raise e

	interface_cpp = { x['cppname']: x for x in interfaces.itervalues() }

	''' Scan for script values and print run results to a log file '''
	with PrintToFile('lastrun.log', 'a+', True):
		scan_results = scanner.runScriptTrace(interface_cpp.keys())

	def restricted_dict(d, ks):
		''' Returns a dict containing only the specified elements ks from d '''
		return { k: v for k, v in d.iteritems() if k in ks }

	def convType(t):
		return t

	def getDescription(thing):
		d = thing['description']
		return d if d['brief'] or d['details'] or d['inbody'] else None

	''' Pull out the info we need from scan_results '''
	scanned_types = {}

	def parse_scan_results(warnings):
		def parse_method(method, name):
			return {
				'name': method['name'].split('::')[-1],
				'isSignal': method['kind'] == 'signal',
				'return': convType(method['type']),
				'params': [{ 'name': p['name'], 'type': p['type'] } for p in method['params'] ],
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

		l = []
		# for item in interface_list:
		indexed_scan_results = { x['name']: x for x in scan_results['items'].itervalues() }
		parsed_scan_results = set()


		loaded_interface_items = []
		for thing in interface_list:
			if thing['loaded']:
				loaded_interface_items.append(thing)
				continue
			if not thing['cppname'] in indexed_scan_results:
				warnings += [ 'WARNING: could not load %s (%s)'%(thing['cppname'], thing['name'])]
				continue

			item = indexed_scan_results[thing['cppname']]
			if item['kind'] in ('struct', 'class'):
				thing.update(parse_class(item, thing['name']))
				loaded_interface_items.append(thing)
			else:
				warnings += ["WARNING: Unhandled interface kind '%s': "%(item['kind'])]
			parsed_scan_results.add(item['name'])

		unparsed_scan_results = { 
			k: v 
			for k, v in indexed_scan_results.iteritems() 
			if k not in parsed_scan_results
		}
		if unparsed_scan_results:
			warnings += [ 'WARNING: unused scanned items: %s'%(', '.join(unparsed_scan_results.keys()))]

		return loaded_interface_items

	interface_list = parse_scan_results(warnings)

	non_loaded = [ x['name'] for x in interfaces.itervalues() if not x['loaded'] ]
	if non_loaded:
		warnings += ["WARNING: The following class interfaces were not found:\n\t%s"%', '.join(non_loaded)]
		interfaces = { k: v for k, v in interfaces.iteritems() if v['loaded'] }

	types = {}
	for k, v in config['types'].iteritems():
		if type(v) in (str, unicode):
			types[k] = { "name": v, "link": None }
		else:
			print(type(v))
			types[k] = { "name": v["name"], "link": v["link"] }

	types.update({ x['cppname']: { 'name': x['name'], 'link': x['docpage'] } for x in interface_list })
	toJsType = convertType({}, builtintypes = dict([ (k, v["name"]) for k, v in types.iteritems() ]))
 
	linked_types = { x['name']: x['link'] for x in types.itervalues() }


	unknown_types = set()
	def fmtType(t):
		t = toJsType(t).strip()
		if '[]' in t and '[]' not in t.strip('[]'):	# Replace this w/ proper regexes later
			return fmtType(t.strip('[]')) + '[]'
		if '.' in t:
			return '.'.join(map(fmtType, t.split('.')))
		if t in linked_types and linked_types[t]:
			return '[%s](doc:%s)'%(t, linked_types[t])
		if t not in linked_types:
			unknown_types.add(t)
			# print("UNKNOWN TYPE: %s"%t)
		return t
	def printUnknownTypes():
		if unknown_types:
			print("UNKNOWN TYPES: %s"%(', '.join(unknown_types)))
			print('(These types will be used but are not linkable. Add them to <config>.json "types" or "custom_interfaces" to fix)')
			print('If some of these are hifi interfaces, check your "interfaces"/"custom_interfaces" sections for errors. ' + \
		          'If this is not the case, there may be a problem within the python script itself.')
			print("")

	def fmtMethod_jsStyle(method, name, link):
		return "[**%s**](%s) (%s)%s"%(
			name,
			link,
			', '.join([
				'%s: %s'%(p['name'], fmtType(p['type']))
				for p in method['params']
			]),
			': %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else '')
	def fmtMethod_cStyle(method, name, link):
		return "%s[**%s**](%s) (%s)"%(
			' %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else '',
			name,
			link,
			', '.join([
				'%s %s'%(fmtType(p['type'], p['name']))
				for p in method['params']
			]))
	def fmtMethod_arrowStyle(method, name, link):
		return "[**%s**](%s) (%s)%s"%(
			name,
			link,
			', '.join([
				'%s %s'%(fmtType(p['type']), p['name'])
				for p in method['params']
			]),
			' => %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else '')

	def fmtProperty_jsStyle(prop, name, link):
		print(prop)
		return '[**%s**](%s): %s'%(name, link, fmtType(prop['type']))
	def fmtProperty_cStyle(prop, name, link=None):
		return '%s [**%s**](%s)'%(link, fmtType(prop['type']), name)

	def fmtMethodDefn_jsStyle(method):
		return "<a id='%s'>%s</a> (%s)%s"%(
			method['name'], method['name'], ', '.join([ '%s: %s'%(p['name'], fmtType(p['type'])) for p in method['params'] ]),
			': %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
		)
	def fmtMethodDefn_cStyle(method):
		return "%s<a id='%s'>%s</a> (%s)"%(
			'%s '%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else '',
			method['name'], method['name'],
			', '.join([ '%s %s'%(p['type'], p['name']) for p in method['params'] ]) 
		)
	def fmtMethodDefn_arrowStyle(method):
		return "<a id='%s'>%s</a> (%s)%s"%(
			method['name'], method['name'], ', '.join([ '%s %s'%(p['type'], fmtType(p['name'])) for p in method['params'] ]),
			'=> %s'%(fmtType(method['return'])) if fmtType(method['return']) != 'undefined' else ''
		)
	def fmtPropertyDefn_jsStyle(prop):
		return "<a id='%s'>%s</a>: %s"%(prop['name'], prop['name'], fmtType(prop['type']))
	def fmtPropertyDefn_cStyle(prop):
		return "%s <a id='%s'>%s</a>"%(fmtType(prop['type']), prop['name'], prop['name'])

	fmtMethod = fmtMethod_jsStyle
	fmtProperty = fmtProperty_jsStyle
	fmtMethodDefn = fmtMethodDefn_jsStyle
	fmtPropertyDefn = fmtPropertyDefn_jsStyle

	print("")
	print("Generating api-reference.txt")
	with PrintToFile("tools/docgen/generated/api-reference.txt", duplicate_to_stdout=True):
		for cls in interface_list:
			print("")
			print("# %s"%cls['name'])
			for method in cls['methods']:
				print("%s %s"%(
					'function' if not method['isSignal'] else 'signal',
					fmtMethod(
						method, 
						'%s.%s'%(cls['name'], method['name']),
						'doc:%s#%s'%(cls['docpage'], method['name'])
					)))
			for prop in cls['properties']:
				print("property %s"%(fmtProperty(
					prop, 
					'%s.%s'%(cls['name'], prop['name']),
					'doc:%s#%s'%(cls['docpage'], prop['name'])
				)))
	for cls in interfaces.itervalues():
		print("Generating stub: %s.txt"%(cls['docpage']))
		with PrintToFile("tools/docgen/generated/%s.txt"%(cls['docpage']), duplicate_to_stdout=False):
			methods = [ method for method in cls['methods'] if not method['isSignal'] ]
			signals = [ method for method in cls['methods'] if method['isSignal'] ]

			''' Print page header / summary '''
			print("## Description:")
			print("STUB")
			print("")

			if methods:
				print("### Functions:")
				for method in methods:
					print("function %s"%fmtMethod(method, '%s.%s'%(cls['name'], method['name']), link='#%s'%(method['name'])))
			if signals:
				print("### Signals:")
				for method in methods:
					print("signal %s"%fmtMethod(method, '%s.%s'%(cls['name'], method['name']), link='#%s'%(method['name'])))
			if cls['properties']:
				print("### Properties:")
				for prop in cls['properties']:
					print(fmtProperty(prop, '%s.%s'%(cls['name'], prop['name']), link='#%s'%(prop['name'])))

			''' Print page contents (stubs) '''
			print("")
			for method in cls['methods']:
				print("# %s"%(fmtMethodDefn(method)))
				# if method['descr']:
				# 	if method['descr']['brief']:
				# 		print(method['descr']['brief'])
				# 	if method['descr']['details']:
				# 		print(method['descr']['details'])
				print("STUB")
				print("")
	print('')
	print('\n'.join(warnings))
	print('')
	printUnknownTypes()


if __name__ == '__main__':
    os.chdir('../../')  # Navigate to root hifi directory
    autobuild()

    with PrintToFile('lastrun.log'):
    	scanner = DoxygenScanner('docs/xml')
    	scanner.loadIndex()
    loadApi('tools/docgen/hifi-docs.json', scanner)
