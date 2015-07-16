
import os.path
from multiprocessing import Pool
from xml.etree import ElementTree
import re

'''
Need to get list of:
 - functions, methods, and properties decorated with SCRIPT_API
 - All QObject classes
 - All QObject classes with public slots and/or QPROPERTY(s)
 - All types that have had been decorated via Q_DECLARE_METATYPE (at global scope)
 - All types that have had qScriptRegisterMetaType() called on them (from local scope)
 - The list of functions/methods that used qScriptRegisterMetaType
 - The list of all files that included:
 	- QScriptEngine
 	- QScriptValue
 	- ScriptEngine.h (and the files that were included into ScriptEngine.h)

 - Just a plain dependency graph...? (everything that was used by ScriptEngine, rofl)

'''

STRIP_CONST_REF = True


def gettext(node):
	return ''.join([ text for text in node.itertext() ])

def getname(node):
	return gettext([ name for name in node.iter('name') ][0])

def gettag(node, tag):
	return gettext([ elem for elem in node.iter(tag) ][0])

class XmlClassFileScanner:
	''' Loads and scans a class_**********.xml file. DEPRECATED. '''

	def __init__(self, classFile):
		root = ElementTree.parse(classFile).getroot()
		self.results = []
		for node in root.iter('compounddef'):
			kind = node.attrib['kind']
			if kind == 'class' or kind == 'struct':
				self.scanClass(node)
			elif kind == 'namespace':
				self.scanNamespace(node)
			else:
				print("WARNING -- unhandled compounddef type: %s (%s)"%(kind, ''))
		# self.checkTagUsage(root, ['compounddef'], classFile)
		# self.checkKindUsage(root, ['class', 'struct', 'namespace'], classFile)

		# unhandledTypes = set([ elem.tag for elem in root if elem.tag != 'compounddef' ])
		# if len(unhandledTypes) > 0:
		# 	print("Unhandled tag(s): " + ", ".join(unhandledTypes))

	@staticmethod
	def checkTagUsage(node, tags, name):
		tags = set(tags)
		unhandledTags = set([ elem.tag for elem in node if elem.tag not in tags ])
		if len(unhandledTags) > 0:
			print("WARNING: Unhandled tag(s): " + ", ".join(unhandledTags) + " (%s)"%name)

	@staticmethod
	def checkKindUsage(node, kinds, name):
		kinds = set(kinds)
		unhandledKinds = set([ elem.attrib['kind'] for elem in node if elem.attrib['kind'] not in kinds ])
		if len(unhandledKinds) > 0:
			print("WARNING: Unhandled kind(s): " + ", ".join(unhandledKinds) + " (%s)"%name)

	''' Section types:
	      "user-defined", "public-type", "public-func", "public-attrib", "public-slot", "signal", "dcop-func", "property", 
	      "event", "public-static-func", "public-static-attrib", "protected-type", "protected-func", "protected-attrib", 
	      "protected-slot", "protected-static-func", "protected-static-attrib", "package-type", "package-func", "package-attrib", 
	      "package-static-func", "package-static-attrib", "private-type", "private-func", "private-attrib", "private-slot", 
	      "private-static-func", "private-static-attrib", "friend", "related", "define", "prototype", "typedef", "enum", "func", "var"
	'''

	section_types = {
		'method':		set(['func', 'public-func', 'protected-func', 'private-func']),
		'static_method':set(['public-static-func', 'protected-static-func', 'private-static-func']),
		'member':		set(['var', 'public-attrib', 'protected-attrib', 'private-attrib']),
		'static_member':set(['public-static-attrib', 'protected-static-attrib', 'private-static-attrib']),
		'signal': 		set(['signal']),
		'slot':	  		set(['public-slot', 'private-slot', 'protected-slot']),
		'public_slot': 	set(['public-slot']),
		'property':		set(['property'])
	}

	def scanClass(self, node):
		name = gettag(node, 'compoundname')

		qt_public_slots = []
		qt_properties   = []
		qt_signals      = []
		is_qt_object = True		#dunno how to check this actually >.<

		api_exposed_methods = []

		section_types = self.section_types
		member_types = section_types['method'] | section_types['static_method'] | \
					   section_types['member'] | section_types['static_member']

		all_member_types = member_types | section_types['signal'] | section_types['slot'] | section_types['property']

		# scan sections
		for elem in node.iter('sectiondef'):
			kind = elem.attrib['kind']
			if kind in self.section_types['public_slot']:
				for member in elem.iter('memberdef'):
					qt_public_slots += [(getname(member), member)]
			elif kind in self.section_types['property']:
				for member in elem.iter('memberdef'):
					qt_public_slots += [(getname(member), member)]

			if kind in all_member_types:
				for member in elem.iter('memberdef'):
					typeSig = gettext([ type_ for type_ in member.iter('type') ][0])
					if typeSig.find('SCRIPT_API') >= 0:
						api_exposed_methods += [(getname(member), member)]
			# else:
				# print("WARNING -- unhandled kind: %s (%s)"%(kind, name))

		info = { 'class': node }
		if api_exposed_methods or qt_public_slots or qt_properties:
			if api_exposed_methods:
				info['exposed_methods']    = api_exposed_methods
			if qt_public_slots:
				info['exposed_slots']      = qt_public_slots
			if qt_properties:
				info['exposed_properties'] = qt_properties
			self.results += [(name, info)]

	def scanNamespace(self, node):
		pass

def scanFile(file_):
	try:
		return XmlClassFileScanner(file_).results or None
	except Exception, e:
		print("EXCEPTION: ")
		print(e)

class ScriptApiScanner:
	def __init__(self, xmldir):
		self.xmlpath = xmldir

	def _loadIndex(self, **kwargs):
		file_ = os.path.join(self.xmlpath, "index.xml")
		self.index = ElementTree.parse(file_).getroot()
		self.items = {}


		# self.classes = {}
		# self.namespaces = {}
		# self.methods = {}
		# self.data_members = {}
		# self.properties = {}
		# self.enums = {}
		# self.enum_values = {}
		# self.unions = {}
		# self.typedefs = {}
		# self.global_variables = {}
		# self.global_functions = {}
		# self.friend_decls = {}
		# self.doxygen_data = {
		# 	'classes':    	self.classes,
		# 	'namespaces': 	self.namespaces,
		# 	'methods':		self.methods,
		# 	'data_members': self.data_members,
		# 	'properties':	self.properties,
		# 	'enums':		self.enums,
		# 	'enum_values':	self.enum_values,
		# 	'unions':		self.unions,
		# 	'typedefs':		self.typedefs,
		# 	'global_variables':	self.global_variables,
		# 	'global_functions': self.global_functions,
		# 	'friend_decls':	self.friend_decls
		# }

		categories = [ 'classes', 'namespaces', 'methods', 'data_members', 'properties', 'enums', 'enum_values', 'unions', 'typedefs', 'global_variables', 'global_functions', 'friend_decls']
		for cat in categories:
			self.__dict__[cat] = {}
		self.doxygen_data = dict([ (cat, self.__dict__[cat]) for cat in categories ])

		self.scanned_scriptable_values = {}
		''' <refid>: {
			name: <name>
			kind: <kind>
			type: Function (rtype, (params...)) | Member (type)
			used_types: [ cpptype ]
			references:    [ refids called by this ]
			referenced_by: [ refids referencing this ]
		}
		'''

		self.scannedItems = {}
		self._scanIndex(**kwargs)

	def _scanIndex(self, print_indexed_items = False, print_index_summary = False, print_warnings = True, print_aliases = True):
		if print_warnings:
			def warn(*args):
				print('WARNING: ' + ''.join(map(str, args)))
		else:
			def warn(*args):
				pass

		# dict of str: set([ str ])
		aliased_members = {}

		def scanContainer(container, member_map):
			def scanNode(node):
				name = self.getNameOfNode(node)
				self.items[node.attrib['refid']] = {
					'name': name,
					'kind': node.attrib['kind'],
					'members': dict([(member.attrib['refid'], {
							'kind': member.attrib['kind'],
							'name': name,
							'parent': node.attrib['refid']
						}) for member in node.iter('member')])
				}
				container[name] = node.attrib['refid']
				for refid, member in self.items[node.attrib['refid']]['members'].iteritems():
					member_name = name + '::' + member['name']
					cat         = member_map[member['kind']]
					if member_name in cat:
						# Handle aliases / overloads
						# print("Alias! %s (%d)"%(member_name, len(aliased_members)))
						# alias_len = len(aliased_members)

					 	if type(cat[member_name]) == list:
					 		cat[member_name] += [ refid ]
					 		aliased_members[member_name] += [ refid ]
					 	else:
					 		aliased_members[member_name] = [ cat[member_name], refid ]
					 		cat[member_name] = [ cat[member_name], refid ]
					 	# print(alias_len, len(aliased_members))
					 	# print(aliased_members)
					else:
						cat[member_name] = refid
					self.items[refid] = member
			return scanNode

		scanClassNode = scanContainer(self.classes, {
			'property': self.properties,
			'variable': self.data_members,
			'function': self.methods,
			'slot':		self.methods,
			'signal':	self.methods,
			'typedef':  self.typedefs,
			'enum':		self.enums,
			'enumvalue': self.enum_values,
			'union':	self.unions,
			'class':	self.classes,
			'struct': 	self.classes,
			'friend':   self.friend_decls
		})
		scanNamespace = scanContainer(self.namespaces, {
			'variable': self.global_variables,
			'function': self.global_functions,
			'typedef':  self.typedefs,
			'enum':  	self.enums,
			'enumvalue': self.enum_values
		})
		scanUnion     = scanContainer(self.unions, {
			'variable': self.global_variables,
			'function': self.global_functions,
			'typedef':  self.typedefs,
			'enum':  	self.enums,
			'enumvalue': self.enum_values,
			'union':	self.unions
		})

		def __ignore__():
			def scanClassNode(node):
				name = self.getNameOfNode(node)
				self.items[node.attrib['refid']] = {
					'name': name,
					'kind': node.attrib['kind'],
					'members': dict([(member.attrib['refid'], {
							'kind': member.attrib['kind'],
							'name': self.getNameOfNode(member),
							'parent': node.attrib['refid']
						}) for member in node.iter('member')])
				}
				if name in self.classes:
					print('%s already defined as %s'%(name, self.classes['name']))
					print('also defined as %s'%(node.attrib['refid']))
					return
				self.classes[name] = node.attrib['refid']
				member_map = {
					'property': self.properties,
					'variable': self.data_members,
					'function': self.methods,
					'slot':		self.methods,
					'signal':	self.methods,
					'typedef':  self.typedefs,
					'enum':		self.enums,
					'enumvalue': self.enum_values,
					'union':	self.unions,
					'class':	self.classes,
					'struct': 	self.classes,
					'friend':   self.friend_decls
				}
				for refid, member in self.items[node.attrib['refid']]['members'].iteritems():
					member_name = name + '::' + member['name']
					cat         = member_map[member['kind']]
					if member_name in cat:
					# 	# Handle overloads / aliases
					 	if type(cat[member_name]) == list:
					 		cat[member_name] += [ refid ]
					 		aliased_members[member_name].add(member['kind'])
					 	else:
					 		aliased_members[member_name] = set([
					 			self.items[cat[member_name]]['kind'],
					 			member['kind'] ])
					 		cat[member_name] = [ cat[member_name], refid ]
					else:
						cat[member_name] = refid
					self.items[refid] = member
	
			def scanNamespace(node):
				name = self.getNameOfNode(node)
				self.items[node.attrib['refid']] = {
					'name': name,
					'kind': node.attrib['kind'],
					'members': dict([(member.attrib['refid'], {
							'kind': member.attrib['kind'],
							'name': self.getNameOfNode(member),
							'parent': node.attrib['refid']
						}) for member in node.iter('member')])
				}
				if name in self.namespaces:
					warn('%s already defined as %s'%(name, self.classes['name']))
					warn('also defined as %s'%(node.attrib['refid']))
					return
				self.namespaces[name] = node.attrib['refid']
				member_map = {
					'variable': self.global_variables,
					'function': self.global_functions,
					'typedef':  self.typedefs,
					'enum':  	self.enums,
					'enumvalue': self.enum_values
				}
				for refid, member in self.items[node.attrib['refid']]['members'].iteritems():
					member_map[member['kind']][name + '::' + member['name']] = refid
					if not refid in self.items:
						self.items[refid] = member
					else:
						warn("Duplicate member %s"%refid)
	
			def scanUnion(node):
				name = self.getNameOfNode(node)
				self.items[node.attrib['refid']] = {
					'name': name,
					'kind': node.attrib['kind'],
					'members': dict([(member.attrib['refid'], {
							'kind': member.attrib['kind'],
							'name': self.getNameOfNode(member),
							'parent': node.attrib['refid']
						}) for member in node.iter('member')])
				}
				if name in self.namespaces:
					warn('%s already defined as %s'%(name, self.classes['name']))
					warn('also defined as %s'%(node.attrib['refid']))
					return
				self.unions[name] = node.attrib['refid']
				member_map = {
					'variable': self.global_variables,
					'function': self.global_functions,
					'typedef':  self.typedefs,
					'enum':  	self.enums,
					'enumvalue': self.enum_values,
					'union':	self.unions
				}
				for refid, member in self.items[node.attrib['refid']]['members'].iteritems():
					member_map[member['kind']][name + '::' + member['name']] = refid
					if not refid in self.items:
						self.items[refid] = member
					else:
						warn("Duplicate member %s"%refid)

		def warnNoScan(node):
			warn("Not parsing %s (%s)"%(self.getNameOfNode(node), node.attrib['kind']))
		def ignore(node):
			pass

		parseRules = {
			'struct':    scanClassNode,
			'class':     scanClassNode,
			'example':   warnNoScan,
			'dir':       ignore,
			'union':     scanUnion,
			'namespace': scanNamespace,
			'file':      ignore, 	# source files + headers
			'page':      ignore		# readmes, etc
		}

		# Scan everything in index
		unhandledKinds = set()
		for node in self.index.iter('compound'):
			if node.attrib['kind'] in parseRules:
				parseRules[node.attrib['kind']](node)
			else:
				unhandledKinds.add(node.attrib['kind'])

		# print(len(aliased_members))
		# print(aliased_members)
		if aliased_members and print_aliases:
			print("%d aliases"%(len(aliased_members)))
			for name, refids in aliased_members.iteritems():
				print("%s has %d aliases:\n\t"%(name, len(refids)) + '\n\t'.join([
					'%s %s (child of %s %s)'%(
						self.items[refid]['kind'], refid, 
						self.items[self.items[refid]['parent']]['kind'], self.items[refid]['parent'])
					for refid in refids ]))

		# Scan for things that are defined in one place (self.items) but not another
		# (self.classes | self.namespaces | self.members | ...)
		undefined_values = []

		# get the set of all refids, then remove anything that is stored somewhere else
		# what remains is not contained in self.classes, etc.,
		dangling_references = set(self.items.keys())		
		for cat, elems in self.doxygen_data.iteritems():
			for name, item in elems.iteritems():
				if type(item) == str:	
					# item is a refid
					if item in dangling_references:
						dangling_references.remove(item)
					else:
						undefined_values += [(name, refid)]
				elif type(item) == list:
					# item is (should be) a list of refids
					for ref in item:
						if ref in dangling_references:
							dangling_references.remove(ref)
						else:
							undefined_values += [(name, refid)]
				else:
					warn('%s is not a refid: %s'%(name, item))

		for ref in dangling_references:
			print("cannot access %s:  %s"%(ref, self.items[ref]))
			print(self.items[ref])
			parent = self.items[self.items[ref]['parent']]
			members = parent['members'] if 'members' in parent else []
			if members:
				print('parent has items:\n\t' + '\n\t'.join([ '%s:   %s'%(childref, self.items[childref]['kind']) for childref in members ]))

		if print_indexed_items:
			for thing_type, thing in self.doxygen_data.iteritems():
				print('%d %s: '%(len(thing), thing_type))
				for name, item in thing.iteritems():
					print('\t%s: %s'%(name, item))

		if print_index_summary:
			print('indexed ' + ', '.join([ '%d %s'%(len(things), thing) for thing, things in self.doxygen_data.iteritems() if things ]))
			non_indexed_things = [ thing for thing, things in self.doxygen_data.iteritems() if not things ]
			if non_indexed_things:
				if len(non_indexed_things) > 1:
					print('no ' + ', '.join(non_indexed_things[:-1]) + ', or ' + non_indexed_things[-1])
				else:
					print('no ' + ', '.join(non_indexed_things))

		if print_warnings:
			if dangling_references:
				print('WARNING: %d values are indexed, but not referencable:\n\t'%len(dangling_references) + '\n\t'.join(
					[ '%s    (%s)'%(ref, self.items[ref]) for ref in dangling_references]))
			if undefined_values:
				print('WARNING: %d values are referenced, but not indexed:\n\t'%(len(undefined_values)) + '\n\t'.join(
					[ '%s    (%s)'%item for item in undefined_values ]))

		if unhandledKinds:
			print("Unhandled kinds: " + ', '.join(unhandledKinds))

	def getIndex (self):
		''' Gets the doxygen index.xml file as an ElementNode '''
		if not 'index' in self.__dict__:
			self._loadIndex()
		return self.index


	def _reloadIndex (self):
		''' Loads the doxygen index.xml file (which all function/class/etc lookups start at). '''
		file_ = os.path.join(self.xmlpath, "index.xml")
		self.index = ElementTree.parse(file_).getroot()

		scannableItems = [ 'class', 'struct', 'namespace', 'var', 'function' ]
		self.classFiles = set([])

		# Scan entries
		for node in self.index.iter('compound'):
			kind = node.attrib['kind']
			if kind in scannableItems:
				self.classFiles.add(os.path.join(self.xmlpath, node.attrib['refid'] + '.xml'))

	def scanAllFiles (self):
		''' Runs a full scan of the hifi project sources and returns a list of methods + classes that are accessible by the scripting api.
		Uses multiple instances of XmlClassFileScanner and multithreaded file i/o to do this quickly.

		This is the old impl.
		'''
		if not 'classFiles' in self.__dict__:
			self._reloadIndex()

		pool = Pool(16)
		results = pool.map(scanFile, self.classFiles)

		# Flatten array and remove empty elements
		results_ = []
		for result in results:
			if result:
				results_ += result
		return results_


	def getNameOfNode(self, node, tag = 'name', assignToNode = False):
		''' Returns the name of an doxygen xml node, where 'tag' is the name of the xml tag containing the name.
		Can be used to get the contents of other simple nodes as well, so this may need to be renamed/refactored...
		'''
		if tag in node.__dict__:
			return node.__dict__[tag]
		name = [ ''.join(elem.itertext()) for elem in node.iter(tag) ][0]
		if assignToNode:
			node.__dict__[tag] = name
		return name

	def getInnerText(self, node):
		''' Returns the inner text of a doxygen node (converts <p> into '\n' and strips out <ref>) '''
		def _getInnerText(node): 
			if type(node) == str:
				return node
			if node.tag == 'para':
				return '\n' + node.tag + ''.join(map(self.getInnerText, node))
			if node.tag == 'ref':
				return node.text + ''.join(map(self.getInnerText, node))
			if node.text:
				return node.text + ''.join(map(self.getInnerText, node))
			return ''.join(map(self.getInnerText, node))
		return _getInnerText(node).strip()

	def getQObjectList(self):
		if not '_class_list' in self.__dict__:
			if not 'index' in self.__dict__ or self.index is None:
				self._reloadIndex()
			classTypes = set(['class', 'struct'])
			self._class_list = [ (
				self.getNameOfNode(elem), elem.attrib['refid']) 
				for elem in self.index.iter('compound') 
				if elem.attrib['kind'] ]
		return self._class_list

	def getClassIndex(self, name):
		''' Returns the doxygen class node from index.xml '''
		if not 'index' in self.__dict__ or self.index is None:
			self._reloadIndex()
		classTypes = set(['class', 'struct'])
		for node in self.index.iter('compound'):
			if node.attrib['kind'] in classTypes and self.getNameOfNode(node, assignToNode=True) == name:
				return node
		return None

	def loadClassXml(self, classIndex):
		''' Loads a doxygen class node from its corresponding .xml file. Use with getClassIndex(name). '''
		file_ = os.path.join(self.xmlpath, classIndex.attrib['refid'] + '.xml')
		root = ElementTree.parse(file_).getroot()

		classnode = [ node for node in root.iter('compounddef') if node.attrib['id'] == classIndex.attrib['refid']][0]
		assert(classnode.attrib['kind'] == 'class' or classnode.attrib['kind'] == 'struct')
		assert(classnode.attrib['language'] == 'C++')
		return classnode

	def scanExposedClass(self, scriptedclass):
		''' Scans a doxygen class node for js-related information (exposed methods, class dependencies, etc).
		Returns [ <scanned classes> ], set([ <external types> ])
		'''
		if not '_scannedClasses' in self.__dict__:
			self._scannedClasses = {}
		if scriptedclass in self._scannedClasses:
			print("Already scanned class '%s'"%(scriptedclass))
			return [], set()

		index  = self.getClassIndex(scriptedclass)
		class_ = self.loadClassXml(index)

		members = self.scanMembers(class_)
		# print [k for k in members if members[k] ]

		exposed_methods = members['exposed_methods'] + members['exposed_slots'] + members['exposed_signals']
		type_dependencies = set()
		for method in exposed_methods:
			rtype, params = method['jstype']
			# print([rtype] + [ param['type'] for param in params ])
			map(type_dependencies.add, [rtype] + [ param['type'] for param in params ])

		exposed_properties = members['exposed_attribs'] + members['exposed_properties']
		for prop in exposed_properties:
			type_dependencies.add(prop['type'])

		hifi_classes = self.getQObjectList()
		class_set = set([ name for name, _ in hifi_classes ])

		print("Scanned class '%s'"%scriptedclass)
		for category, values in members.iteritems():
			if values:
				if type(values[0]) == dict:
					# Processed method, etc
					print('%s:\n\t%s'%(category, ', '.join([ val['name'] for val in values ])))
				else:
					# Unprocessed doxygen xml node
					print('%s:\n\t%s'%(category, ', '.join([ self.getNameOfNode(node) for node in values ])))

		internal_types, external_types = type_dependencies.intersection(class_set), type_dependencies.difference(class_set)
		print("Internal types: " + ', '.join(internal_types))
		print("External types: " + ', '.join(external_types))
		print('')

		class_ = {
			'name': scriptedclass,
			'members': members,
			'internal_types': internal_types,
			'external_types': external_types
		}

		scannedClasses = [class_]
		for type_ in internal_types:
			print("scanning dependent class '%s'"%type_)
			classes, externals = self.scanExposedClass(type_)
			scannedClasses += classes
			external_types |= externals
		
		self._scannedClasses[scriptedclass] = class_
		return scannedClasses, external_types

	''' Defines what the contents of doxygen member sections are tagged as. 
	Used by getSectionLookupTable and scanScriptableMembers.
	'''
	method_section_categories = [
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
	]
	def getSectionLookupTable(self):
		''' Generates and caches a fast lookup table to categorize doxygen xml nodes based on attrib['kind'].
		Used by scanScriptableMembers; the result is generated from method_section_categories.
		'''
		if not 'method_section_lookup_table' in self.__dict__:
			self.method_section_lookup_table = {}
			for category, kinds in self.method_section_categories:
				self.method_section_lookup_table.update(dict([ (kind, category) for kind in kinds ]))
			self._testSectionLookupTable()
			# print("Method section-lookup-table:")
			# for k, v in self.method_section_lookup_table.iteritems():
				# print("\t'%s': '%s'"%(k, v))
		return self.method_section_lookup_table

	def _testSectionLookupTable(self):
		''' Tests the lookup table against the section kinds defined in compound.xsd '''
		doxygen_section_kinds = ["user-defined", "public-type", "public-func", "public-attrib", "public-slot", 
			"signal", "dcop-func", "property", "event", "public-static-func", "public-static-attrib", "protected-type", 
			"protected-func", "protected-attrib", "protected-slot", "protected-static-func", "protected-static-attrib", 
			"package-type", "package-func", "package-attrib", "package-static-func", "package-static-attrib", 
			"private-type", "private-func", "private-attrib", "private-slot", "private-static-func", 
			"private-static-attrib", "friend", "related", "define", "prototype", "typedef", "enum", "func", "var"]
		for thing in doxygen_section_kinds:
			assert(thing in self.getSectionLookupTable())

	def scanMembers(self, classNode):
		''' Scans and returns a dict of a class's members, sorted by category. Used by scanExposedClass(). '''
		members = dict([ (category, []) for category, _ in self.method_section_categories ])
		lookup  = self.getSectionLookupTable()

		# print(classNode.__dict__)
		# print([ section.attrib['kind'] for section in classNode.iter('sectiondef') ])

		for section in classNode.iter('sectiondef'):
			# print('section %s: '%(section.attrib['kind']) + ', '.join([ self.getNameOfNode(member) for member in section.iter('memberdef') ]))
			members[lookup[section.attrib['kind']]] += [ member for member in section.iter('memberdef') ]

		methods = ['exposed_methods', 'non_exposed_methods', 'exposed_slots', 'non_exposed_slots', 'exposed_signals', 'non_exposed_signals']
		for category in methods:
			members[category] = map(self.parseMethod, members[category])

		if members['exposed_attribs']:
			members['exposed_attribs'] = map(self.parsePublicAttrib, members['exposed_attribs'])

		self.checkForPropertyMacroDefns(members)

		return members


	def checkForPropertyMacroDefns (self, members):
		''' BRAD... >.> '''

		def checkForPropertyMacroMasqueradingAsMethod():
			macro_invocations = []
			for method in members['non_exposed_methods']:
				if 'DEFINE_PROPERTY' in method['name']:
					_, params = method['cpptype']
					macro, macro_args = method['name'], [ param['type'] for param in params ]
					macro_invocations += [(macro, macro_args)]
			if macro_invocations:
				print("Found un-expanded property macros:\n\t%s"%'\n\t'.join(['%s(%s)'%(macro, ', '.join(args)) for macro, args in macro_invocations ] ))
				print("Correcting...")
				# Add as properties
				print(set([ len(args) for macro, args in macro_invocations ]))
				print([ (macro, args) for macro, args in macro_invocations if len(args) == 3 ])
				members['exposed_properties'] += [ {'name': args[2], 'type': args[3] } for macro, args in macro_invocations if len(args) == 4 ] + \
												 [ {'name': args[1], 'type': args[2] } for macro, args in macro_invocations if len(args) == 3 ]

				# Remove from methods list
				thingsToDelete = set([ macro for macro, _ in macro_invocations ])
				members['non_exposed_methods'] = [ thing for thing in members['non_exposed_methods'] if thing['name'] not in thingsToDelete ]

		# Attempt to handle all weird cases
		checkForPropertyMacroMasqueradingAsMethod()


	def toJsType(self, type_, strip_const = STRIP_CONST_REF):
		''' Converts a c++ type to a js-friendly version. 
		Removes useless decorators like Q_INVOKABLE and SCRIPT_API, and strips const and const & if strip_const == True
		'''
		type_ = re.sub(r'(Q_INVOKABLE|SCRIPT_API)', '', type_)
		if strip_const:
			type_ = re.sub(r'const\s+(.+)\s*&', r'\1', type_)
			type_ = re.sub(r'const\s+(.+)', r'\1', type_)
		return type_.strip()

	def parseMethod(self, methodnode):
		''' Parses a doxygen method node and returns a python-friendly version of its contents. '''
		methodInfo = {}
		methodInfo['name'] = self.getNameOfNode(methodnode)

		rtype  = map(self.getInnerText, methodnode.iter('type'))
		rtype  = rtype[0] if rtype else None
		params = [ dict([ (elem.tag, self.getInnerText(elem)) for elem in param ]) for param in methodnode.iter('param') ]
		methodInfo['cpptype'] = (rtype, params)

		js_rtype = self.toJsType(rtype) if rtype else None
		js_params = []
		for param in params:
			param = param.copy()
			if 'type' in param:
				param['type'] = self.toJsType(param['type'])
			js_params += [param]
		methodInfo['jstype'] = (js_rtype, js_params)

		methodInfo['attribs'] = methodnode.attrib
		methodInfo['references'] = [ ref.attrib for ref in methodnode.iter('references')]
		methodInfo['referencedby'] = [ ref.attrib for ref in methodnode.iter('referencedby')]

		brief = map(self.getInnerText, methodnode.iter('briefdescription'))
		methodInfo['brief'] = brief[0] if brief and brief[0] else None

		details = map(self.getInnerText, methodnode.iter('detaileddescription'))
		methodInfo['details'] = details[0] if details and details[0] else None

		return methodInfo

	def parsePublicAttrib(self, attribnode):
		''' Parses a doxygen attrib node and returns a python-friendly version of its contents. '''
		# print(attribnode.__dict__)
		attribInfo = {
			'name': self.getNameOfNode(attribnode),
			'type': map(self.getInnerText, attribnode.iter('type'))[0]
		}
		return attribInfo


	def parseEntityProperties(self):
		'''Guess what -- EntityItemProperties is so f***ing convoluted I need tons of custom logic to parse it.
		Thanks a lot, brad >.>
		'''

		''' What we know: (update this if anything f***ing changes!!!)
		- Properties are declared in EntityItemProperties.h using DEFINE_PROPERTY* invokations.


		'''
		entityProperties = self.loadClassXml(self.getClassIndex('EntityItemProperties'))
		members = self.scanMembers(entityProperties)

		'''
		Note: DEFINE_PROPERTY, DEFINE_PROPERTY_REF, DEFINE_PROPERTY_WITH_SETTER, DEFINE_PROPERTY_REF_WITH_SETTER,
		and DEFINE_PROPERTY_REF_WITH_SETTER_AND_GETTER behave functionally identical from a javscript POV.

		They are just variants on the same set of method/attrib decls, where the type T is passed by value or
		by const ref, and getters/setters either are or are not automatically generated (the methods are exactly
		the same though).

		DEFINE_PROPERTY_REF_ENUM also does the same thing, but adds... to/from string operations. (why...?)

		All DEFINE_PROPERTY macros have the signature (PROPERTY_ENUM_VALUE, lowercaseVarName, upperCaseVarName, type),
		and define:
			- type _varName, bool _varNameChanged attribs
			- type getVarName(), void setVarName(type value) methods
			- bool varNameChanged(), void setVarNameChanged (bool value) methods.
		'''

		defineMacros = { 
			'DEFINE_PROPERTY': lambda (_, __, name, type_): { 'name': name, 'type': type_ }, 
			'DEFINE_PROPERTY_REF': lambda (_, __, name, type_): { 'name': name, 'type': type_ }, 
			'DEFINE_PROPERTY_REF_ENUM': lambda (_, __, name, type_): { 'name': name, 'type': type_ },
			'DEFINE_PROPERTY_WITH_SETTER': lambda (_, __, name, type_): { 'name': name, 'type': type_ }, 
			'DEFINE_PROPERTY_REF_WITH_SETTER': lambda (_, __, name, type_): { 'name': name, 'type': type_ }, 
			'DEFINE_PROPERTY_REF_WITH_SETTER_AND_GETTER': lambda (_, __, name, type_): { 'name': name, 'type': type_ }, 
			'DEFINE_PROPERTY_REF_WITH_SETTER_AND_GETTER': lambda (_, __, name, type_): { 'name': name, 'type': type_ }
		}

		properties = [ member for member in members['non_exposed_methods'] if 'DEFINE_PROPERTY' in members['name'] ]
		properties = [ defineMacros(member['type'][1]) for member in properties ]






def autobuild ():
	''' Runs doxygen if the documentation has not already been built. '''
	if not os.path.isfile('docs/config.txt'):
		print('Missing doxygen config file')
		system.exit(-1)

	if not os.path.isfile('docs/xml/index.xml'):
		print('Generating docs...')
		os.system('doxygen docs/config.txt')
		print('Generated docs in <hifi dir>/docs')

	assert(os.path.isfile('docs/xml/index.xml'))

if __name__ == '__main__':
	os.chdir('../../')	# Navigate to root hifi directory
	autobuild()

	scanner = ScriptApiScanner('docs/xml')
	scanner._loadIndex(print_indexed_items = False, print_index_summary = True)


	# results = scanner.scanAllFiles()

	# for name, info in results:
	# 	print("Exposed class: %s"%name)
	# 	if 'exposed_methods' in info:
	# 		print("SCRIPT_API:   " + ', '.join([ name for name, _ in info['exposed_methods']]))
	# 	if 'exposed_slots' in info:
	# 		print("public slots: " + ', '.join([ slot for slot, _ in info['exposed_slots']]))
	# 	if 'exposed_properties' in info:
	# 		print("properites:   " + ', '.join([ name for name, _ in infor['exposed_properites']]))
	# 	print('')


	# num_api_methods = sum([ len(info['exposed_methods']) for name, info in results if 'exposed_methods' in info ])
	# num_qt_slots    = sum([ len(info['exposed_slots'])   for name, info in results if 'exposed_slots' in info ])
	# num_qt_props    = sum([ len(info['exposed_properties']) for name, info in results if 'exposed_properties' in info ])
	# untagged_methods = num_qt_slots + num_qt_props - num_api_methods

	# num_tagged = lambda (name, info): len(info['exposed_methods']) if 'exposed_methods' in info else 0
	# num_slots  = lambda (name, info): len(info['exposed_slots'])   if 'exposed_slots'   in info else 0
	# num_props  = lambda (name, info): len(info['exposed_properties']) if 'exposed_properties' in info else 0

	# tags = map(num_tagged, results)
	# tagged_classes = filter(lambda n: n != 0, tags)
	# fully_tagged_classes = []

	# num_tagged_classes   = len(tagged_classes)
	# num_untagged_classes = len(results) - num_tagged_classes

	# print("Finished scanning %d files."%len(scanner.classFiles))
	# print("Results: ")
	# print("    %d exposed classes (%d tagged, %d untagged)"%(len(results), num_tagged_classes, num_untagged_classes))
	# print("    %d exposed methods (%d tagged, %d untagged)"%(num_qt_props + num_qt_slots, num_api_methods, untagged_methods))
	
	# # Test recursive scanning
	# print('')
	# print('=' * 80)
	# print('')
	# scannedClasses, externals = scanner.scanExposedClass('EntityScriptingInterface')
	# print("Scanned classes:\n\t%s"%([ class_['name'] for class_ in scannedClasses ]))
	# print("Depends on external types:\n\t%s"%(', '.join(externals)))
