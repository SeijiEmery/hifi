
import os.path
from scanner import ScriptApiScanner
import json

class JsdocGenerator:
	def __init__ (self, jsconfig):
		with open(jsconfig, 'r') as f:
			self.jsconfig = json.load(f)

	def generate (self, scannedContent):
		classes = dict(scannedContent)

		for v in self.jsconfig['global-objects']:
			clsinfo, jsobj = classes[v['cpp']], v['js']

			print('%s exposed as %s:'%(v['cpp'], v['js']))
			print(clsinfo)



if __name__ == '__main__':
	generator = JsdocGenerator('interface-api.json')

	os.chdir('../../')		# cd to root dir
	scanner = ScriptApiScanner('docs/xml')
	# scanner.reloadIndex()

	generator.generate(scanner.scanAllFiles())


