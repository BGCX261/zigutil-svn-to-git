#!/usr/bin/python
# coding=utf-8

from xml.etree.cElementTree import parse

def dictlist(node):
    res = {}
    res[node.tag] = []
    xmltodict(node,res[node.tag])
    reply = {}
    reply[node.tag] = {'value':res[node.tag],'attribs':node.attrib,'tail':node.tail}
    
    return reply

def xmltodict(node,res):
    rep = {}
    
    if len(node):
        #n = 0
        for n in list(node):
            rep[node.tag] = []
            value = xmltodict(n,rep[node.tag])
            if len(n):
            
                value = {'value':rep[node.tag],'attributes':n.attrib,'tail':n.tail}
                res.append({n.tag:value})
            else :      
                res.append(rep[node.tag][0])      
    else:
        value = {}
        value = {'value':node.text,'attributes':node.attrib,'tail':node.tail}
        
        res.append({node.tag:value})
    
    return 
        
def main():
    tree = parse('Zig_input.xml')
    res = dictlist(tree.getroot())
    print res
    
    
if __name__ == '__main__' :
    main()