import unittest 
import sys
import os
import shutil
from collections import OrderedDict

from crom import crom
from mock import create_autospec


class TestFactorySetupDefaults(unittest.TestCase):

	def test_init_defaults(self):
		self.assertEqual(crom.factory.base_url, 'http://lod.example.org/museum/')
		self.assertEqual(crom.factory.debug_level, 'warn')
		self.assertEqual(crom.factory.log_stream, sys.stderr)
		self.assertFalse(crom.factory.materialize_inverses)
		self.assertFalse(crom.factory.full_names)
		# Don't test orders, as these will change repeatedly

class TestFactorySetup(unittest.TestCase):

	def setUp(self):
		crom.factory.base_url = 'http://data.getty.edu/provenance/'
		crom.factory.base_dir = 'tests/provenance_base_dir'
		crom.factory.default_lang = 'en'
		crom.factory.context_uri = 'http://www.cidoc-crm.org/cidoc-crm/'

	def tearDown(self):
		crom.factory.base_url = 'http://lod.example.org/museum/'
		crom.factory.log_stream = sys.stderr
		crom.factory.debug_level = 'warn'

	def test_base_url(self):
		self.assertEqual(crom.factory.base_url, 'http://data.getty.edu/provenance/')

	def test_base_dir(self):
		self.assertEqual(crom.factory.base_dir, 'tests/provenance_base_dir')

	def test_default_lang(self):
		self.assertEqual(crom.factory.default_lang, 'en')

	def test_context_uri(self):
		self.assertEqual(crom.factory.context_uri, 'http://www.cidoc-crm.org/cidoc-crm/')

	def test_set_debug_stream(self):
		strm = open('err_output', 'w')
		crom.factory.set_debug_stream(strm)
		self.assertEqual(crom.factory.log_stream, strm)

	def test_set_debug(self):
		crom.factory.set_debug('error_on_warning')
		self.assertEqual(crom.factory.debug_level, 'error_on_warning')
		self.assertRaises(crom.ConfigurationError, crom.factory.set_debug, 'xxx')

class TestFactorySerialization(unittest.TestCase):

	def setUp(self):
		self.collection = crom.InformationObject('collection')

	def test_toJSON(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/InformationObject/collection'), 
			('type', 'InformationObject')])
		outj = crom.factory.toJSON(self.collection)
		self.assertEqual(expect, outj)

	def test_toString(self):
		expect = u'{"id":"http://lod.example.org/museum/InformationObject/collection","type":"InformationObject"}'
		outs = crom.factory.toString(self.collection)
		self.assertEqual(expect, outs)

	def test_toFile(self):
		self.assertRaises(crom.ConfigurationError, crom.factory.toFile, self.collection)
		crom.factory.base_dir = 'tests'
		crom.factory.toFile(self.collection)
		self.assertTrue(os.path.isfile('tests/InformationObject/collection.json'))
		shutil.rmtree('tests/InformationObject')

class TestProcessTSV(unittest.TestCase):

	def test_process_tsv(self):
		expect = {u'subs': [u'E84_Information_Carrier'], u'label': u'Man-Made Object', u'className': u'ManMadeObject', 
		u'subOf': u'E19_Physical_Object|E24_Physical_Man-Made_Thing', u'props': [], u'class': None, 
		u'desc': u'This class comprises physical objects purposely created by human activity.\\nNo assumptions are made as to the extent of modification required to justify regarding an object as man-made. For example, an inscribed piece of rock or a preserved butterfly are both regarded as instances of E22 Man-Made Object.'}
		fn = 'crom/data/crm_vocab.tsv'
		vocabData = crom.process_tsv(fn)
		man_made = vocabData['E22_Man-Made_Object']
		self.assertEqual(expect, man_made)

class TestBuildClasses(unittest.TestCase):

	def test_build_classes(self):
		mock_function = create_autospec(crom.build_classes)
		mock_function()
		mock_function.assert_called_with()

class TestBuildClass(unittest.TestCase):

	def test_build_class(self):
		fn = 'crom/data/crm_vocab.tsv'
		vocabData = crom.process_tsv(fn)
		mock_function = create_autospec(crom.build_class)
		mock_function('E22_Man-Made_Object', crom.PhysicalManMadeThing, vocabData)
		mock_function.assert_called_with('E22_Man-Made_Object', crom.PhysicalManMadeThing, vocabData)
		
class TestBaseResource(unittest.TestCase):

	def setUp(self):
		self.artist = crom.Person('00001', 'Jane Doe')
		self.son = crom.Person('00002', 'John Doe')

	def test_init(self):
		self.assertEqual(self.artist.id, 'http://lod.example.org/museum/Person/00001')
		self.assertEqual(self.artist.type, 'crm:E21_Person')
		self.assertEqual(self.artist.label, 'Jane Doe')
		self.assertFalse(hasattr(self.artist, 'value'))
		self.assertFalse(hasattr(self.artist, 'has_type'))

	def test_check_prop(self):
		desc = self.artist._check_prop('description', 'Jane Doe\'s Bio')
		self.assertEqual(desc, 1)
		parent = self.artist._check_prop('parent_of', self.son)
		self.assertEqual(parent, 2)
		birth = self.artist._check_prop('born', 1977)
		self.assertEqual(birth, 0)
		no_key = self.artist._check_prop('knew', 'Jen Smith')
		self.assertEqual(no_key, 0)

	def test_list_all_props(self):
		props = self.artist._list_all_props()
		(lbl, cl) = sorted(props.items())[0]
		self.assertEqual('acquired_title_through', lbl)
		self.assertEqual(crom.Acquisition, cl)

	def test_check_reference(self):
		self.assertTrue(self.artist._check_reference('http'))
		self.assertFalse(self.artist._check_reference('xxx'))
		self.assertTrue(self.artist._check_reference({'id': 'xxx'}))
		self.assertFalse(self.artist._check_reference({'xxx': 'yyy'}))
		self.assertTrue(self.artist._check_reference(self.son))
		self.assertTrue(self.artist._check_reference(['http']))
		self.assertFalse(self.artist._check_reference(['xxx', 'yyy']))
		self.assertTrue(self.artist._check_reference(crom.Person))

class TestMagicMethods(unittest.TestCase):

	def test_set_magic_lang(self):
		crom.factory.default_lang = 'en'
		crom.Person._lang_properties = ['label', 'description']
		artist = crom.Person('00001', 'Jane Doe')
		self.assertEqual(artist.label, {'en': 'Jane Doe'})
		artist._set_magic_lang('label', 'Janey')
		self.assertEqual(artist.label, {'en': ['Jane Doe', 'Janey']})
		son = crom.Person('00002', 'John Doe')
		self.assertRaises(crom.DataError, artist._set_magic_lang, 'parent_of', son)

	def test_set_magic_resource(self):
		artist = crom.Person('00001', 'Jane Doe')
		son = crom.Person('00002', 'John Doe')
		daughter = crom.Person('00002', 'Jenny Doe')
		son2 = crom.Person('00002', 'Jim Doe')
		artist._set_magic_resource('parent_of', son)
		self.assertEqual(artist.parent_of, son)
		artist._set_magic_resource('parent_of', daughter)
		self.assertIn(son, artist.parent_of)
		self.assertIn(daughter, artist.parent_of)
		artist._set_magic_resource('parent_of', son2)
		self.assertIn(son, artist.parent_of)
		self.assertIn(daughter, artist.parent_of)
		self.assertIn(son2, artist.parent_of)

	def test_set_magic_resource_inverse(self):
		crom.factory.materialize_inverses = True
		artist = crom.Person('00001', 'Jane Doe')
		son = crom.Person('00002', 'John Doe')
		artist._set_magic_resource('parent_of', son)
		self.assertEqual(son.parent, artist)





if __name__ == '__main__':
	unittest.main()
