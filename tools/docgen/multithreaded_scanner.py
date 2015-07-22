
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
	scanUnion     = scanContainer('unions', {
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

def classParserInfo():
	member_categories = makeReverseLookup([
		('exposed_methods', []),
		('exposed_attribs', ['public-attrib']),
		('exposed_signals', ['signal']),
		('exposed_slots', ['public-slot']),
		('exposed_properties', ['property']),
		('non_exposed_methods', [
			'func', 'public-func', 'private-func', 'protected-func', 'package-func',
			'public-static-func', 'private-static-func', 'protected-static-func', 'package-static-func']),
		('non_exposed_attribs', [
			'var', 'private-attrib', 'protected-attrib', 'package-attrib',
			'public-static-attrib', 'private-static-attrib', 'protected-static-attrib', 'package-static-attrib']),
		('non_exposed_slots', ['private-slot', 'protected-slot']),
		('non_exposed_signals', []),
		('non_exposed_properties', []),
		('unused', [
			'user-defined', 'typedef', 'public-type', 'private-type', 'package-type', 'protected-type',
			'dcop-func', 'event', 'friend', 'related', 'define', 'prototype', 'enum'])
	])
	def get():
		return member_categories
	return get
classParserInfo = classParserInfo()

def loadCompoundFile(info):
	root = ElementTree.parse(info['xmlpath']).getroot()

	def multiplexWithScope(member_type, scope_types):
		return [ '%s-%s'%(scope, member_type) for scope in scope_types ]

	categorize = makeReverseLookup([
		('methods', ['func', 'public-func', 'private-func', 'protected-func', 'package-func',
				'public-static-func', 'private-static-func', 'protected-static-func', 'package-static-func',
				'signal', 'public-slot', 'private-slot', 'protected-slot']),
		('members', ['var', 'public-attrib', 'private-attrib', 'protected-attrib', 'package-attrib']),
		('properties', ['property']),
		('typedefs', ['typedef']),
		('enums', ['enum']),
		('unused', ['user-defined', 'public-type', 'private-type', 'package-type', 'protected-type',
			'dcop-func', 'event', 'friend', 'related', 'define', 'prototype'])
	])

	def parseSections(section_parsers):
		for section in root.iter('sectiondef'):
			map(section_parsers[categorize(section.attrib['kind'])], section.iter('memberdef'))

	def printAs(type_):
		def print_(node):
			print("%s: %s"%(type_, node))
		return print_


	parseSections({
		'methods': printAs("method"),
		'members': printAs("member"),
		'properties': printAs("property"),
		'typedefs': printAs("typedef"),
		'enums': printAs("enum"),
		'unused': printAs("unused")
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
		r = loadCompoundFile(self.index[refid])
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
		self.loadIndex()
		cats = [ 'classes', 'namespaces', 'unions', 'enums' ]
		for cat in cats:
			print("%s: "%cat)
			for kind in self.getUsedSectionsByType(cat):
				print("\t%s"%kind)
			print('')

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
	# scanner.getScriptableInfo(['EntityScriptingInterface'])
	scanner.debugGetSectionKindsForProject()






























































