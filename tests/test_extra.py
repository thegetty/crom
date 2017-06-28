
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import extra
from cromulent.model import factory, Person, DataError, Dimension


class TestExtraClasses(unittest.TestCase):

	def test_destruction(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Activity/1'), 
			('type', ['Destruction', 'Activity']), ('label', "Test Destruction")])
		extra.DestructionActivity._okayToUse = 1
		da = extra.DestructionActivity("1")
		da.label = "Test Destruction"
		factory.context_uri = ""
		dajs = factory.toJSON(da)
		self.assertEqual(dajs, expect)

	def test_payment(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Payment/1'), ('type', 'Payment'), \
			('paid_to', 'http://lod.example.org/museum/Person/1')])
		p = extra.Payment('1')
		who = Person('1')
		p.paid_to = who
		pjs = factory.toJSON(p)
		self.assertEqual(pjs, expect)

	def test_add_schema(self):
		who = Person("1")
		self.assertRaises(DataError, who.__setattr__, 'exact_match', who)
		extra.add_schema_properties()
		who.exact_match = who
		self.assertEqual(who.exact_match, [who])

	def test_add_value(self):
		what = Dimension("1")
		self.assertRaises(DataError, what.__setattr__, 'value', 6)
		extra.add_rdf_value()
		what.value = 6
		self.assertEqual(what.value, 6)
