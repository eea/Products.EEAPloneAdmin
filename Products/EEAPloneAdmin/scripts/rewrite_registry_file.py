#!/usr/bin/python
""" A script to rewrite a [js/css]registry.xml file to an optimization format
"""
import sys
import lxml.etree
import string

def main():
    if len(sys.argv) != 3:
        print "You need to provide paths to input and output file"

    input, output = map(string.strip, sys.argv[1:])

    _type = None

    if 'cssregistry.xml' in input:
        _type = 'stylesheet'
    if 'jsregistry.xml' in input:
        _type = 'javascript'

    if not _type:
        print "Invalid named input file, has ",
        print "to be either jsregistry.xml or cssregistry.xml"

    with open(input) as f:
        s = f.read()

    e = lxml.etree.fromstring(s)
    obj = lxml.etree.Element('object')
    for k, v in e.items():
        obj.set(k, v)

    scripts = e.xpath('//' + _type)

    previous = None
    for script in scripts:
        es = lxml.etree.SubElement(obj, _type)
        for k, v in script.items():
            if k not in ['after', 'insert-after',
                         'position-top', 'update']:
                es.set(k, v)
        if previous:
            es.set('insert-after', previous)
        else:
            es.set('insert-top', 'true')

        #es.set('update', 'true')

        previous = es.get('id')

    out = open(output, 'w')
    out.write(lxml.etree.tostring(obj, pretty_print=True, standalone=True))

if __name__ == "__main__":
    main()
