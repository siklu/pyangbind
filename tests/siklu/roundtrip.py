#!/usr/bin/env python

import logging
import os
import sys
import importlib

from lxml import objectify
from lxml import etree
from pyangbind.lib.serialise import pybindIETFXMLDecoder, pybindIETFXMLEncoder

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


"""
Populated PyangBind class is not useful in and of itself,
So the common use case is that they are sent to a external system (e.g., a router, or other NMS component). 
To achieve this the class hierarchy needs to be serialized (encoded) into a format that can be sent to the remote entity.
PyangBind class can be serialized into any of the supported formats including XML and JSON.
All netconf  in/out messages payloads are YANG model entities encoded in XML format,
The rules for this mapping are defined in RFC 7950.
Current Test uses XML payload as an input to verify data integrity between decoding/encoding PyangBind methods using Siklu YANG model. 
"""


class XMLDeserialise():

    def __init__(self, test_param=None):
        # Validate and process arguments
        self.parse_args(test_param)

    def parse_args(self, test_param):
        if test_param is None:
            print("Missing test param")
        self.bindings_path = test_param['bindings_path']
        self.xml_path = test_param['xml_path']

    def get_model(self, module_name):
        for filename in os.listdir(self.bindings_path):
            b = os.path.join(self.bindings_path, filename)
            x = os.path.join(self.xml_path, os.path.basename(b).replace('py', 'xml'))
            current_module_name = os.path.basename(b).split('.')[0]
            if os.path.isfile(b) and os.path.isfile(x) and current_module_name == module_name:
                return {'bindings': b, 'xml_file': x, 'module_name': module_name}
        logging.getLogger().error("\nModule: " + module_name + " was not found")

    def test_deserialise_full_container_roundtrip(self, module_name=None):
        logging.getLogger().info("\nModule name: " + module_name)
        model = self.get_model(module_name)
        if not model:
            return False
        with open(os.path.join(os.path.dirname(__file__), 'xml', model['xml_file']), "r") as fp:
            external_xml = fp.read()
            existing_doc = objectify.fromstring(external_xml)
            bindings = importlib.import_module('gen.'
                                               + model['module_name'], package=None)
            result = pybindIETFXMLDecoder().decode(
                external_xml, bindings, model['module_name'])
            doc = pybindIETFXMLEncoder().encode(result)
            if not self.xml_tree_equivalence(doc, existing_doc):
                logging.getLogger().error("\nEncoded XML: \n" + etree.tostring(doc, pretty_print=True).decode("utf-8"))
                return False
        return True

    def xml_tree_equivalence(self, e1, e2):
        """
        Rough XML comparison function based on https://stackoverflow.com/a/24349916/1294458.
        This is necessary to provide some sort of structural equivalence of a generated XML
        tree; however there is no XML deserialisation implementation yet. A naive text comparison
        fails because it seems it enforces ordering, which seems to vary between python versions
        etc. Strictly speaking, I think, only the *leaf-list* element mandates ordering.. this
        function uses simple sorting on tag name, which I think, should maintain the relative
        order of these elements.
        """
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if e1.tail != e2.tail:
            return False
        if e1.attrib != e2.attrib:
            return False
        if len(e1) != len(e2):
            return False
        e1_children = sorted(e1.getchildren(), key=lambda x: x.tag)
        e2_children = sorted(e2.getchildren(), key=lambda x: x.tag)
        if len(e1_children) != len(e2_children):
            return False
        return all(self.xml_tree_equivalence(c1, c2) for c1, c2 in zip(e1_children, e2_children))

