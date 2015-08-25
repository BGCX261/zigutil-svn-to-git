#!/usr/bin/python
# coding=utf-8

import os
from datetime import date
from xml.etree.cElementTree import Element, ElementTree, parse, dump
from xmltodict import dictlist

class ZigXmlParser(object):

    def __init__(self, infile):
        self.filename = os.path.split(infile)[-1]
        self.xmltree = parse(self.filename).getroot()
        self.today = date.today().isoformat()
        self.feature = None
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

    def xml2list(self):
        return dictlist(self.xmltree)
        
    def write_element(self, element, idvalue, value):
        # Set modified_date for the inputset
        self.xmltree.find('modified_date').text = self.today
        for target in self.xmltree.findall('feature'):
            if target.find('ID').text == str(idvalue):
                target.find(element).text = str(value)
                # Set modified_date for the specific element
                target.find('modified_date').text = self.today

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

    def indent(self, eleme, level=0):
        """ Adds tab to the tree, so that saving it as usual results in a 
        prettyprinted tree."""
        i = "\n" + level * "\t"
        if len(eleme):
            if not eleme.text or not eleme.text.strip():
                eleme.text = i + "\t"
            for elem in eleme:
                self.indent(elem, level+1)
            if not eleme.tail or not eleme.tail.strip():
                eleme.tail = i
        else:
            if level and (not eleme.tail or not eleme.tail.strip()):
                eleme.tail = i

if __name__ == '__main__':
    testinput = 'Zig_input.xml'
    xml = ZigXmlParser(testinput)
    print xml.xml2list()