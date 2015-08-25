import os
import xmlParser

os.chdir(r'C:\Documents and Settings\Joona\My Documents\CodeVault\far_out_repo_work')
xml = xmlParser.ZigXmlParser(os.getcwd() + r'\Zig_input.xml')
print xml.read_element('alpha', 2)
xml.write_element('alpha', 2, 0.023)
print xml.read_element('alpha', 2)
xml.write_xml_file()