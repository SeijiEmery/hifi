
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
			'int':   'number',
			'unsigned int': 'number',
			'float': 'number',
			'bool': 'bool',
			'std::string': 'string',
			'std::vector': 'Array',
			'glm::vec3': 'glm.vec3',
			'glm::quat': 'glm.quat',
			'glm::vec2': 'glm.vec2',
			'QObject *': 'object',
			'void': 'undefined'
		})

	def generate(self, scanner, entrypoints):
		scanOutput = scanner.runScriptTrace(entrypoints.keys())
		items = scanOutput['items']

		print("")
		print("GENERATING JSDOC")
		print("")

		def makeDocstring(lines):
			return '/** %s %s*/'%('\n * '.join(lines), '\n' if len(lines) > 1 else '')

		def fmtDescription(s, col_limit=100):
			s = s.replace('<para>', '').replace('</para>', '')
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


		def genClass(cls):
			lines = ['', '@namespace'] + list(getDescriptionLines(cls))
			# lines += ['%s:%s'%(cls['file'], cls['line'])]
			s = ''

			if cls['scriptable']:
				for prop in cls['scriptable']['properties']:
					lines += ['@property {%s} %s'%(self.toJsType(prop['type']), sanitizeName(prop['name']))]
			s += makeDocstring(lines) + '\n'
			s += class_stub_template.format(
				decl= 'var',
				name= sanitizeName(cls['name'])
			) + '\n'

			if cls['scriptable']:
				for method in cls['scriptable']['methods']:
					s += '\n'
					lines = [
						'',
						'%s %s.%s'%(method['kind'], cls['name'], method['name'])
					]
					lines += list(getDescriptionLines(method))
					lines += [
						'@function %s'%method['name'], 
						'@memberof %s'%cls['name'],
						'@static'
					]

					for p in method['params']:
						lines += ['@param {%s} %s'%(self.toJsType(p['type']), sanitizeName(p['name']))]
					if method['type']:
						lines += ['@return {%s}'%(self.toJsType(method['type']))]
					lines += [
						'',
						'%s:%s'%(method['file'], method['line'])
					] 
					s += makeDocstring(lines) + '\n'
			return s

		def genNonScriptable(item):
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




