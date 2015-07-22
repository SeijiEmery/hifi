
import unittest
import os
from xml.etree import ElementTree
from scanner import XmlScanner, autobuild


class TestDoxygenScanner (unittest.TestCase):
	def testFoo(self):
		self.assertTrue(True)

	def setUp(self):
		os.chdir('../../')
		autobuild()
		self.scanner = XmlScanner('docs/xml')

	def testInnerXml(self):
		sample_xml = '''<memberdef kind="variable" id="class_overlays_1acd4d6e1f069b505eb5a4cf81fcb36b9e" prot="private" static="no" mutable="no">
        <type>QMap&lt; unsigned int, <ref refid="class_overlay_1a348ec86ee3beadeff8db130170d6b66a" kindref="member">Overlay::Pointer</ref> &gt;</type>
        <definition>QMap&lt;unsigned int, Overlay::Pointer&gt; Overlays::_overlaysHUD</definition>
        <argsstring></argsstring>
        <name>_overlaysHUD</name>
        <briefdescription>
        <para>example. Uses <ref refid="class_overlay_1a348ec86ee3beadeff8db130170d6b66a" kindref="member">Overlay::Pointer</ref>.</para>
        </briefdescription>
        <detaileddescription>
        </detaileddescription>
        <inbodydescription>
        </inbodydescription>
        <location file="/Users/semery/hifi-docgen/interface/src/ui/overlays/Overlays.h" line="95" column="1" bodyfile="/Users/semery/hifi-docgen/interface/src/ui/overlays/Overlays.h" bodystart="95" bodyend="-1"/>
      </memberdef>'''

		xml = ElementTree.fromstring(sample_xml)
		self.assertEqual(XmlScanner.getInnerXml(xml, 'name').strip(), '_overlaysHUD')
		self.assertEqual(XmlScanner.unxmlify(XmlScanner.getInnerXml(xml, 'type', preserveChildNodes = False).strip()), 'QMap< unsigned int, Overlay::Pointer >')
		self.assertEqual(XmlScanner.getInnerXml(xml, 'type', preserveChildNodes = True).strip(), '''
			QMap&lt; unsigned int, <ref refid="class_overlay_1a348ec86ee3beadeff8db130170d6b66a" kindref="member">Overlay::Pointer</ref> &gt;
			'''.strip())
		self.assertEqual(XmlScanner.unxmlify(XmlScanner.getInnerXml(xml, 'type', ignoredTags = set(['ref'])).strip()), 'QMap< unsigned int, Overlay::Pointer >')
		self.assertEqual(XmlScanner.getInnerXml(xml, 'type', ignoredTags = set(['foo'])).strip(), '''
			QMap&lt; unsigned int, <ref refid="class_overlay_1a348ec86ee3beadeff8db130170d6b66a" kindref="member">Overlay::Pointer</ref> &gt;
			'''.strip())
		self.assertEqual(XmlScanner.getInnerXml(xml, 'briefdescription', ignoredTags = set(['ref'])).strip(), '''
			<para>example. Uses Overlay::Pointer.</para>
			'''.strip())
		self.assertEqual(XmlScanner.getInnerXml(xml, 'briefdescription', ignoredTags = set(['ref', 'para'])).strip(), '''
			example. Uses Overlay::Pointer.
			'''.strip())
		self.assertEqual(XmlScanner.getInnerXml(xml, 'briefdescription', preserveChildNodes = False, ignoredTags = set(['ref'])).strip(), '''
			example. Uses Overlay::Pointer.
			'''.strip())

	def testIndexScan(self):
		pass

if __name__ == '__main__':
	unittest.main()




























































