#!/usr/bin/env python

import os.path
import unittest

import pyangbind.lib.pybindJSON as pbJ
from pyangbind.lib.xpathhelper import YANGPathHelper
from tests.base import PyangBindTestCase


class OpenconfigInterfacesTests(PyangBindTestCase):
  yang_files = [
    os.path.join("openconfig", "%s.yang" % fname) for fname in
    ["openconfig-interfaces", "openconfig-if-aggregate", "openconfig-if-ip"]
  ]
  pyang_flags = [
    '-p %s' % os.path.join(os.path.dirname(__file__), "include"),
    '--use-xpathhelper',
    '--lax-quote-checks',
  ]
  split_class_dir = True
  module_name = 'ocbind'

  remote_yang_files = [
    {
      'local_path': 'include',
      'remote_prefix': 'https://raw.githubusercontent.com/robshakir/yang/master/standard/ietf/RFC/',
      'files': [
        'ietf-inet-types.yang',
        'ietf-yang-types.yang',
        'ietf-interfaces.yang',
      ]
    },
    {
      'local_path': 'include',
      'remote_prefix': 'https://raw.githubusercontent.com/openconfig/public/master/release/models/',
      'files': [
        'openconfig-extensions.yang',
        'types/openconfig-types.yang',
        'vlan/openconfig-vlan.yang',
        'vlan/openconfig-vlan-types.yang',
        'types/openconfig-inet-types.yang',
        'types/openconfig-yang-types.yang',
      ],
    },
    {
      'local_path': 'openconfig',
      'remote_prefix': 'https://raw.githubusercontent.com/openconfig/public/master/release/models/',
      'files': [
        'interfaces/openconfig-if-ip.yang',
        'interfaces/openconfig-if-ethernet.yang',
        'interfaces/openconfig-if-aggregate.yang',
        'interfaces/openconfig-interfaces.yang',
      ],
    },
  ]

  def setUp(self):
    self.yang_helper = YANGPathHelper()
    self.instance = self.ocbind.openconfig_interfaces(path_helper=self.yang_helper)

  def test_001_populated_intf_type(self):
    i0 = self.instance.interfaces.interface.add("eth0")
    self.assertEqual(len(i0.config.type._restriction_dict), 1)


class OpenconfigIANATests(PyangBindTestCase):
  yang_files = [
    os.path.join("include", "%s.yang" % fname) for fname in
    ["openconfig-interfaces", "openconfig-if-aggregate", "openconfig-if-ethernet",
     "openconfig-if-ip-ext", "openconfig-if-ip", "openconfig-vlan", "iana-if-type"]
  ]
  pyang_flags = [
    '-p %s' % os.path.join(os.path.dirname(__file__), "include"),
    '--lax-quote-checks',
  ]
  module_name = 'openconfig_interfaces'

  remote_yang_files = [
    {
      'local_path': 'include',
      'remote_prefix': 'https://raw.githubusercontent.com/openconfig/public/master/release/models/',
      'files': [
        'interfaces/openconfig-if-aggregate.yang',
        'interfaces/openconfig-if-ethernet.yang',
        'interfaces/openconfig-if-ip-ext.yang',
        'interfaces/openconfig-if-ip.yang',
        'interfaces/openconfig-interfaces.yang',
        'types/openconfig-inet-types.yang',
        'types/openconfig-types.yang',
        'types/openconfig-yang-types.yang',
        'vlan/openconfig-vlan-types.yang',
        'vlan/openconfig-vlan.yang',
        'openconfig-extensions.yang',
      ]
    },
    {
      'local_path': 'include',
      'remote_prefix': 'https://github.com/YangModels/yang/raw/master/standard/ietf/RFC/',
      'files': [
        'iana-if-type.yang',
      ]
    }
  ]

  def test_load_ietf_json_with_iana_if_type(self):
    allowed = True
    try:
      pbJ.load_ietf(
        os.path.join(os.path.dirname(__file__), 'fail_xslt_iana.json'),
        self.openconfig_interfaces,
        'openconfig-interfaces'
      )
    except ValueError:
      allowed = False
    self.assertTrue(allowed)


if __name__ == '__main__':
  unittest.main()
