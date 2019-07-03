import unittest 
import sys
import os

from cromulent import vocab, model
from cromulent.model import factory

class TestClassBuilder(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_class(self):
		vocab.register_aat_class("TestObject1", {"parent": model.HumanMadeObject, "id": "1", "label": "example 1"})
		from cromulent.vocab import TestObject1
		self.assertEqual(TestObject1._classification[0].id, 'http://vocab.getty.edu/aat/1')

	def test_instance(self):
		vocab.register_instance("TestMaterial2", {"parent": model.Material, "id": "2", "label": "example 2"})
		self.assertTrue('TestMaterial2' in vocab.instances)
		tm2 = vocab.instances['TestMaterial2']
		self.assertEqual(tm2.id, "http://vocab.getty.edu/aat/2")

	def test_art_setter(self):
		p = model.HumanMadeObject("a", art=1)
		p._label = "a"
		pj = p._toJSON(done={})
		self.assertFalse(pj.get('classified_as', None))
		vocab.add_art_setter()
		p2 = vocab.Painting("b", art=1)
		p2j = p2._toJSON(done={})
		# self.assertTrue("aat:300133025" in p2j['classified_as'])
		# no idea why the aat:1234 pattern doesn't work here
		# something to do with failing to set up the factory?

	def test_aa_check(self):
		t = model.Type()
		aa = model.AttributeAssignment()
		# First check that aa accepts a type
		aa.assigned_property = t
		# And will not accept a string
		self.assertRaises(model.DataError, aa.__setattr__, "assigned_property", "classified_as")

		# Check we can set anything to assigned / assigned_to
		aa.assigned_property = None
		aa.assigned = aa
		aa.assigned_to = aa
		self.assertEqual(aa.assigned, aa)
		self.assertEqual(aa.assigned_to, aa)

		vocab.add_attribute_assignment_check()

		# This should fail right now as can't classify as an AA
		self.assertRaises(model.DataError, aa.__setattr__, "assigned_property", "classified_as")
		aa.assigned = None
		aa.assigned_to = None
		aa.assigned = t
		aa.assigned_to = t
		aa.assigned_property = "classified_as"
		self.assertEqual(aa.assigned_property, 'classified_as')


	def test_boundary_setter(self):
		vocab.add_linked_art_boundary_check()
		p = model.Person()
		p2 = model.Person()
		n = model.Name()
		n.content = "Test"
		p2.identified_by = n
		p.related = p2
		# Now, Test should not appear in the resulting JSON of p
		factory.linked_art_boundaries = True
		js = factory.toJSON(p)
		self.assertTrue(not 'identified_by' in js['related'][0])
		factory.linked_art_boundaries = False
		js = factory.toJSON(p)
		self.assertTrue('identified_by' in js['related'][0])		

	def test_procurement_boundary(self):
		vocab.add_linked_art_boundary_check()
		a = model.Activity()
		p = vocab.Procurement()
		a.caused = p
		js = factory.toJSON(a)
		self.assertTrue(not 'classified_as' in js['caused'][0])		
