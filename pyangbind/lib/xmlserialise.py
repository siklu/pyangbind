"""
Copyright 2015  Rob Shakir (rjs@jive.com, rjs@rob.sh)

This project has been supported by:
          * Jive Communcations, Inc.
          * BT plc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

serialise:
  * module containing methods to serialise pyangbind class hierarchie
    to various data encodings. XML and/or JSON as the primary examples.
"""

from collections import OrderedDict
from decimal import Decimal
from pyangbind.lib.yangtypes import safe_name
import copy
import sys
from lxml import etree

class pybindXMLEncoderException(Exception):
  pass

class pybindXMLEncoder(object):

  @staticmethod
  def encode(path_helper):
    #
    # path_helper is expected to be an instance of a YANGPathHelper, this is an object
    # that each class registers against when path_helper is supplied to it as an argument,
    # and the --use-xpathhelper switch is used.
    #
    # The reason that we start with this is because it actually maintains an internal XML
    # document that allows XPATH expressions to be resolved for the classes. This means that
    # it has something that looks like the XML encoding already, albeit that this document
    # does not have the actual values - we can use it as a starting point to generate the
    # serialised XML document.
    #
    # The downside of using this is that we require --use-xpathhelper to be used for implementations
    # that want to serialise to XML - this is a little annoying if you're just doing client-side
    # code that generates a single instance to ship to a server, and never need to reference the
    # object again. However, the cost to do this is pretty low. An alternative approach would
    # use the object structure itself like the JSON serialisers. At the time of writing this
    # is left as an exercise to the reader.
    #
    def append_namespace_if_different(library, parent, child):
      # set the namespace of an element if it does not match the parent's namespace.
      setns = False

      if not "obj_ptr" in parent.attrib:
        setns = True
      elif not "obj_ptr" in child.attrib:
        return
      elif not library[parent.attrib["obj_ptr"]]._namespace == library[child.attrib["obj_ptr"]]._namespace:
        setns = True

      if setns:
        child.attrib['xmlns'] = library[child.attrib["obj_ptr"]]._namespace

    if hasattr(path_helper, "_root") is False or hasattr(path_helper, "_library") is False:
      raise pybindXMLEncoderException("Invalid XPathHelper object specified")

    xml_root_object = path_helper._root
    library = path_helper._library
    xml_doc = copy.deepcopy(xml_root_object)

    for elem in xml_doc.iter("*"):
      if "obj_ptr" in elem.attrib:
        if library[elem.attrib["obj_ptr"]]._is_leaf:
          # if specific handling is needed here for encoding, then the
          # _yang_type can be checked. A specific case where this is
          # required is that we need to distinguish 'empty' types from
          # boolean types. This might not work with derived types (a typedef
          # that uses empty within it). In this case then we would need
          # YANGBool to have an attribute that stores what type of boolean
          # it is storing.
          if library[elem.attrib["obj_ptr"]]._yang_type == "empty":
            pass
          else:
            obj = library[elem.attrib["obj_ptr"]]
            if obj._default is False and obj._changed():
              elem.text = unicode(obj)
            elif obj._default and not obj == obj._default:
              elem.text = unicode(obj)
            else:
              elem.getparent().remove(elem)
              continue
        elif library[elem.attrib["obj_ptr"]]._is_container:
          pass
        else:
          # this is a leaflist - so we need to add new elements to the document
          # that correspond to the leaflist element
          parent = elem.getparent()
          for item in library[elem.attrib["obj_ptr"]]:
            added_item = etree.SubElement(parent, elem.tag)
            added_item.text = unicode(item)
            append_namespace_if_different(library, parent, added_item)
          parent.remove(elem)
          continue

        append_namespace_if_different(library, elem.getparent(), elem)

    #
    # Go through and remove the object ptr if it has one, as this is not required in the serialisation
    # also remove empty containers or lists.
    #
    for elem in xml_doc.iter("*"):
      try:
        if library[elem.attrib["obj_ptr"]]._is_container and not len(elem):
          elem.getparent().remove(elem)
      except KeyError:
        # this is an element that we added ourselves during serialisation
        pass
      if "obj_ptr" in elem.attrib:
        del elem.attrib["obj_ptr"]

    #
    # We actually return an XML document here that starts with <root> this
    # is because there can be multiple elements at the root of the YANG tree,
    # and we don't know what the code that has called this function is actually doing with it
    # - it will usually wrap these elements in another container, so will need to restructure
    # the document itself. Using <root> lets us hand back one document.
    #
    e = etree.ElementTree(xml_doc)
    return e

