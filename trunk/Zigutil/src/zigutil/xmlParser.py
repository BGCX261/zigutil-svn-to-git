#!/usr/bin/python
# coding=utf-8

import os
from datetime import date
from elementtree.ElementTree import Element, ElementTree, parse, dump

class ZigXmlParser(object):

	def __init__(self, input):
		self.filename = os.path.split(input)[-1]
		self.xmltree = parse(input).getroot()
		self.TODAY = date.today().isoformat()
		self.tag_names = ['ID',
						  'creator',
						  'created_date',
						  'modified_date',
						  'weight',
						  'aplha',
						  'BQP',
						  'BQP_buffer',
						  'cell_removal',
						  'spp_file']

	def read_element(self, element, idvalue):
		for target in self.xmltree.findall('feature'):
			if target.find('ID').text == str(idvalue):
				return target.find(element).text
		
	def write_element(self, element, idvalue, value):
		# Set modified_date for the inputset
		self.xmltree.find('modified_date').text = self.TODAY
		for target in self.xmltree.findall('feature'):
			if target.find('ID').text == str(idvalue):
				target.find(element).text = str(value)
				# Set modified_date for the specific element
				target.find('modified_date').text = self.TODAY

	def create_new_feature(self, location=None):
		self.feature = Element('feature')
		for elem in self.tag_names:
			self.feature.append(Element(elem))
		if not location:
			self.xmltree.append(self.feature)
		else:
			self.xmltree.insert(location, self.feature)
		self.indent(self.xmltree)
		
	def write_xml_file(self):
		ElementTree(self.xmltree).write(os.getcwd() + r'\mod_' + self.filename)
		print os.getcwd() + r'\mod_' + self.filename
		
	def show_xml_tree(self):
		dump(self.xmltree)
		
	def indent(self, elem, level=0):
		""" Adds tab to the tree, so that saving it as usual results in a prettyprinted tree."""
		i = "\n" + level * "\t"
		if len(elem):
			if not elem.text or not elem.text.strip():
				elem.text = i + "\t"
			for elem in elem:
				self.indent(elem, level+1)
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
		else:
			if level and (not elem.tail or not elem.tail.strip()):
				elem.tail = i

if __name__ == '__main__':
	test_input = os.getcwd() + r'\xml\Zig_input.xml'
	xml = ZigXmlParser(test_input)
	xml.show_xml_tree()