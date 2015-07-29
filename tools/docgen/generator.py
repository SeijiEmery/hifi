
import os.path
from scanner import DoxygenScanner, autobuild, convertType, script_api
# from itertools import filterfalse, tee
import json
import re
import textwrap

method_doc_template = '''
{decl} = function {name} {{
		
}};
'''.strip()


class_stub_template = '''
{decl} {name} = {{}};
'''.strip()

method_stub_template = '''
{decl} {name} = function ({args}) {{}};
'''.strip()

jsdoc_template = '''
/** {{brief}} {{lines}} */
'''.strip()


class JsdocGenerator(object):
	def __init__(self, config):
		self.config = config
		self.toJsType = convertType(knowntypes=set(script_api.keys()), builtintypes={
			'QVector': 'Array',
			'QString': 'string',
			'QStringList': 'string[]',
			'QVariant': 'object',
			'QVariantList': 'Array',
			'QVariantMap': 'object',
			'QScriptValue': 'object',
			'int':   'number',
			'unsigned int': 'number',
			'float': 'number',
			'bool': 'bool',
			'std::string': 'string',
			'std::vector': 'Array',
			'glm::vec3': '{x: number, y: number, z: number}',
			'glm::quat': '{x: number, y: number, z: number, w: number}',
			'glm::vec2': '{x: number, y: number, z: number}',
			'QObject *': 'object',
			'void': 'undefined'
		})

	def generate(self, scanner, typenames):
		scanOutput = scanner.runScriptTrace(typenames.keys())
		# typenames = dict((v, k) for k, v in typenames.iteritems())

		items = scanOutput['items']

		print("")
		print("GENERATING JSDOC")
		print("")

		def makeDocstring(lines):
			return '/** %s %s*/'%('\n * '.join(lines), '\n' if len(lines) > 1 else '')

		def fmtDescription(s, col_limit=100):
			s = s.replace('<para>', '<p>').replace('</para>', '</p>')
			return textwrap.wrap(s, col_limit, break_long_words=False, replace_whitespace=False)

		def getDescriptionLines(thing):
			if thing['description']['brief']:
				for l in fmtDescription(thing['description']['brief']):
					yield l
				yield ''
			if thing['description']['details']:
				for l in fmtDescription(thing['description']['details']):
					yield l

		def sanitizeName(name):
			return name.replace('function', 'func')

		jstypes = set()

		def fmtType(type_):
			jstype = self.toJsType(type_)
			if '{' in jstype and ']' in jstype:
				return 'Array'
			jstypes.add('{%s}'%jstype)
			return '{%s} '%jstype# if jstype != 'object' else ''

		def genClass(cls):
			if cls['name'] in typenames:
				clsname = typenames[cls['name']]
			elif cls['name'].split('::')[-1] in typenames:
				clsname = typenames[cls['name'].split('::')[-1]]
			else:
				clsname = cls['name'].replace('::', '.')
				print("%s not in %s"%(cls['name'], typenames.keys()))
			lines = [ '' ]
			# lines += [ cls['name'].split('::')[-1] ]
			lines += [ '@namespace ']
			if '.' in clsname:
				lines += [ '@memberof %s'%('.'.join(clsname.split('.')[:-1]))]
			# if len(cls['name'].split('::')) > 1:
				# lines += [ '@memberof %s'%('.'.join(cls['name'].split('::')[:-1])) ]
			lines += list(getDescriptionLines(cls))
			# lines += ['%s:%s'%(cls['file'], cls['line'])]
			if cls['scriptable']:
				for prop in cls['scriptable']['properties']:
					lines += ['@property %s%s'%(fmtType(prop['type']), sanitizeName(prop['name'].split('::')[-1]))]
			s = makeDocstring(lines) + '\n'
			s += 'var %s;'%(clsname.split('::')[-1])

			if cls['scriptable']:
				for method in cls['scriptable']['methods']:
					methodname = method['name'].split('::')[-1]
					s += '\n'
					lines = [ '' ]
					lines += list(getDescriptionLines(method))
					if method['kind'] in ('signal', 'slot'):
						lines += [ '@%s'%method['kind'] ]
					lines += [
						'@function %s'%methodname, 
						'@memberof %s'%clsname,
					]
					for p in method['params']:
						lines += ['@param %s%s'%(fmtType(p['type']), sanitizeName(p['name']))]
					if self.toJsType(method['type']) != 'undefined':
						lines += ['@returns {%s}'%(self.toJsType(method['type']))]
						jstypes.add('{%s}'%self.toJsType(method['type']))
					s += makeDocstring(lines) + '\n'
					s += '%s.%s = function(%s){};'%(clsname, methodname,
						', '.join([p['name'].replace('function', '_function') for p in method['params']]))
			return s

		def genNonScriptable(item):
			return ''
			name = sanitizeName(item['name']).replace('::', '.')
			s = ''
			if '.' in name:
				deps = name.split('.')
				s += 'var %s = {};\n'%(deps[0])
				for i in range(1, len(deps)):
					s += '%s = {};\n'%('.'.join(s[:i]))
			else:
				s = 'var '
			s += "/** %s %s (NON-SCRIPTABLE) */"%(item['kind'], sanitizeName(item['name'])) + '\n'
			s += "%s = {};"%(name) + '\n\n'
			return s

		def genEnum(item):
			return ''

		def genFunction(item):
			return ''

		generators = {
			'struct': genClass,
			'class':  genClass,
			'enum':   genEnum,
			'function': genFunction
		}

		s = ''
		print(items.keys())
		for item in items.itervalues():
			# print(item)
			print(item.keys())
			if 'scriptable' in item and item['scriptable']:
				s += generators[item['kind']](item)
			else:
				s += genNonScriptable(item)
		print(s)

		# print("js types:\n\t" + '\n\t'.join(jstypes))
		return s

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
	rs = generator.generate(scanner, script_api)

	with open('tools/docgen/jsdoc/api.js', 'w') as f:
		f.write(rs)
	print("Wrote to tools/docgen/jsdoc/api.js")




