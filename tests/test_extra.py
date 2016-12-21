
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import extra
from cromulent.model import factory, Person


class TestExtraClasses(unittest.TestCase):

	def test_destruction(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Activity/1'), ('type', ['Destruction', 'Activity'])])
		da = extra.DestructionActivity("1")
		dajs = factory.toJSON(da)
		self.assertEqual(dajs, expect)

	def test_payment(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/Payment/1'), ('type', 'Payment'), \
			('paid_to', OrderedDict([('id', u'http://lod.example.org/museum/Person/1'), ('type', 'Person')]))])
		p = extra.Payment('1')
		who = Person('1')
		p.paid_to = who
		pjs = factory.toJSON(p)
		self.assertEqual(pjs, expect)
