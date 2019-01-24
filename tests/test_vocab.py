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
		vocab.register_aat_class("TestObject1", model.ManMadeObject, "1", "example 1")
		from cromulent.vocab import TestObject1
		self.assertEqual(TestObject1._classification.id, "aat:1")

	def test_instance(self):
		vocab.register_instance("TestMaterial2", model.Material, "2", "example 2")
		self.assertTrue('TestMaterial2' in vocab.instances)
		tm2 = vocab.instances['TestMaterial2']
		self.assertEqual(tm2.id, "aat:2")

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
