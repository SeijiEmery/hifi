
import os.path
from scanner import DoxygenScanner, autobuild
# from itertools import filterfalse, tee
import json
import re


''' Config '''
STRIP_CONST_REF = True


# Utility functions

# #https://docs.python.org/dev/library/itertools.html#itertools-recipes
# def partition(pred, iterable):
#     'Use a predicate to partition entries into false entries and true entries'
#     # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
#     t1, t2 = tee(iterable)
#     return filterfalse(pred, t1), filter(pred, t2)

def partition(pred, iterable):
	return [ x for x in iterable if pred(x) ], [ x for x in iterable if not pred(x) ]










''' 
TODO:
- Overloads
- Specify types externally
- Scan for internal types

'''

'''
class JsdocGenerator:
	def __init__ (self, jsconfig):
		with open(jsconfig, 'r') as f:
			self.jsconfig = json.load(f)

	def generate(self, apiScanner):
		classes, externals = [], set()

		for _class in self.jsconfig['global-objects']:
			exposedClasses, externalTypes = apiScanner.scanExposedClass(_class['cpp'])
			classes    += exposedClasses
			externals  |= externalTypes

		int_types    = [ 'int', 'uint', 'quint32', 'unsigned int', 'quint64', 'uint16_t', 'unsigned char' ]
		float_types  = [ 'float' ]
		string_types = [ 'QString', 'std::string', 'string' ]
		qvector_types = [ 
			('int', '0'),
			('glm::vec3', '{ x: 0.0, y: 0.0, z: 0.0 }'),
			('QUuid', '')
		]

		builtins = \
			[ (int_type, 'Number', '0') for int_type in int_types ] + \
			[ (float_type, 'Number', '0.0') for float_type in float_types ] + \
			[ (string_type, 'String', '""') for string_type in string_types ] + \
			[ ('QVector< %s >'%type_, '%s[]'%type_, "[ %s ]"%val) for type_, val in qvector_types ] + \
			[ 
				('void', 'undefined', 'undefined'),
				('bool', 'bool', 'false'),
				('glm::vec3', 'glm::vec3', '{ x: 0.0, y: 0.0, z: 0.0 }'),
				('glm::quat', 'glm::quat', '{ x: 0.0, y: 0.0, z: 0.0, w: 0.0 }'),
				('QUuid', 'QUuid', '{}'),
				('QByteArray', 'QByteArray', '[]'),
				('QVariantMap', 'Object', '{}')
			]
		
		jstypes = dict([ (cpptype, jstype) for cpptype, jstype, _ in builtins ])
		jsvals  = dict([ (jstype, val)     for _, jstype, val in builtins ])

		for cls in classes:
			jstypes[cls['name']] = cls['name']
			jsvals [cls['name']] = 'new %s()'%(cls['name'])

		classes = dict([ (cls['name'], cls) for cls in classes ])

		undefined_externals = filter(lambda type_: type_ not in jstypes, externals)
		print("Undefined external types:\n\t%s"%(', '.join(undefined_externals)))

		for thing in undefined_externals:
			jstypes[thing] = thing
			jsvals [thing] = 'undefined'

		global_object_list = [ cls_['cpp'] for cls_ in self.jsconfig['global-objects'] ]

		global_objects  = [ class_ for class_ in classes.itervalues() if class_['name'] in global_object_list ]
		exposed_classes = [ class_ for class_ in classes.itervalues() if class_['name'] not in global_object_list ]

		header = ''
		body   = ''

		for obj in self.jsconfig['global-objects']:
			name, cls = obj['js'], classes[obj['cpp']]

			header += '\n/** @namespace */'
			header += '\nvar %s = {'%(cls['name'])

			print("EXPOSED_METHODS: ")
			print(cls['members']['exposed_methods'])
			print(cls['members']['exposed_slots'])
			print(cls['members']['exposed_signals'])
			print('')

			print("EXPOSED ATTRIBUTES: ")
			print(cls['members']['exposed_attribs'])
			print(cls['members']['exposed_properties'])
			print('')

			for attrib in (cls['members']['exposed_attribs'] + cls['members']['exposed_properties']):
				header += '\n\t"this.%s": %s'%(attrib['name'], jsvals[jstypes[apiScanner.toJsType(attrib['type'])]])
			header += '};\n'

			methods = cls['members']['exposed_methods'] + cls['members']['exposed_slots'] + cls['members']['exposed_signals']
			for method in methods:
				rval, _ = method['jstype']
				body += self.generateMethodDocstring(method, ['@static']) + '\n'
				body += self.generateMethodStub(name, method, jsvals[jstypes[rval]]) + '\n\n'
				
		for cls in exposed_classes:
			header += '\n/** @constructor */\n'
			header += 'var %s = function () {'%(cls['name'])
			for attrib in (cls['members']['exposed_attribs'] + cls['members']['exposed_properties']):
				try:
					header += '\n\tthis.%s = %s;'%(attrib['name'], jsvals[jstypes[apiScanner.toJsType(attrib['type'])]])
				except KeyError:
					print("Unknown type: %s"%attrib['type'])
			header += '\n};\n'

			methods = cls['members']['exposed_methods'] + cls['members']['exposed_slots'] + cls['members']['exposed_signals']# + \
			#		  cls['members']['non_exposed_methods']
			for method in methods:
				# print(method)
				rtype, _ = method['jstype']
				body += self.generateMethodDocstring(method) + '\n'
				if rtype and rtype in jstypes:
					rval = jsvals[jstypes[rtype]]
				elif rtype:
					print("Missing type '%s'"%rtype)
					rval = None
				else:
					rval = None
				body += self.generateMethodStub('%s.prototype'%cls['name'], method, rval) + '\n\n'

		print(header)
		print(body)

	def parseMethod(self, node):
		method = {
			'name': None,
			'params': [],
			'returntype': None,
			'file': None,
			'line': None,
			'brief': None,
			'details': None,
			'docstring': None,
			'references': {},
		}

		def innertext(node):
			if type(node) == str:
				return str
			if node.tag == 'para':
				return '\n%s%s'%(node.text, ''.join(map(innertext, node)))
			if node.tag == 'ref':
				return '%s%s'%(node.text, ''.join(map(innertext, node)))
			if node.text:
				return node.text + ''.join(map(innertext, node))
			return ''.join(map(innertext, node))
			# return repr(node.__dict__)

		# Used types.
		param_types = {
			'type': 			'type',
			'declname': 		'name',
			'defname':			'name',
			'briefdescription': 'description',
			'defval':			'defaultvalue'
		}
		# All types:
		# type, declname, defname, array, defval, briefdescription

		simple_tags = {
			'name': 'name',
			'detaileddescription': 'details',
			'briefdescription':	'brief'
		}
		ignored = set([
			'argsstring',
			'definition'
		])

		for elem in node:
			if elem.tag in simple_tags:
				method[simple_tags[elem.tag]] = innertext(elem).strip()
			elif elem.tag in ignored:
				pass
			elif elem.tag == 'param':
				param = {}
				for el in elem:
					try:
						key = param_types[el.tag]
					except KeyError, e:
						print("Unknown tag: '%s': '%s'"%(el.tag, innertext(el)))
						raise e
					if key in param:
						params.append(param)
						param = {}
					if key == 'type':
						param[key] = self.toJsType(innertext(el))
					else:
						param[key] = innertext(el)
				if param:
					method['params'].append(param)
			elif elem.tag == 'type':
				method['returntype'] = self.toJsType(innertext(elem))
			elif elem.tag == 'references':
				method['references'][elem.text] = elem.attrib['refid']
			elif elem.tag == 'location':
				method['file'] = elem.attrib['file']
				method['line'] = elem.attrib['line']
			elif elem.tag == 'inbodydescription':
			 	if len([ e for e in elem ]) != 0:
					print('inbodydescription: %s'%[e for e in elem ])
			else:
				print("Unknown elem '%s': %s"%(elem.tag, repr(elem.__dict__)))
		return method

	def generateMethodDocstring(self, method, injected_lines = None):
		docstring = '/** ' + (method['brief'] or '\n')
		if method['details']:
			for line in method['details']:
				docstring += ' * %s\n'%(line)

		rtype, params = method['jstype']

		# print(params)
		for line in injected_lines:
			docstring += ' * %s\n'%(line)
		for param in params:
			name = param['declname'] if 'declname' in param else param['defname']
			s = '@param {%s} %s'%(self.toJsType(param['type']).replace(':', '_'), name)
			if 'defaultvalue' in param.keys():
				s += ' = %s'%param['defaultvalue']
			if 'description' in param.keys():
				s += ' ' + param['description']
			docstring += ' * %s\n'%(s)
		injected_lines = injected_lines or []
		if rtype and rtype != 'void':
			docstring += ' * @return {%s}\n'%(rtype.replace(':', '_'))
		docstring += ' */'
		return docstring

	def generateMethodStub(self, objdecl, method, rval):
		rtype, params = method['jstype'] if 'jstype' in method else method['type']
		params = ', '.join([ (param['declname'] if 'declname' in param else param['defname']) for param in params ])

		return ('%s.%s = function (%s) {\n' 	    + \
			    '    // native code\n' 			+ \
			    ('    // (%s:%s)\n' and '')	    + \
			    ('    return %s;\n' % rval if (rval and rval != 'undefined') else '') + \
			    '};') % (objdecl, method['name'], params)#, '', 0)#method['file'], method['line'])

	def toJsType (self, cpptype, stripConstRef = False):
		# print(cpptype)
		decorators = ['Q_INVOKABLE', 'SCRIPT_API']
		for decorator in decorators:
			cpptype = cpptype.replace(decorator, '')

		# cpptype = re.sub(r'(\s+[\<\>\(\)\&\*]\s*)', r'\1', cpptype)
		# cpptype = re.sub(r'([\<\>\(\)\&\*])\s+', r'\1', cpptype)

		if STRIP_CONST_REF or stripConstRef:
			cpptype = re.sub(r'const\s+(.+)\s*&', r'\1', cpptype)
			cpptype = re.sub(r'const\s+(.+)', r'\1', cpptype)
		return cpptype.strip()

	def defaultValueForJsType(self, type_):
		if 'jsTypeValues' not in self.__dict__:
			qt_builtins = {
				'QVector': '[]',
				'QString': '""',
				'QVariantMap': '{}',
				'QUuid': '{}',
			}
			primitives = {
				'int':   "0",
				'float': '0.0',
				'bool':  'false',
				'void': None
			}
			metatypes = {
				'glm::vec3': '{ x: 0.0, y: 0.0, z: 0.0 }',
				'glm::quat': '{ x: 0.0, y: 0.0, z: 0.0, w: 0.0 }'
			}
			builtins = {}
			builtins.update(qt_builtins)
			builtins.update(primitives)
			builtins.update(metatypes)
			self.jsTypeValues = builtins
		else:
			builtins = self.jsTypeValues

		templated_builtins = {
			'QVector': '[ %s ]'
		}

		# Try to deal with templates...
		if '<' in type_:
			template_type = type_.split('<')[0]
			if template_type in builtins and template_type in templated_builtins:
				inner_type = type_.split(template_type)[1].strip('<> \t\n')

				inner_type = self.defaultValueForJsType(inner_type)
				if not inner_type:
					print("ERROR: Tried to template '%s', but '%s' is not a valid type"%(template_type, inner_type))
				else:
					return templated_builtins[template_type] % inner_type
			elif template_type in builtins:
				print("ERROR: %s is not a templated type"%(template_type))
		if type_ in builtins:
			return builtins[type_]

		print("ERROR: Unknown type '%s'"%type_)
		return None
'''

class JsdocGenerator(object):
	def __init__(self, config):
		self.config = config

	def generate(self, scanner, entrypoints):
		items = scanner.runScriptTrace(entrypoints.values())

		print("")
		print("GENERATING JSDOC")
		print("")

		def genClass(cls):
			doc =  "/** %s %s \n"
			if cls['description'] and cls['description']['brief']:
				doc += " * %s\n"%(cls['description']['brief'])
			doc += "  * @class \n";
			doc += " */\n"
			stub = "var %s = function(){};"%(cls['name'].replace('::', '.'))

			s = '%s\n%s\n\n'%(doc, stub)
			for method in cls['scriptable']['methods']:
				pass

			return "CLASS %s\n"%(cls['name'])

		def genNonScriptable(item):
			doc = "/** %s %s (NON-SCRIPTABLE) */"%(item['kind'], item['name'])
			stub = "var %s = function(){};"%(item['name'].replace('::', '.'))
			return '%s\n%s\n\n'%(doc, stub)

		generators = {
			'struct': genClass,
			'class':  genClass,
		}

		s = ''
		for item in items['items'].itervalues():
			if item['scriptable']:
				s += generators[item['kind']](item)
			else:
				s += genNonScriptable(item)
		print(s)

	def generateMethodStub(self, objdecl, method, rval):
		rtype, params = method['jstype'] if 'jstype' in method else method['type']
		params = ', '.join([ (param['declname'] if 'declname' in param else param['defname']) for param in params ])

		return ('%s.%s = function (%s) {\n' 	    + \
			    '    // native code\n' 			+ \
			    ('    // (%s:%s)\n' and '')	    + \
			    ('    return %s;\n' % rval if (rval and rval != 'undefined') else '') + \
			    '};') % (objdecl, method['name'], params)#, '', 0)#method['file'], method['line'])


if __name__ == '__main__':
	generator = JsdocGenerator('interface-api.json')

	os.chdir('../../')		# cd to root dir
	autobuild()
	scanner = DoxygenScanner('docs/xml')
	generator.generate(scanner, {
		'Entities': 'EntityScriptingInterface',
		'Scene': 'SceneScriptingInterface',
		'Script': 'ScriptEngine'
	})



