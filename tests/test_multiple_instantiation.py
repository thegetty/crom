
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

# Windows - 1. win directory fix  2. Modify import statements accordingly
import sys
import os
curr_dir = os.path.dirname(__file__)
crom_dir = os.path.abspath(os.path.join(curr_dir, '..', 'cromulent'))
sys.path.append(crom_dir)

import multiple_instantiation as mi
from model import factory, Person, DataError, Dimension
#from cromulent import multiple_instantiation as mi
#from cromulent.model import factory, Person, DataError, Dimension
##

class TestMIClasses(unittest.TestCase):

	def test_destruction(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Activity/1'), 
			('type', ['Destruction', 'Activity']), ('label', "Test Destruction")])
		mi.DestructionActivity._okayToUse = 1
		da = mi.DestructionActivity("1")
		da.label = "Test Destruction"
		factory.context_uri = ""
		dajs = factory.toJSON(da)
		self.assertEqual(dajs, expect)

