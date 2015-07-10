
import os.path
from scanner import ScriptApiScanner
import json
import re

''' Config '''
STRIP_CONST_REF = True




''' 
TODO:
- Overloads
- Specify types externally
- Scan for internal types

'''


class JsdocGenerator:
	def __init__ (self, jsconfig):
		with open(jsconfig, 'r') as f:
			self.jsconfig = json.load(f)

	def generate (self, scannedContent):
		xmlclasses = dict(scannedContent)
		classes = {}
		all_exposed_types = set()

		for v in self.jsconfig['global-objects']:
			cppname, jsname = v['cpp'], v['js']
			classxml = xmlclasses[cppname]

			getelem = lambda dict_, key: dict_[key] if key in dict_ else {}

			methodxml = getelem(classxml, 'exposed_methods').copy()
			slots     = getelem(classxml, 'exposed_slots')
			methodxml.update(slots)
			properties = getelem(classxml, 'exposed_properties')
			
			print(classxml['class'].__dict__)
			classinfo = {
				'name': jsname,
				'id':   classxml['class'].attrib['id'],
				'dependencies': {},
				'exposed-types': set([]),
				'methods': {}
			}
			classes[jsname] = classinfo

			for name, node in methodxml.iteritems():
				method = self.parseMethod(node)
				classinfo['methods'][name] = method

				classinfo['dependencies'].update(method['references'])
				if method['returntype']:
					classinfo['exposed-types'].add(self.toJsType(method['returntype'], stripConstRef = True))
				for param in method['params']:
					classinfo['exposed-types'].add(self.toJsType(param['type'], stripConstRef = True))

				print("METHOD")
				for k, v in method.iteritems():
					print('\t%s: %s'%(k, v))

			all_exposed_types |= classinfo['exposed-types']

			print('class %s'%classinfo['name'])
			print('\tid: %s'%classinfo['id'])
			print('\texposed types:')
			for t in classinfo['exposed-types']:
				print('\t\t%s'%(t))
			print('\tdepends on:')
			for k, v in classinfo['dependencies'].iteritems():
				print('\t\t%s: %s'%(k, v))
			print('\tmethods:')
			for k, v in classinfo['dependencies'].iteritems():
				print('\t\t%s: %s'%(k, v))

		print('exposed types:\n\t%s'%('\n\t'.join(all_exposed_types)))

		for _, class_ in classes.iteritems():
			print("var %s = {\n\t// native class\n};"%(class_['name']))
			for _, method in class_['methods'].iteritems():
				print(self.generateMethodDocstring(method))
				print(self.generateMethodStub(class_['name'], method))

				# print('method %s:'%name)
				# self.parseMethod(node, jsname)
				# print('method %s:\n\t%s\n'%(name, node.__dict__))

			for name, node in properties.iteritems():
				print('property %s:\n\t%s\n'%(name, node.__dict__))


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

	def generateMethodDocstring(self, method):
		docstring = '/** ' + (method['brief'] or '\n')
		
		for line in method['details']:
			docstring += ' * %s\n'%(line)

		for param in method['params']:
			assert(param['name'] and param['type'])
			s = '@param %s %s'%(self.toJsType(param['type']), param['name'])
			if 'defaultvalue' in param.keys():
				s += ' = %s'%param['defaultvalue']
			if 'description' in param.keys():
				s += ' ' + param['description']
			docstring += ' * %s\n'%(s)
		if method['returntype']:
			docstring += ' * @returns %s\n'%(method['returntype'])
		docstring += ' */'
		return docstring

	def generateMethodStub(self, objdecl, method):
		params = ', '.join([ param['name'] for param in method['params'] ])
		rval = self.defaultValueForJsType(method['returntype'])

		return ('%s.%s = function (%s) {\n' 	    + \
			    '    // native code\n' 			+ \
			    '    // (%s:%s)\n' 			    + \
			    ('    return %s;\n' % rval if rval else '') + \
			    '};') % (objdecl, method['name'], params, method['file'], method['line'])

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
				'undefined': None
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
		return None

if __name__ == '__main__':
	generator = JsdocGenerator('interface-api.json')

	os.chdir('../../')		# cd to root dir
	scanner = ScriptApiScanner('docs/xml')

	generator.generate(scanner.scanAllFiles())


