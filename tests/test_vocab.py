import unittest 
import sys
import os

from cromulent import vocab, model

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
