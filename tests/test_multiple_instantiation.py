
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import multiple_instantiation as mi
from cromulent.model import factory, Person, DataError, Dimension


class TestMIClasses(unittest.TestCase):

	def test_destruction(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Activity/1'), 
			('type', ['Destruction', 'Activity']), ('_label', "Test Destruction")])
		mi.DestructionActivity._okayToUse = 1
		da = mi.DestructionActivity("1")
		da._label = "Test Destruction"
		factory.context_uri = ""
		dajs = factory.toJSON(da)
		self.assertEqual(dajs, expect)

