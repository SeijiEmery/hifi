
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


def scanFile(file_):
	try:
		return XmlClassFileScanner(file_).results or None
	except Exception, e:
		print("EXCEPTION: ")
		print(e)

def loadXml(refid):
	pass

class DoxyRef:
	def __init__(self, refid, constructorClass):
		self.refid
		self.constructorClass = constructorClass

	def load (self):
		return self.constructorClass(self, loadXml(self.refid))

class DoxyClass:
	pass


class ScriptApiScanner:
	def __init__(self, xmldir):
		self.xmlpath = xmldir

	def loadIndex(self, **kwargs):
		if 'index' in self.__dict__:
			return
		file_ = os.path.join(self.xmlpath, "index.xml")
		self.index = ElementTree.parse(file_).getroot()
		self.items = {}

		categories = [ 'classes', 'namespaces', 'enums', 'enum_values', 'unions', 
			'methods', 'data_members', 'properties', 'typedefs', 'global_variables', 'global_functions', 'friend_decls']
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
		self.scanIndex(**kwargs)

	def scanIndex(self, print_warnings = True, print_indexed_items = False, print_index_summary = False, print_aliases = False):
		if print_warnings:
			def warn(*args):
				print('WARNING: ' + ''.join(map(str, args)))
		else:
			def warn(*args):
				pass
		aliased_members = {}

		def scanContainer(container, member_map):
			def scanNode(node):
				name = self.getNodeName(node)
				self.items[node.attrib['refid']] = {
					'name': name,
					'kind': node.attrib['kind'],
					'members': dict([(member.attrib['refid'], {
							'kind': member.attrib['kind'],
							'name': name + '::' + self.getNodeName(member),
							'refid': member.attrib['refid'],
							'parent': node.attrib['refid']
						}) for member in node.iter('member')])
				}
				container[name] = node.attrib['refid']
				for refid, member in self.items[node.attrib['refid']]['members'].iteritems():
					# member_name = name + '::' + member['name']
					# print(name, member['name'], member_name, node.attrib['kind'], member['kind'])
					member_name = member['name']
					cat         = member_map[member['kind']]
					if member_name in cat:
						# Handle aliases / overloads
						if type(cat[member_name]) == list:
							aliases = [ refid ]
							cat[member_name] += aliases
						else:
							aliases = [ cat[member_name], refid ]
							cat[member_name] = aliases
						if not member_name in aliased_members:
							aliased_members[member_name] = set()
						map(aliased_members[member_name].add, aliases)
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

		def warnNoScan(node):
			warn("Not parsing %s (%s)"%(self.getNodeName(node), node.attrib['kind']))
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

		# for ref in dangling_references:
			# print("cannot access %s:  %s"%(ref, self.items[ref]))
			# print(self.items[ref])
			# parent = self.items[self.items[ref]['parent']]
			# members = parent['members'] if 'members' in parent else []
			# if members:
				# print('parent has items:\n\t' + '\n\t'.join([ '%s:   %s'%(childref, self.items[childref]['kind']) for childref in members ]))

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

	def getScriptable(self, class_list):
		''' Scans everything in the class_list and does recursive searcing for all that touch or reference these classes.
		Note: the items in class_list do not have to be classes -- they can be classes, structs, enums, functions, 
		global variables, methods, etc '''
		pass

	def scanItem(self, refid):
		for cat, elems in self.doxygen_data.iteritems():
			for elem in elems:
				if elem == refid or (type(elem) == dict and elem['refid'] == refid):
					self._reloadClass(self.doxygen_data[cat], elem)
					return self.items[refid]

	def loadClass(self, className):
		self.loadIndex()
		if not className in self.classes:
			return None
		if type(self.classes[className]) == str:
			self._reloadClass(self.classes, className)
		return self.classes[className]


	def getClass(self, name, *args):
		if not name in self.classes:
			raise Exception("%s is not a class"%(name))

		if type(self.classes[name]) == list:
			# Load and visit all aliases
			for i, alias in enumerate(self.classes[name]):
				if type(alias) == 'str':
					alias = self.scanItem(alias, *args)
				else:
					alias = self.scanItem(alias['refid'], *args)
				self.classes[name][i] = alias
		else:
			refid = self.classes[name] if type(self.classes[name] == str) else self.classes[name]['refid']
			self.classes[name] = self.scanItem(refid, *args)
		return self.classes[name]


	def scanItem(self, refid, visitor = None):
		# refid = classes[name]
		xmlfile = os.path.join(self.xmlpath, '%s.xml'%(refid))
		xml = ElementTree.parse(xmlfile).getroot()

		classNode = self.getCompoundDefWithId(xml, refid)
		class_ = self.items[refid]
		if '_scanned' in self.items[refid]:
			if visitor:
				visitor(class_)
			return class_
		class_['_scanned'] = True

		assert(class_['name'] == self.getNodeName(classNode, tag='compoundname'))

		referenced_types = set()
		referenced_type_ids = set()

		xml_members = self.getMemberSectionDefs(classNode)
		for member_id in class_['members']:
			sectiondef, memberdef = xml_members[member_id]
			member = self.items[member_id]

			# print(memberdef)
			# print(memberdef.__dict__)

			assert(member['kind'] == memberdef.attrib['kind'])

			member['section'] = sectiondef.attrib['kind']
			member['description'] = {
				'brief':   self.getChildInnerXml(memberdef, 'briefdescription', preserveChildNodes = True),
				'details': self.getChildInnerXml(memberdef, 'detaileddescription', preserveChildNodes = True),
				'inbody':  self.getChildInnerXml(memberdef, 'inbodydescription', preserveChildNodes = True)
			}
			loc = self.getChildNode(memberdef, 'location')
			# print(loc)
			# print(list(memberdef.iter('location')))
			# if loc:

			assert(member['name'] == class_['name'] + '::' + self.getNodeName(memberdef))
			# member['name'] = self.getNodeName(memberdef)
			member['file'] = loc.attrib['file']
			member['line'] = loc.attrib['line']
			member['type'] = self.getChildInnerXml(memberdef, 'type', preserveChildNodes = False)
			member['params'] = [{
				'name': self.getInnerXml(self.getChildNode(param, 'declname'), preserveChildNodes = False),
				'type': self.getInnerXml(self.getChildNode(param, 'type'), preserveChildNodes = False)
			} for param in memberdef.iter('param')]

			if member['params']:
				print(member['name'])
				print(member['type'])
				print(member['params'])

			# 	def showInternals(obj):
			# 		if obj is not None:
			# 			return obj.__dict__
			# 		return None

				# print([ (showInternals(self.getChildNode(param, 'type')), showInternals(self.getChildNode(param, 'declname'))) for param in memberdef.iter('param')])
				# print()

			referenced_types.add(self.getChildInnerXml(memberdef, 'type', preserveChildNodes = False))
			for ref in self.getChildNode(memberdef, 'type').iter('ref'):
				try:
					referenced_type_ids.add(ref.attrib['refid'])
				except AttributeError:
					print("WARNING: ref has no refid: %s %s"%(ref, ref.__dict__))

			for param in memberdef.iter('param'):
				referenced_types.add(self.getChildInnerXml(param, 'type', preserveChildNodes = False))

		# classes[name] = class_

		print("Scanned %s %s"%(class_['kind'], class_['name']))
		if referenced_types:
			print("%d referenced type(s): %s"%(len(referenced_types), ', '.join(referenced_types)))
			print("%d referended refid(s): %s"%(len(referenced_type_ids), ', '.join(referenced_type_ids)))
		
		class_['referenced_type_ids'] = referenced_type_ids
		class_['referenced_types']    = referenced_types
		class_['recursive_type_list']  = set(referenced_types)

		print("Loading classes...")
		for refid in referenced_types:
		 	cls = self.scanItem(refid)
		 	if cls is None:
		 		print("Null scanItem(): '%s'"%refid)
		 		assert(False)
		 	class_['recursive_type_list'] |= cls['recursive_type_list']
		return class_

	def getCompoundDefWithId(self, root, refid):
		for compound in root.iter('compounddef'):
			if compound.attrib['id'] == refid:
				return compound

	def getMemberSectionDefs(self, compounddef):
		def iterSectionsAndMembers ():
			for sectiondef in compounddef.iter('sectiondef'):
				for memberdef in sectiondef.iter('memberdef'):
					yield (memberdef.attrib['id'], (sectiondef, memberdef))
		return dict(iterSectionsAndMembers())

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


	def getNodeName(self, node, tag = 'name', assignToNode = False):
		''' Returns the name of an doxygen xml node, where 'tag' is the name of the xml tag containing the name.
		Can be used to get the contents of other simple nodes as well, so this may need to be renamed/refactored...
		'''
		if tag in node.__dict__:
			return node.__dict__[tag]
		name = [ ''.join(elem.itertext()) for elem in node.iter(tag) ][0]
		if assignToNode:
			node.__dict__[tag] = name
		return name

	def getChildInnerXml(self, node, tag, **kwargs):
		return self.getInnerXml(self.getChildNode(node, tag) or '', **kwargs)

	def getInnerXml(self, node, preserveChildNodes = False, ignoredTags = None):
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
		# return ((preserveChildNodes and getInnerWithTags) or getInnerWithoutTags)(node)
		# return inner.strip() != '' and inner or ''

		# print(node.__dict__)
		# if preserveChildNodes:
			# return getInnerWithTags(node)
		# return getInnerWithoutTags(node)
			# return ''.join(map(getInnerWithTags, node))
		# return ''.join(map(getInnerWithoutTags, node))


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

	def getChildNode(self, node, tag):
		elems = list(node.iter(tag))
		if len(elems) > 0:
			return elems[0]
		return None
		# return ((len(elems) > 0) and elems[0]) or None

	def getQObjectList(self):
		if not '_class_list' in self.__dict__:
			if not 'index' in self.__dict__ or self.index is None:
				self._reloadIndex()
			classTypes = set(['class', 'struct'])
			self._class_list = [ (
				self.getNodeName(elem), elem.attrib['refid']) 
				for elem in self.index.iter('compound') 
				if elem.attrib['kind'] ]
		return self._class_list

	def getClassIndex(self, name):
		''' Returns the doxygen class node from index.xml '''
		if not 'index' in self.__dict__ or self.index is None:
			self._reloadIndex()
		classTypes = set(['class', 'struct'])
		for node in self.index.iter('compound'):
			if node.attrib['kind'] in classTypes and self.getNodeName(node, assignToNode=True) == name:
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
					print('%s:\n\t%s'%(category, ', '.join([ self.getNodeName(node) for node in values ])))

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
			# print('section %s: '%(section.attrib['kind']) + ', '.join([ self.getNodeName(member) for member in section.iter('memberdef') ]))
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
		methodInfo['name'] = self.getNodeName(methodnode)

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
			'name': self.getNodeName(attribnode),
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
	scanner.loadIndex(print_indexed_items = False, print_index_summary = True)

	scanner.getClass('EntityScriptingInterface')
	# print(scanner.loadClass('EntityScriptingInterface'))


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
