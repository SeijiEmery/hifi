
import os.path
from multiprocessing import Pool
from xml.etree import ElementTree

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




def gettext(node):
	return ''.join([ text for text in node.itertext() ])

def getname(node):
	return gettext([ name for name in node.iter('name') ][0])

def gettag(node, tag):
	return gettext([ elem for elem in node.iter(tag) ][0])

class XmlClassFileScanner:
	''' Loads and scans a class_**********.xml file '''

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
		# print('scanning class: ' + gettag(node, 'compoundname'))
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

		info = {}
		if api_exposed_methods or qt_public_slots or qt_properties:
			print("Exposed class: %s"%name)
			if api_exposed_methods:
				print("SCRIPT_API:   " + ', '.join([ name for name, _ in api_exposed_methods]))
				info['exposed_methods'] = api_exposed_methods
			if qt_public_slots:
				print("public slots: " + ', '.join([ slot for slot, _ in qt_public_slots]))
				info['exposed_slots'] = qt_public_slots
			if qt_properties:
				print("properties:   " + ', '.join([ name for name, _ in qt_properties]))
				info['exposed_properties'] = qt_properties
			print('')
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

	def reloadIndex (self):
		file_ = os.path.join(self.xmlpath, "index.xml")
		index = ElementTree.parse(file_).getroot()

		scannableItems = [ 'class', 'struct', 'namespace', 'var', 'function' ]
		self.classFiles = set([])

		# Scan entries
		for node in index.iter('compound'):
			kind = node.attrib['kind']
			if kind in scannableItems:
				self.classFiles.add(os.path.join(self.xmlpath, node.attrib['refid'] + '.xml'))

	def scanAllFiles (self):
		if not 'classFiles' in self.__dict__:
			self.reloadIndex()

		pool = Pool(16)
		results = pool.map(scanFile, self.classFiles)

		# Flatten array and remove empty elements
		results_ = []
		for result in results:
			if result:
				results_ += result
		return results_


if __name__ == '__main__':
	os.chdir('../../')	# Navigate to root hifi directory

	if not os.path.isfile('docs/config.txt'):
		print('Missing doxygen config file')
		system.exit(-1)

	if not os.path.isfile('docs/xml/index.xml'):
		print('Generating docs...')
		os.system('doxygen docs/config.txt')
		print('Generated docs in <hifi dir>/docs')

	assert(os.path.isfile('docs/xml/index.xml'))

	scanner = ScriptApiScanner('docs/xml')
	results = scanner.scanAllFiles()

	num_api_methods = sum([ len(info['exposed_methods']) for name, info in results if 'exposed_methods' in info ])
	num_qt_slots    = sum([ len(info['exposed_slots'])   for name, info in results if 'exposed_slots' in info ])
	num_qt_props    = sum([ len(info['exposed_properties']) for name, info in results if 'exposed_properties' in info ])
	untagged_methods = num_qt_slots + num_qt_props - num_api_methods

	num_tagged = lambda (name, info): len(info['exposed_methods']) if 'exposed_methods' in info else 0
	num_slots  = lambda (name, info): len(info['exposed_slots'])   if 'exposed_slots'   in info else 0
	num_props  = lambda (name, info): len(info['exposed_properties']) if 'exposed_properties' in info else 0
	# num_total  = lambda (name, info): num_slots((name, info)) + num_props((name, info))


	# fully_tagged_classes = len([ 1 for name, info in results if num_tagged(info) != 0 and num_tagged(info) == num_total(info) ])
	# tagged_classes       = len([ 1 for name, info in results if num_tagged(info) != 0 ])

	tags = map(num_tagged, results)
	tagged_classes = filter(lambda n: n != 0, tags)
	fully_tagged_classes = []

	# tagged_classes       = filter(lambda name, info: num_tagged(name, info) != 0, results)
	# fully_tagged_classes = filter(lambda name, info: num_tagged(name, info) == num_total(info), tagged_classes)

	# print(map(num_tagged, results))
	# print(map(lambda info: info['exposed_slots'] if 'exposed_methods' in info else [], results, results))

	# print(tagged_classes)
	# print(fully_tagged_classes)

	num_tagged_classes   = len(tagged_classes)
	num_untagged_classes = len(results) - num_tagged_classes

	print("Finished scanning %d files."%len(scanner.classFiles))
	print("Results: ")
	print("    %d exposed classes (%d tagged, %d untagged)"%(len(results), num_tagged_classes, num_untagged_classes))
	print("    %d exposed methods (%d tagged, %d untagged)"%(num_qt_props + num_qt_slots, num_api_methods, untagged_methods))

