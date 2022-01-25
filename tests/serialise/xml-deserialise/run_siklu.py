#!/usr/bin/env python

import os
import sys
import unittest

# make PyangBindTestCase class available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')))

from lxml import objectify
from pyangbind.lib.serialise import pybindIETFXMLDecoder, pybindIETFXMLEncoder
from tests.base import PyangBindTestCase
from tests.serialise.xml_utils import xml_tree_equivalence

"""
Populated PyangBind class is not useful in and of itself,
So the common use case is that they are sent to a external system (e.g., a router, or other NMS component). 
To achieve this the class hierarchy needs to be serialized (encoded) into a format that can be sent to the remote entity.
PyangBind class can be serialized into any of the supported formats including XML and JSON.
All netconf  in/out messages payloads are YANG model entities encoded in XML format,
The rules for this mapping are defined in RFC 7950.
Current Test uses XML payload as an input to verify data integrity between decoding/encoding PyangBind methods using Siklu YANG model. 
"""
class XMLDeserialiseTests(PyangBindTestCase):

    yang_files = ["radio-bridge-tg-radio-dn.yang"]
    maxDiff = None

    def test_deserialise_full_container_roundtrip(self):
        with open(os.path.join(os.path.dirname(__file__), "xml", "siklu.xml"), "r") as fp:
            
            external_xml = fp.read()
            existing_doc = objectify.fromstring(external_xml)

        result = pybindIETFXMLDecoder().decode(external_xml, self.bindings, "radio-bridge-tg-radio-dn")
        doc = pybindIETFXMLEncoder().encode(result)

        self.assertTrue(xml_tree_equivalence(doc, existing_doc), "Generated XML did not match the expected output.")


if __name__ == "__main__":
    unittest.main()
