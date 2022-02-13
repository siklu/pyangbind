#!/usr/bin/env python

import shutil
from parameterized import parameterized
import unittest
import sys

from roundtrip import *


class XMLDeserialiseTest(unittest.TestCase):

    def setUp(self):
        self.test_param = {
            'bindings_path': sys.argv[2],
            'xml_path': 'xml'
        }
        bindings_dest = os.getcwd() + '/' + os.path.basename(self.test_param['bindings_path'])
        xml_dest = os.getcwd() + '/' + os.path.basename(self.test_param['xml_path'])
        # remove destination first
        shutil.rmtree(bindings_dest, ignore_errors=True)
        # copy remote repo bindings
        shutil.copytree(self.test_param['bindings_path'], bindings_dest)
        self.test_param['bindings_path'] = bindings_dest
        # create test object
        self.test = XMLDeserialise(self.test_param)

    @parameterized.expand(["radio_bridge_tg_radio_dn",
                           "radio_bridge_tg_radio_common",
                           "radio_bridge_tg_system",
                           "radio_bridge_tg_ip",
                           "radio_bridge_tg_interfaces",
                           "radio_bridge_tg_user_bridge",
                           "radio_bridge_tg_inventory"])
    def test_roundtrip(self, module):
        self.assertTrue(self.test.test_deserialise_full_container_roundtrip(module),
                        "Generated XML did not match the expected output.")

    def tearDown(self):
        # remove generated bindings
        shutil.rmtree(self.test_param['bindings_path'], ignore_errors=True)
        

if __name__ == "__main__":
    unittest.main()
