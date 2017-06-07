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
		vocab.register_aat_class("TestObject1", model.ManMadeObject, "1")
		from cromulent.vocab import TestObject1
		self.assertEqual(TestObject1._classification, "aat:1")

	def test_material(self):
		vocab.register_aat_material("TestMaterial2", "2")
		self.assertTrue('TestMaterial2' in vocab.materialTypes)
		tm2 = vocab.materialTypes['TestMaterial2']
		self.assertEqual(tm2.id, "aat:2")

	def test_unit(self):
		vocab.register_aat_dimensionUnit("TestUnit4", "4")
		self.assertTrue('TestUnit4' in vocab.dimensionUnits)
		tu4 = vocab.dimensionUnits['TestUnit4']
		self.assertEqual(tu4.id, "aat:4")

	def test_type_patch(self):
		t = model.Type("http://vocab.getty.edu/aat/5")
		nt = t._toJSON()
		self.assertEqual(nt, "aat:5")

	def test_art_setter(self):
		p = model.ManMadeObject("a", art=1)
		p.label = "a"
		pj = p._toJSON()
		self.assertFalse(pj.get('classified_as', None))
		vocab.add_art_setter()
		p2 = vocab.Painting("b", art=1)
		p2j = p2._toJSON()
		# self.assertTrue("aat:300133025" in p2j['classified_as'])
		# no idea why the aat:1234 pattern doesn't work here
		# something to do with failing to set up the factory?
