import unittest 
import sys
import os

from crom import vocab_mapping
from crom import crom

class TestClassBuilder(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_class(self):
		vocab_mapping.register_aat_class("TestObject1", crom.ManMadeObject, "1")
		from crom.vocab_mapping import TestObject1
		self.assertEqual(TestObject1._classification, "http://vocab.getty.edu/aat/1")

	def test_material(self):
		vocab_mapping.register_aat_material("TestMaterial2", "2")
		self.assertTrue('TestMaterial2' in vocab_mapping.materialTypes)
		tm2 = vocab_mapping.materialTypes['TestMaterial2']
		self.assertEqual(tm2.id, "http://vocab.getty.edu/aat/2")

	def test_dimension(self):
		vocab_mapping.register_aat_dimensionType("TestDimension3", "3")
		self.assertTrue('TestDimension3' in vocab_mapping.dimensionTypes)
		td3 = vocab_mapping.dimensionTypes['TestDimension3']
		self.assertEqual(td3.id, "http://vocab.getty.edu/aat/3")

	def test_unit(self):
		vocab_mapping.register_aat_dimensionUnit("TestUnit4", "4")
		self.assertTrue('TestUnit4' in vocab_mapping.dimensionUnits)
		tu4 = vocab_mapping.dimensionUnits['TestUnit4']
		self.assertEqual(tu4.id, "http://vocab.getty.edu/aat/4")

	def test_type_patch(self):
		t = crom.Type("http://vocab.getty.edu/aat/5")
		nt = t._toJSON()
		self.assertEqual(nt, "aat:5")
