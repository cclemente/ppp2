
import os
from lxml import etree
from xml.etree.ElementTree import ElementTree


class Settings(object):
	def __init__(self, ppp_main_fname):
		self.dir_ppp        = os.path.split(__file__)[0]
		self.dir_project    = None
		self.fname_settings = os.path.join(self.dir_ppp,  'settings.xml')
		self.root           = None
		self.tree           = None
		self._init()
		
	def _create(self):
		root     = etree.Element('ppp_settings', version='0.0.0001')
		el       = etree.Element('directories')
		el0      = etree.Element('project')
		el0.text = os.curdir
		el.append(el0)
		root.append(el)
		### write:
		s = etree.tostring(root, pretty_print=True, xml_declaration=True)
		fid = open(self.fname_settings, 'w')
		fid.write(s)
		fid.close()
		
	def _init(self):
		if not os.path.exists(self.fname_settings):
			self._create()
		self._parse()
			
	def _parse(self):
		self.tree        = ElementTree()
		self.tree.parse(self.fname_settings)
		self.root        = self.tree.getroot()
		dir0             = self.root.find('directories/project').text
		if not os.path.isdir(dir0):
			self.set_dir_project('.')
			self._parse()
			# raise(ValueError('In the settings.xml file, <director><project> contains an invalid directory.'))
		self.dir_project = dir0
		
	def _write(self):
		self.tree.write(self.fname_settings, xml_declaration=True)
	
	def set_dir_project(self, dir0):
		if not os.path.exists(dir0):
			raise(ValueError('The specified directory does not exist.'))
		if not os.path.isdir(dir0):
			raise(ValueError('The specified value is an invalid directory.'))
		leaf             = self.root.find('directories/project')
		leaf.text        = dir0
		self._write()
		

# __file__  = '/Users/todd/Documents/Python/myLibraries/ppp/ppp_main.py'
# settings = Settings(__file__)
# print settings.dir_project