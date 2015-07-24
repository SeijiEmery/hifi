
import os.path
from multiprocessing import Pool, Queue
from xml.etree import ElementTree
import traceback
import re

USE_MULTITHREADING = True


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
				'parent':  None,
				'refid':   refid,
				'kind':    node.attrib['kind'],
				'name':	   _getNodeName(node),
				'members': dict([ (member.attrib['refid'], {
						'refid': member.attrib['refid'],
						'parent': refid,
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

# print("Test: %s"%fmtHumanReadableList(['foo', 'bar', 'baz']))
# print("Test: %s"%fmtHumanReadableList(['foo', 'bar']))
# print("Test: %s"%fmtHumanReadableList(['foo']))
# print("Test: %s"%fmtHumanReadableList([]))

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
		('vars', ['var']),
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

def getDescription(node):
	def getDescriptionLine(descrip):
		if getChildNode(node, descrip) is not None:
			return getChildInnerXml(node, descrip, preserveChildNodes=True).strip()
		return ''
	return {
		'brief': getDescriptionLine('briefdescription'),
		'details': getDescriptionLine('detaileddescription'),
		'inbody': getDescriptionLine('inbodydescription')
	}

def parseEnum(node):
	# for value in node.iter('enumvalue'):
	# 	print('%s: %s'%(_getNodeName(value), value.__dict__))
	loc = getChildNode(node, 'location')
	enum =  {
		'name': _getNodeName(node),
		'refid': node.attrib['id'],
		'kind': node.attrib['kind'],
		'prot': node.attrib['prot'],
		'values': [{
			'name': _getNodeName(value),
			'refid': value.attrib['id'],
			'initializer': getChildInnerXml(value, 'initializer'),
			'description': getDescription(value),
			# 'file': getChildNode(value, 'location').attrib['file'] if getChildNode(value, 'location') else None,
			# 'line': getChildNode(value, 'location').attrib['line'] if getChildNode(value, 'location') else None,
		} for value in node.iter('enumvalue')],
		'description': getDescription(node),
		# 'file': loc.attrib['file'] if loc else None,
		# 'line': loc.attrib['line'] if loc else None
	}
	# print(enum)
	return enum

def parseTypedef(node):
	# print("TYPEDEF %s: %s"%(node, node.__dict__))
	return {
		'name': _getNodeName(node),
		'refid': node.attrib['id'],
		'prot': node.attrib['prot'],
		'type': getChildInnerXml(node, 'type'),
		'description': getDescription(node)
	}

def loadUnion(info, traceTypeInfo=False, printSummary=False):
	# print(info)
	root = ElementTree.parse(info['xmlpath']).getroot()
	compound = [ node for node in root.iter('compounddef') if node.attrib['id'] == info['refid']][0]
	if printSummary:
		print("Loading %s"%(info['refid']))
	# print("%s %s")%(compound, compound.__dict__)
	categorize = UnionParser.memberSectionKinds
	def parseSections(parsers):
		for section in compound.iter('sectiondef'):
			cat = categorize(section.attrib['kind'])
			map(parsers[cat], section.iter('memberdef'))
	obj = {
		'name': info['name'],
		'kind': info['kind'],
		'refid': info['refid'],
		'members': [],
		'description': getDescription(compound)
	}
	def parseMember(node):
		# print("UNION MEMBER %s: %s"%(node, node.__dict__))
		loc = getChildNode(node, 'location')
		obj['members'].append({
			'name': _getNodeName(node),
			'refid': node.attrib['id'],
			'kind': node.attrib['kind'],
			'prot': node.attrib['prot'],
			'type': getChildInnerXml(node, 'type', preserveChildNodes=True),
			'description': getDescription(node),
			'references': dict([(ref.attrib['refid'], {
				'name': getInnerXml(ref),
				'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else ''
			}) for ref in node.iter('references')]),
			'referencedby': dict([(
				ref.attrib['refid'],
				getInnerXml(ref)
			) for ref in node.iter('referencedby')]),
			'file': loc.attrib['file'],
			'line': loc.attrib['line']
		})
		# print(obj['members'][-1])

	parseSections({
		'union_members': parseMember
	})
	obj['references']   = {}
	obj['referencedby'] = {}
	for member in obj['members']:
		obj['references'].update(member['references'])
		obj['referencedby'].update(member['referencedby'])

	if traceTypeInfo:
		obj['used_types'] = set()
		for member in obj['members']:
			obj['used_types'].add(member['type'])


	if printSummary:
		s = "Union %s (%s)"%(obj['name'], obj['refid'])
		s += "\nhas %d reference(s):"%(len(obj['references']))
		for k, v in obj['references'].iteritems():
			s += '\n\t%s: %s'%(k, v) 
		s += "\nis referenced by %d:"%(len(obj['references']))
		for k, v in obj['referencedby'].iteritems():
			s += '\n\t%s: %s'%(k, v) 
		if traceTypeInfo:
			s += "\nuses %d type(s):"%(len(obj['used_types']))
			for t in obj['used_types']:
				s += '\n\t%s'%(t)
		print(s)
	return obj


def loadNamespace(info, traceTypeInfo=False, printSummary=False):
	root = ElementTree.parse(info['xmlpath']).getroot()
	compound = [ node for node in root.iter('compounddef') if node.attrib['id'] == info['refid']][0]
	if printSummary:
		print("Loading %s"%(info['refid']))
	categorize = NamespaceParser.memberSectionKinds
	def parseSections(parsers):
		for section in compound.iter('sectiondef'):
			# print("GOT NAMESPACE SECTION %s"%(section.attrib['kind']))
			cat = categorize(section.attrib['kind'])
			map(parsers[cat], section.iter('memberdef'))
	ns = {
		'name': info['name'],
		'kind': info['kind'],
		'refid': info['refid'],
		'vars': [],
		'functions': [],
		'enums': [],
		'typedefs': [],
		'description': getDescription(compound)
	}
	
	def parseFunc(node):
		name = _getNodeName(node)
		loc  = getChildNode(node, 'location')
		ns['functions'].append({
			'name': name,
			'refid': node.attrib['id'],
			'kind': node.attrib['kind'],
			'type': getChildInnerXml(node,'type'),
			'params': parseParams(node),
			'const': doxybool(node.attrib['const']),
			'prot': doxybool(node.attrib['prot']),
			'inline': doxybool(node.attrib['inline']),
			'file': loc.attrib['file'],
			'line': loc.attrib['line'],
			'description': getDescription(node),
			'references': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref),
				'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else ''
			} for ref in node.iter('references')],
			'referencedby': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref)
			} for ref in node.iter('referencedby')]
		})

	def parseVar(node):
		name = _getNodeName(node)
		loc = getChildNode(node, 'location')
		ns['vars'].append({
			'name': name,
			'refid': node.attrib['id'],
			'kind': node.attrib['kind'],
			'type': getChildInnerXml(node, 'type'),
			# 'const': doxybool(node.attrib['const']),
			'mutable': doxybool(node.attrib['mutable']),
			'static': doxybool(node.attrib['static']),
			# 'inline': doxybool(node.attrib['inline']),
			'file': loc.attrib['file'],
			'line': loc.attrib['line'],
			'description': getDescription(node),
			'references': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref),
				'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else ''
			} for ref in node.iter('references')],
			'referencedby': [{
				'refid': ref.attrib['refid'],
				'name': getInnerXml(ref)
			} for ref in node.iter('referencedby')]
		})

	def nsParseEnum(node):
		ns['enums'].append(parseEnum(node))
	def nsParseTypedef(node):
		ns['typedefs'].append(parseTypedef(node))
	
	parseSections({
		'vars': parseVar,
		'funcs': parseFunc,
		'enums': nsParseEnum,
		'typedefs': nsParseTypedef
	})

	if printSummary:
		print("\nParsed %s %s (%s)\n%s\n"%(ns['kind'], ns['name'], ns['refid'],
			  "Has " + fmtHumanReadableList([ '%d %s'%(len(ns[k]), k) for k in ['vars', 'functions', 'enums', 'typedefs']])))
	return ns


def loadClass(info, traceTypeInfo=False, printSummary=False):
	root = ElementTree.parse(info['xmlpath']).getroot()
	compound = [ node for node in root.iter('compounddef') if node.attrib['id'] == info['refid'] ][0]

	if printSummary:
		print("Loading %s"%(info['refid']))
	categorize = ClassParser.memberSectionKinds
	def parseSections(parsers):
		for section in compound.iter('sectiondef'):
			cat = categorize(section.attrib['kind'])
			map(parsers[cat], section.iter('memberdef'))
	obj = {
		'name': info['name'],
		'kind': info['kind'],
		'refid': info['refid'],
		'members': [],
		'methods': [],
		'properties': [],
		'enums': [],
		'typedefs': [],
		# 'used-types': [],
		# 'references': [],
		# 'referencedby': [],
		'friends': [],
		'description': getDescription(compound)
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
			'refid': node.attrib['id'],
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
			'description': getDescription(node),
			'references': dict([(
				ref.attrib['refid'],
				{ 'name': getInnerXml(ref), 'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else '' }
			) for ref in node.iter('references')]),
			'referencedby': dict([(
				ref.attrib['refid'],
				getInnerXml(ref)
			) for ref in node.iter('referencedby')])
		}
		# print(method)
		obj['methods'].append(method)

	def parseMember(node):
		# print(node.__dict__)
		name = _getNodeName(node)
		loc = getChildNode(node, 'location')
		member = {
			'name': name,
			'refid': node.attrib['id'],
			'kind': node.attrib['kind'],
			'type': getChildInnerXml(node, 'type'),
			# 'const': doxybool(node.attrib['const']),
			'mutable': doxybool(node.attrib['mutable']),
			'static': doxybool(node.attrib['static']),
			# 'inline': doxybool(node.attrib['inline']),
			'file': loc.attrib['file'],
			'line': loc.attrib['line'],
			'description': getDescription(node),
			'references': dict([(
				ref.attrib['refid'],
				{ 'name': getInnerXml(ref), 'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else '' }
			) for ref in node.iter('references')]),
			'referencedby': dict([(
				ref.attrib['refid'],
				getInnerXml(ref)
			) for ref in node.iter('referencedby')])
		}
		# print(member)
		obj['members'].append(member)

	def parseProperty(node):
		name = _getNodeName(node)
		loc = getChildNode(node, 'location')
		obj['properties'].append({
			'name': name,
			'refid': node.attrib['id'],
			'kind': node.attrib['kind'],
			'prot': node.attrib['prot'],
			'static': doxybool(node.attrib['static']),
			'read': (doxybool(node.attrib['readable']) and getChildNode(node, 'read').text) or None,
			'write': (doxybool(node.attrib['writable']) and getChildNode(node, 'write').text) or None,
			'description': getDescription(node),
			'type': getChildInnerXml(node, 'type'),
			'file': loc.attrib['file'],
			'line': loc.attrib['line'],
			'references': dict([(
				ref.attrib['refid'],
				{ 'name': getInnerXml(ref), 'compoundref': ref.attrib['compoundref'] if 'compundref' in ref.attrib else '' }
			) for ref in node.iter('references')]),
			'referencedby': dict([(
				ref.attrib['refid'],
				getInnerXml(ref)
			) for ref in node.iter('referencedby')])
		})
		# print("PROPERTY")
		# print(obj['properties'][-1])
		# print(node, node.__dict__)
		# print("READ: %s"%(getChildNode(node, 'read') is not None and getChildNode(node, 'read').__dict__))
		# print("WRITE: %s"%(getChildNode(node, 'write') is not None and getChildNode(node, 'write').__dict__))
		# pass

	def parseInternalType(node):
		# print("INTERNAL TYPE")
		if node.attrib['kind'] == 'enum':
			# print("%s %s")%(node, node.__dict__)
			obj['enums'].append(parseEnum(node))#, obj['name'] + '::' + _getNodeName(node)))
			# print("%s = %s")%(obj['name'] + '::' + _getNodeName(node), obj['enums'][-1])
		elif node.attrib['kind'] == 'typedef':
			# print("%s %s")%(node, node.__dict__)
			obj['typedefs'].append(parseTypedef(node))
			# print("%s = %s")%(obj['name'] + '::' + _getNodeName(node), obj['typedefs'][-1])
		else:
			print("UNKNOWN KIND %s"%(node.attrib['kind']))
			print("%s %s")%(node, node.__dict__)
			
	def parseFriend(node):
		# print("%s %s")%(node, node.__dict__)
		obj['friends'].append({
			'refid': node.attrib['id'],
			'name': _getNodeName(node)
		})
		# print(obj['friends'][-1])

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

	obj['internal_types'] = internal_types

	parseSections({
		'methods': parseMethod,
		'members': parseMember,
		'properties': parseProperty,
		'friends': parseFriend,
		'types': parseInternalType
	})

	obj['calls'] = {}
	obj['called_by'] = {}
	for method in obj['methods']:
		obj['calls'].update(method['references'])
		obj['called_by'].update(method['referencedby'])
	if traceTypeInfo:
		obj['used_types'] = set()
		for method in obj['methods']:
			obj['used_types'].add(method['type'])
		for member in obj['members']:
			obj['used_types'].add(member['type'])
		for prop in obj['properties']:
			obj['used_types'].add(prop['type'])
		for t in obj['typedefs']:
			obj['used_types'].add(t['type'])

	if printSummary:
		print("\nParsed %s %s (%s)\n%s\n"%(obj['kind'], obj['name'], obj['refid'],
			  "Has " + fmtHumanReadableList([ '%d %s'%(len(obj[k]), k) for k in ['methods', 'members', 'properties', 'enums', 'typedefs']])))
	# print(compound.__dict__)
	# print(getChildInnerXml(compound, 'basecompoundref', preserveChildNodes=True))
	# print(getChildInnerXml(compound, 'inheritancegraph', preserveChildNodes=True) if getChildNode(compound, 'inheritancegraph') else "NO INHERITANCE") 

	if printSummary:
		s = "Class %s (%s)"%(obj['name'], obj['refid'])
		s += "\nhas %d reference(s):"%(len(obj['calls']))
		for k, v in obj['calls'].iteritems():
			s += '\n\t%s: %s'%(k, v) 
		s += "\nis referenced by %d:"%(len(obj['called_by']))
		for k, v in obj['called_by'].iteritems():
			s += '\n\t%s: %s'%(k, v) 
		if traceTypeInfo:
			s += "\nuses %d type(s):"%(len(obj['used_types']))
			for t in obj['used_types']:
				s += '\n\t%s'%(t)
		print(s)
	# if traceTypeInfo:
	# 	print("\nUsed types: ")
	# 	for k, v in internal_types.iteritems():
	# 		print("\t'%s': (%s)"%(v, k))
	# 	print('\n')
	# 	all_references = {}
	# 	all_referencedby = {}
	# 	for method in obj['methods']:
	# 		all_references.update(dict([ (ref['refid'], ref['name']) for ref in method['references'] ]))
	# 		all_referencedby.update(dict([ (ref['refid'], ref['name']) for ref in method['referencedby'] ]))
	
	# 	print("\nReferences:")
	# 	for k, v in all_references.iteritems():
	# 		print("\t'%s': (%s)"%(v, k))
	# 	print("\nReferenced by:")
	# 	for k, v in all_referencedby.iteritems():
	# 		print("\t'%s': (%s)"%(v, k))
	# 	print('')
	return obj

def scanScriptableness(item):
	pass

def loadAnything(stuff, **kwargs):
	# print(kwargs)
	# print("ENTER %s"%(stuff['refid']))
	# print("%d / %d: %f%%"%(stuff['k'], stuff['n'], float(stuff['k']) / float(stuff['n']) * 100.0))
	try:
		if stuff['kind'] == 'class' or stuff['kind'] == 'struct':
			# rs = None
			rs = loadClass(stuff, **kwargs)
		elif stuff['kind'] == 'namespace':
			rs = loadNamespace(stuff, **kwargs)
			# rs = None
		elif stuff['kind'] == 'union':
			# print("Loading unions not yet implemented")
			rs = loadUnion(stuff, **kwargs)
		elif stuff['kind'] == 'enum':
			print("Loading enums not implemented")
			rs = stuff
		else:
			print("Cant load '%s'"%(stuff['kind']))
			return stuff
	except Exception as error:
		traceback.print_exc()
		print(error)
		# print("EXIT %s"%(stuff['refid']))
		return rs
	# print("EXIT %s"%(stuff['refid']))
	return rs

def bindkwargs(f, **kwargs):
	return lambda *args: f(*args, **kwargs)

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

	def debugFindThingWithProperties(self):
		self.loadIndex()

		min_properties = 0

		for cls in self.cat_lookup['classes']:
			if not cls in self.index:
				print("Missing refid: %s (%s)"%(refid, "calss"))
				continue
			root = ElementTree.parse(self.index[cls]['xmlpath'])
			matching_compounds = [ node for node in root.iter('compounddef') if node.attrib['id'] == cls ]
			if len(matching_compounds) != 1:
				print("Bad file: %s (%s)"%(cls, self.index[cls]['kind']))
				continue
			compound = matching_compounds[0]
			num_properties = len(list(compound.iter('properties')))
			if num_properties > min_properties:
				print("Found file %s with %d properties: "%(self.index[cls]['xmlpath'], num_properties))

		# OKAAAAAY... We don't have any properties in our codebase XD

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

	def loadEverything(self, **kwargs):
		# try:
			# print("kwargs = %s"%kwargs)
			scanner.loadIndex()
			classes = self.cat_lookup['classes']
			namespaces = self.cat_lookup['namespaces']
			enums = self.cat_lookup['enums']
			unions = self.cat_lookup['unions']
			everything = classes + namespaces + enums + unions
			# print(everything)
			# print(len(everything))
			pool = Pool(processes=32)

			things = [ self.index[thing] for thing in everything if thing in self.index ]
			# print(len(things))

			for i, thing in enumerate(things):
				thing['k'] = i
				thing['n'] = len(things)

			USE_MULTITHREADING = True

			if USE_MULTITHREADING:
				rs = pool.map(loadAnything, things)
				pool.close()
				pool.join()
			else:
				rs = map(bindkwargs(loadAnything, **kwargs), things)
			# print("Finished")
			# output = [ tmp.get() for tmp in rs ]
			# print(len(rs))
			for r in rs:
				self.loaded_items[r['refid']] = r
		# except Exception as e:
		# 	print("EARLY EXIT")
		# 	print(e)
		# print("Done")

	def runScriptTrace(self, entry_typenames):
		print("loading...")
		self.loadEverything(traceTypeInfo=False, printSummary=False)

		all_types = self.cat_lookup['classes'] + self.cat_lookup['namespaces'] + self.cat_lookup['enums'] + self.cat_lookup['unions']
		# print(all_types)

		entry_typenames = set(entry_typenames)
		entrypoints = [ self.loaded_items[ref] for ref in all_types if ref in self.index and self.index[ref]['name'] in entry_typenames ]
		unresolved  = [ name for name in entry_typenames if not name in [ x['name'] for x in entrypoints ]]

		for thing in entrypoints:
			print("Resolved '%s' to %s '%s'"%(thing['name'], thing['kind'], thing['refid']))
		if unresolved:
			print("Could not resolve: " + ', '.join(unresolved))

		def getScriptableMethods(cls):
			return [ 
				method for method in cls['methods'] 
				if 'Q_INVOKABLE' in method['type'] or (method['kind'] in ('signal', 'slot') and method['prot'] == 'public')
			]
		def getScriptableProperties(cls):
			return [
				prop for prop in cls['properties']
				if prop['prot'] == 'public'
			]
		def getReferencedTypes(members):
			exposed_types = set()
			for member in members:
				exposed_types.add(member['type'].replace("Q_INVOKABLE", "").strip())
				if 'params' in members:
					for param in members:
						exposed_types.add(param['type'])
			f = lambda s: s.replace('const', '').replace('&', '').replace('*', '').strip()
			return filter(f, exposed_types)

		def getInternalTypes(types):
			def getAllTypesFromTemplates(type_):
				if '<' in type_ or '>' in type_:
					l = type_.strip('>').split('<')
					first, rest = l[0], '<'.join(l[1:])
					yield first.strip()
					for x in rest.split(','):
						for v in getAllTypesFromTemplates(x.strip()):
							yield v		
				else:
					yield type_
			extracted_types = set()
			for t in types:
				extracted_types.update(set(getAllTypesFromTemplates(t)))
			return extracted_types

		def scanClass(cls, typelist):
			print("Scanning %s '%s'. Found scriptable members:"%(cls['kind'], cls['name']))
			for method in getScriptableMethods(cls):
				print("\t%s %s (%s (%s))"%(method['kind'], method['name'], method['type'], ', '.join([ '%s %s'%(p['type'], p['name']) for p in method['params'] ])))
			for prop in getScriptableProperties(cls):
				print("\t%s %s (%s)"%(prop['kind'], prop['name'], prop['type']))
			members = getScriptableMethods(cls) + getScriptableProperties(cls)
			types = getReferencedTypes(members)
			print("%d raw types:"%len(types))
			for t in types:
				print("\t%s"%t)
			typelist.update(getInternalTypes(types))


		builtin_types = set(['int', 'void', 'float', 'char', 'bool'])
		qt_types = set(['QVector', 'QUuid', 'QVariantMap', 'QString'])
		library_types = set(['glm::vec3', 'glm::mat4', 'glm::quat'])
		hifi_types = dict([ (self.index[k]['name'], self.index[k]['refid']) for k in all_types if k in self.index ])

		def scanRecursive(cls, openlist, closedlist):
			tl = set()
			for cls in entrypoints:
				if cls['kind'] in ('struct', 'class'):
					scanClass(cls, tl)
			print("%d types: %s"%(len(tl), ', '.join(tl)))
	
			builtin_types &= tl
			tl -= builtin_types
	
			qt_types &= tl
			tl -= qt_types
	
			library_types &= tl
			tl -= library_types
	
			hifi_types = dict([ (k, v) for k, v in hifi_types.iteritems() if k in tl ])
			tl -= set(hifi_types.keys())
		# hifi_types &= tl
		# tl -= hifi_types

		print("Used builtins: %s"%(list(builtin_types)))
		print("Used qt types: %s"%(list(qt_types)))
		print("Used library types: %s"%(list(library_types)))
		print("Used hifi types: %s"%(hifi_types))
		print("Unknown types: %s"%(list(tl)))

		entrypoints = {}
		# for typename in entry_types:






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

	# scanner.loadEverything()

	scanner.runScriptTrace(['EntityScriptingInterface', 'SceneScriptingInterface', 'ControllerScriptingInterface', 'foo', 'blarg'])

	# scanner.debugFindThingWithProperties()
	# scanner.debugPrintParamInnerTags()
	# print("scanner.scanType('Application')")
	# print(scanner.getScriptableInfo(["Application"]))
	# print("scanner.scanType('EntityScriptingInterface')")
	# scanner.getScriptableInfo(['EntityScriptingInterface'])

	# scanner.debugGetSectionKindsForProject()






























































