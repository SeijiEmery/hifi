
import os.path
from multiprocessing import Pool, Queue
from xml.etree import ElementTree
import re

class ConditionalTask(object):
	def __init__(self, task, runCondition, *args):
		self.task = task
		self.runCondition = runCondition
		self.args = args

	def tryRun(self):
		if self.runCondition():
			self.task(*self.args)
			return True
		return False

def _getNodeName(node, tag = 'name'):
	name = [ ''.join(elem.itertext()) for elem in node.iter(tag) ][0]
	return name

def _addToListByKey(dict_, key, value):
	if key in dict_:
		dict_[key] += [ value ]
	else:
		dict_[key] = [ value ]


def makeLookup(dict_):
	def lookup(key):
		return dict_[key]
	return lookup

def makeReverseLookup(elems):
	dict_ = {}
	for k, vs in elems:
		for v in vs:
			dict_[v] = k
	def lookup(key):
		return dict_[key]
	return lookup

def getInnerXml(node, preserveChildNodes = False, ignoredTags = None):
	nullGuard = lambda s: s if s is not None else ''
	def getInnerWithTags(node):
		if type(node) == str:
			return node
		text = nullGuard(node.text) + ''.join(map(getInnerWithTags, node))
		if ignoredTags and node.tag in ignoredTags:
			return text
		attribs = ' %s '%(' '.join([ '%s="%s"'%(k, v) for k, v in node.attrib.iteritems() ])) \
			if node.attrib else ''
		return '<%s%s>%s</%s>'%(node.tag, attribs, text, node.tag)

	def getInnerWithoutTags(node):
		if type(node) == str:
			return node
		return nullGuard(node.text) + ''.join(map(getInnerWithoutTags, node))

	if node is None or type(node) == str:
		return node
	return nullGuard(node.text) + ''.join(map( ((preserveChildNodes and getInnerWithTags) or getInnerWithoutTags), node))

def getChildNode(node, tag):
	for child in node.iter(tag):
		return child
	return None

def getChildInnerXml(node, tag, **kwargs):
	return getInnerXml(getChildNode(node, tag), **kwargs)





def loadIndex(xmlpath, index_file = 'index.xml'):
	''' Loads the doxygen index.xml file at index_path, and returns a dict representation
	of its contents, OR an exception if it fails. '''

	path  = os.path.join(xmlpath, index_file)
	index = ElementTree.parse(path).getroot()
	indexed_items = {}
	categorized_items = {}
	name_lookup = {}
	unhandledKinds = set()

	def warn(*args):
		print('WARNING: ' + ''.join(map(str, args)))

	def scanIndex(parseRules):
		for node in index.iter('compound'):
			if node.attrib['kind'] in parseRules:
				if parseRules[node.attrib['kind']] is None:
					print(node.attrib['kind'])
				parseRules[node.attrib['kind']](node)
			else:
				unhandledKinds.add(node.attrib['kind'])
		if unhandledKinds:
			print("UNHANDLED KINDS: %s"%(unhandledKinds))
		return {
			'index': indexed_items,
			'bycategory': categorized_items,
			'byname': name_lookup
		}
	# kindToCat = makeLookup({
	# 		'class': 'class',
	# 		'struct': 'struct',
	# 		'namespace': 'namespace',
	# 		'union': 'union',
	# 		'enum':  'enum'
	# 	})

	def scanContainer(typecat, member_map):
		''' Constructs a funciton that scans a doxygen class, struct, namespace, union, etc (container types) '''
		def scanNode(node):
			name, refid = _getNodeName(node), node.attrib['refid']
			ref = {
				'xmlpath': os.path.join(xmlpath, refid + '.xml'),
				'refid':   refid,
				'kind':    node.attrib['kind'],
				'name':	   _getNodeName(node),
				'members': dict([ (member.attrib['refid'], {
						'refid': member.attrib['refid'],
						'name':  name + '::' + _getNodeName(member),
						'kind':  member.attrib['kind']
					}) for member in node.iter('member') ])
			}
			indexed_items[refid] = ref
			_addToListByKey(categorized_items, typecat, refid)
			_addToListByKey(name_lookup, name, refid)
			for _, member in ref['members'].iteritems():
				cat = member_map[member['kind']]
				_addToListByKey(categorized_items, cat, member['refid'])
				_addToListByKey(name_lookup, member['name'], member['refid'])
		return scanNode

	scanClassNode = scanContainer('classes', {
		'property': 'properties',
		'variable': 'data_members',
		'function': 'methods',
		'slot':		'methods',
		'signal':	'methods',
		'typedef':  'typedefs',
		'enum':		'enums',
		'enumvalue':'enum_values',
		'union':	'unions',
		'class':	'classes',
		'struct': 	'classes',
		'friend':   'friend_decls'
	})
	scanNamespace = scanContainer('namespaces', {
		'variable':  'global_variables',
		'function':  'global_functions',
		'typedef':   'typedefs',
		'enum':  	 'enums',
		'enumvalue': 'enum_values'
	})
	scanUnion = scanContainer('unions', {
		'variable':  'global_variables',
		'function':  'global_functions',
		'typedef':   'typedefs',
		'enum':  	 'enums',
		'enumvalue': 'enum_values',
		'union':	 'union'
	})
	def warnNoScan(node):
		warn("Not parsing %s (%s)"%(_getNodeName(node), node))
	def ignore(node):
		pass
	return scanIndex({
		'struct':    scanClassNode,
		'class':     scanClassNode,
		'example':   ignore,
		'dir':       ignore,
		'union':     scanUnion,
		'namespace': scanNamespace,
		'file':      ignore, 	# source files + headers
		'page':      ignore,		# readmes, etc
	})

def fmtHumanReadableList(li):
	if len(li) > 2:
		return ', '.join(li[:-1]) + ', and ' + li[-1]
	return ' and '.join(li) if li else '[]'; 

print("Test: %s"%fmtHumanReadableList(['foo', 'bar', 'baz']))
print("Test: %s"%fmtHumanReadableList(['foo', 'bar']))
print("Test: %s"%fmtHumanReadableList(['foo']))
print("Test: %s"%fmtHumanReadableList([]))

class ClassParser:
	memberSectionKinds = staticmethod(makeReverseLookup([
		('methods', ['public-func', 'private-func', 'protected-func',
			'private-static-func', 'public-static-func', 'protected-static-func',
			'public-slot', 'private-slot', 'protected-slot', 'signal']),
		('members', ['public-attrib', 'private-attrib', 'protected-attrib',
			'public-static-attrib', 'private-static-attrib', 'protected-static-attrib']),
		('properties', ['property']),
		('friends', ['friend']),
		('types', ['public-type', 'private-type', 'protected-type'])
	]))

class NamespaceParser:
	memberSectionKinds = staticmethod(makeReverseLookup([
		('vars', ['vars']),
		('funcs', ['func']),
		('enums', ['enum']),
		('typedefs', ['typedef'])
	]))

class UnionParser:
	memberSectionKinds = staticmethod(makeReverseLookup([
		('union_members', ['public-attrib'])
	]))

class EnumParser:
	memberSectionKinds = staticmethod(makeReverseLookup([

	]))

def doxybool(val):
	if val == 'yes':
		return True
	if val == 'no':
		return False
	return val

def parseParams(node):
	typeConv = {
		'declname': 'name',
		'defname': 'name',
		'type': 'type',
		'array': 'type_array',
		'defval': 'default_value'
	}
	def parseParam(param):
		return dict([ (typeConv[elem.tag], getInnerXml(elem)) for elem in param ])
	return map(parseParam, node.iter('param'))

def loadClass(info):
	root = ElementTree.parse(info['xmlpath']).getroot()
	compound = [ node for node in root.iter('compounddef') if node.attrib['id'] == info['refid'] ][0]

	print("Loading %s"%(info['refid']))
	categorize = ClassParser.memberSectionKinds
	def parseSections(parsers):
		for section in compound.iter('sectiondef'):
			cat = categorize(section.attrib['kind'])
			map(parsers[cat], section.iter('memberdef'))
	obj = {
		'members': [],
		'methods': [],
		'properties': [],
		'used-types': [],
		'references': [],
		'referencedby': []
	}
	def parseVirtual(virt):
		if virt == 'virtual':
			return True
		if virt == 'non-virtual':
			return False
		return virt

	def parseMethod(node):
		name = _getNodeName(node)
		loc  = getChildNode(node, 'location')
		method = {
			'name': name,
			'kind': node.attrib['kind'],
			'type': getChildInnerXml(node,'type'),
			'params': parseParams(node),
			'const': doxybool(node.attrib['const']),
			'virtual': parseVirtual(node.attrib['virt']),
			'prot': doxybool(node.attrib['prot']),
			'static': doxybool(node.attrib['static']),
			'inline': doxybool(node.attrib['inline']),
			'file': loc.attrib['file'],
			'line': loc.attrib['line'],
			'description': {
				'brief': getChildInnerXml(node, 'briefdescription', preserveChildNodes=True).strip(),
				'details': getChildInnerXml(node, 'detaileddescription', preserveChildNodes=True).strip(),
				'inbody':  getChildInnerXml(node, 'inbodydescription', preserveChildNodes=True).strip()
			},
			'references': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref),
				'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else ''
			} for ref in node.iter('references')],
			'referencedby': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref)
			} for ref in node.iter('referencedby')]
		}
		# print(method)
		obj['methods'].append(method)

	def parseProperty(node):
		pass

	def tbd(cat, withObjectDump=False):
		if withObjectDump:
			def print_(node):
				print("%s: %s (TBD)\n\t%s"%(cat, node, node.__dict__))
		else:
			def print_(node):
				print("%s: %s (TBD)"%(cat, node))
		return print_

	internal_types = {}
	for type_ in compound.iter('type'):
		# print(type_.__dict__)
		ref = getChildNode(type_, 'ref')
		if ref is not None:
			internal_types[ref.attrib['refid']] = getInnerXml(type_, preserveChildNodes=False)
	# if internal_types:
	# print(compound.__dict__)
	print("\nUsed types: ")
	for k, v in internal_types.iteritems():
		print("\t'%s': (%s)"%(v, k))
	print('\n')

	obj['internal_types'] = internal_types

	parseSections({
		'methods': parseMethod,
		'members': tbd('member'),
		'properties': tbd('property'),
		'friends': tbd('friend'),
		'types': tbd('type')
	})

	all_references = {}
	all_referencedby = {}
	for method in obj['methods']:
		all_references.update(dict([ (ref['refid'], ref['name']) for ref in method['references'] ]))
		all_referencedby.update(dict([ (ref['refid'], ref['name']) for ref in method['referencedby'] ]))

	print("\nReferences:")
	for k, v in all_references.iteritems():
		print("\t'%s': (%s)"%(v, k))
	print("\nReferenced by:")
	for k, v in all_referencedby.iteritems():
		print("\t'%s': (%s)"%(v, k))
	print('')







	return obj


def loadCompoundFile(info, parser):
	root = ElementTree.parse(info['xmlpath']).getroot()

	categorize = parser.memberSectionKinds
	def parseSections(parsers):
		for section in root.iter('sectiondef'):
			map(parsers[categorize(section.attrib['kind'])], section.iter('memberdef'))

	def printAs(type_):
		def print_(node):
			print("%s: %s"%(type_, node))
		return print_

	def printWithDump(type_):
		def print_(node):
			print("%s: %s %s"%(type_, node, node.__dict__))
		return print_

	def parseClassMethod(node):
		pass

	def parseClassMember(node):
		pass

	def parseClassProperty(node):
		pass

	def parseClassFriend(node):
		pass

	def parseClassInnerType(node):
		pass

	def parseNamespaceVar(node):
		pass

	def parseNamespaceFunc(node):
		pass

	def parseNamespaceEnum(node):
		pass

	def parseNamespaceTypedef(node):
		pass

	def parseUnionMember(node):
		pass

	parseSections({
		'methods': parseClassMethod,
		'members': parseClassMember,
		'properties': parseClassProperty,
		'friends': parseClassFriend,
		'types':   parseClassInnerType,
		'vars': parseNamespaceVar,
		'funcs': parseNamespaceFunc,
		'enums': parseNamespaceEnum,
		'typedefs': parseNamespaceTypedef,
		'union_members': parseUnionMember
	})





def scanScriptableness(item):
	pass


class DoxygenScanner(object):
	''' Scans doxygen xml output. Does lazy loading + scanning of doxygen files to keep individual querries relatively fast.

	Has support for multithreaded, fully-parallel operations, but this has not been fully implemented yet. 
	'''
	def __init__(self, xmlpath):
		self.index = None
		self.name_lookup = None
		self.cat_lookup = None
		self.loaded_items = {}
		self.scanned_scriptable_items = {}
		self.xmlpath = xmlpath
		self.compoundParsers = {
			'class': ClassParser,
			'struct': ClassParser,
			'namespace': NamespaceParser,
			'enum':	EnumParser,
			'union': UnionParser
		}

	def loadIndex(self):
		if not self.index or not self.name_lookup or not self.cat_lookup:
			r = loadIndex(self.xmlpath)
			self.index = r['index']
			self.cat_lookup  = r['bycategory']
			self.name_lookup = r['byname']

			summary = [ '%s %s'%(len(v), k) for k, v in self.cat_lookup.iteritems() ]
			print('Indexed %s'%(fmtHumanReadableList(summary)))

			self.sanityCheckTypesAreNotAliased(['classes', 'namespaces', 'unions'])

			# print("\nNAME LOOKUP:")
			# for k, v in self.name_lookup.iteritems():
			# 	print("\t%s:\t%s\n"%(k, v))
			# print(self.name_lookup)

	def getType(self, typename):
		self.loadIndex()
		if typename not in self.name_lookup:
			return None
		if len(self.name_lookup[typename]) != 0:
			return None
		refid = self.name_lookup[typename][0]
		if not refid in self.loaded_items:
			self.loadItem(refid)
		return self.loaded_items[refid]

	def getScriptableInfo(self, typenames):
		self.loadIndex()
		# print([ [ self.index[refid] for refid in self.name_lookup[name] ] for name in typenames ])

		missing_types = [ typename for typename in typenames if typename not in self.name_lookup ]
		if missing_types:
			print("Missing types: %s"%(missing_types))
			return None
		aliased_types = [ typename for typename in typenames if len(self.name_lookup[typename]) != 1 ]
		if aliased_types:
			print("Aliased types: %s"%(aliased_types))
			return None
		refids = [ self.name_lookup[typename][0] for typename in typenames ]
		refids_to_load = [ refid for refid in refids if not refid in self.loaded_items ]
		refids_to_scan = [ refid for refid in refids if not refid in self.scanned_scriptable_items ]

		self.loadItemsAsync(refids_to_load)
		self.scanForScriptableItemsAsync( refids_to_scan, lambda refid: refid in self.loaded_items )
		self.launchAndAwaitTasks()

		non_scriptable_types = [ refid for refid in refids if not self.scanned_scriptable_items[refid]['is_scriptable'] ]
		if non_scriptable_types:
			print("Non scriptable types: %s"%(non_scriptable_types))
			return None

		return [ self.scanned_scriptable_items[refid] for refid in refids ]

	def loadItem(self, refid):
		item = self.index[refid]

		loaders = {
			'class': loadClass,
			'struct': loadClass,
			# 'namespace': loadNamespace,
			# 'enum': loadEnum,
			# 'union': loadUnion
		}
		if not item['kind'] in loaders:
			print("ERROR: Don't know how to load '%s'"%item['kind'])
			return
		r = loaders[item['kind']](item)
		self.loaded_items[refid] = None

	def scanForScriptableItem(self, refid):
		r = scanScriptableness(self.loaded_items[refid])
		self.scanned_scriptable_items[refid] = { 'is_scriptable': False }

	def loadItemsAsync(self, refids):
		map(self.loadItem, refids)

	def scanForScriptableItemsAsync(self, refids, condition = None):
		map(self.scanForScriptableItem, refids)

	def launchAndAwaitTasks(self):
		pass

	def sanityCheckTypesAreNotAliased(self, types_):
		badTypes = []
		for cat in types_:
			for thing in self.cat_lookup[cat]:
				if len(self.name_lookup[self.index[thing]['name']]) != 1:
					badTypes += [(cat, name)]
		if badTypes:
			print("Aliased types: ")
			for name in badTypes:
				print(name)
			assert(0 / 0)

	def getUsedSectionsByType(self, type_):
		section_kinds = set()
		parsed_files = 0
		for refid in self.cat_lookup[type_]:
			if not refid in self.index:
				print("Missing refid: %s (%s)"%(refid, type_))
				continue
			root = ElementTree.parse(self.index[refid]['xmlpath'])
			matching_compounds = [ node for node in root.iter('compounddef') if node.attrib['id'] == refid ]
			if len(matching_compounds) != 1:
				print("Bad file: %s (%s)"%(refid, type_))
				continue
			parsed_files += 1
			compound = matching_compounds[0]
			for section in compound.iter('sectiondef'):
				section_kinds.add(section.attrib['kind'])
		print("Parsed %d / %d %s"%(parsed_files, len(self.cat_lookup[type_]), type_))
		return section_kinds

	def debugGetSectionKindsForProject(self):
		''' Debug utility that scans all project files in category XYZ and prints out the section-types (kinds)
		that they use. Used to implement loadCompoundFile more efficiently. '''
		self.loadIndex()
		cats = [ 'classes', 'namespaces', 'unions', 'enums' ]
		for cat in cats:
			print("%s: "%cat)
			for kind in self.getUsedSectionsByType(cat):
				print("\t%s"%kind)
			print('')

	def debugPrintParamInnerTags(self):
		self.loadIndex()

		member_param_tags = {}
		member_tag_examples = {}

		parsed_files = 0
		for cls in self.cat_lookup['classes']:
			if not cls in self.index:
				print("Missing refid: %s (%s)"%(refid, "class"))
				continue
			root = ElementTree.parse(self.index[cls]['xmlpath'])
			matching_compounds = [ node for node in root.iter('compounddef') if node.attrib['id'] == cls ]
			if len(matching_compounds) != 1:
				print("Bad file: %s (%s)"%(cls, self.index[cls]['kind']))
				continue
			parsed_files += 1
			compound = matching_compounds[0]
			for section in compound.iter('sectiondef'):
				for member in section.iter('memberdef'):
					if not member.attrib['kind'] in member_param_tags:
						member_param_tags[member.attrib['kind']] = set()
					for param in member.iter('param'):
						for elem in param:
							member_param_tags[member.attrib['kind']].add(elem.tag)
						fmt = '%s: '%(section.attrib['kind'])
						fmt += ', '.join([ elem.tag for elem in param ])
						if not fmt in member_tag_examples:
							member_tag_examples[fmt] = getInnerXml(param, preserveChildNodes = True).strip() + '\n\t' + \
								getChildInnerXml(member, 'definition') + getChildInnerXml(member, 'argsstring')

		print("Parsed %d / %d files"%(parsed_files, len(self.cat_lookup['classes'])))

		print("Class/struct param tags by section:")
		for k, v in member_param_tags.iteritems():
			print("section '%s': %s"%(k, ', '.join(v)))
		print("Examples:\n")
		for k, v in member_tag_examples.iteritems():
			print("%s\n\t%s"%(k, v))






def autobuild ():
	''' Runs doxygen if the documentation has not already been built. '''
	if not os.path.isfile('docs/config.txt'):
		print('Missing doxygen config file')
		sys.exit(-1)

	if not os.path.isfile('docs/xml/index.xml'):
		print('Generating docs...')
		os.system('doxygen docs/config.txt')
		print('Generated docs in <hifi dir>/docs')

	assert(os.path.isfile('docs/xml/index.xml'))

if __name__ == '__main__':
	os.chdir('../../')	# Navigate to root hifi directory
	autobuild()

	scanner = DoxygenScanner('docs/xml')
	scanner.loadIndex()
	# scanner.debugPrintParamInnerTags()
	print("scanner.scanType('Application')")
	print(scanner.getScriptableInfo(["Application"]))
	print("scanner.scanType('EntityScriptingInterface')")
	scanner.getScriptableInfo(['EntityScriptingInterface'])

	# scanner.debugGetSectionKindsForProject()






























































