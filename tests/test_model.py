import unittest 
import sys
import os
import shutil

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import model

class TestFactorySetupDefaults(unittest.TestCase):

	def test_init_defaults(self):
		self.assertEqual(model.factory.base_url, 'http://lod.example.org/museum/')
		self.assertEqual(model.factory.debug_level, 'warn')
		self.assertEqual(model.factory.log_stream, sys.stderr)
		self.assertFalse(model.factory.materialize_inverses)
		self.assertFalse(model.factory.full_names)
		# Don't test orders, as these will change repeatedly

class TestFactorySetup(unittest.TestCase):

	def setUp(self):
		model.factory.base_url = 'http://data.getty.edu/provenance/'
		model.factory.base_dir = 'tests/provenance_base_dir'
		model.factory.default_lang = 'en'
		model.factory.context_uri = 'http://www.cidoc-crm.org/cidoc-crm/'

	def tearDown(self):
		model.factory.base_url = 'http://lod.example.org/museum/'
		model.factory.log_stream = sys.stderr
		model.factory.debug_level = 'warn'

	def test_base_url(self):
		self.assertEqual(model.factory.base_url, 'http://data.getty.edu/provenance/')

	def test_base_dir(self):
		self.assertEqual(model.factory.base_dir, 'tests/provenance_base_dir')

	def test_default_lang(self):
		self.assertEqual(model.factory.default_lang, 'en')

	def test_context_uri(self):
		self.assertEqual(model.factory.context_uri, 'http://www.cidoc-crm.org/cidoc-crm/')

	def test_set_debug_stream(self):
		strm = open('err_output', 'w')
		model.factory.set_debug_stream(strm)
		self.assertEqual(model.factory.log_stream, strm)

	def test_set_debug(self):
		model.factory.set_debug('error_on_warning')
		self.assertEqual(model.factory.debug_level, 'error_on_warning')
		self.assertRaises(model.ConfigurationError, model.factory.set_debug, 'xxx')

class TestFactorySerialization(unittest.TestCase):

	def setUp(self):
		self.collection = model.InformationObject('collection')

	def test_toJSON(self):
		expect = OrderedDict([('id', u'http://lod.example.org/museum/InformationObject/collection'), 
			('type', 'InformationObject')])
		outj = model.factory.toJSON(self.collection)
		self.assertEqual(expect, outj)

	def test_toString(self):
		expect = u'{"id":"http://lod.example.org/museum/InformationObject/collection","type":"InformationObject"}'
		outs = model.factory.toString(self.collection)
		self.assertEqual(expect, outs)

	def test_toFile(self):
		self.assertRaises(model.ConfigurationError, model.factory.toFile, self.collection)
		model.factory.base_dir = 'tests'
		model.factory.toFile(self.collection)
		self.assertTrue(os.path.isfile('tests/InformationObject/collection.json'))
		shutil.rmtree('tests/InformationObject')



class TestProcessTSV(unittest.TestCase):

	def test_process_tsv(self):
		expect = {u'subs': [u'E84_Information_Carrier'], u'label': u'Man-Made Object', u'className': u'ManMadeObject', 
		u'subOf': u'E19_Physical_Object|E24_Physical_Man-Made_Thing', u'props': [], u'class': None, 
		u'desc': u'This class comprises physical objects purposely created by human activity.\\nNo assumptions are made as to the extent of modification required to justify regarding an object as man-made. For example, an inscribed piece of rock or a preserved butterfly are both regarded as instances of E22 Man-Made Object.'}
		fn = 'cromulent/data/crm_vocab.tsv'
		vocabData = model.process_tsv(fn)
		man_made = vocabData['E22_Man-Made_Object']
		self.assertEqual(expect, man_made)

class TestBuildClasses(unittest.TestCase):

	def test_build_classes(self):
		tsv = "ClassName_full\tclass\tClassName_py\tClass Label\tClass Description\t\n"
		fh = open('tests/temp.tsv', 'w')
		fh.write(tsv)
		fh.close()
		model.build_classes("tests/temp.tsv", "ClassName_full")
		from cromulent.model import ClassName_py
		self.assertEqual('Class Description', ClassName_py._description)
		os.remove('tests/temp.tsv')

class TestBuildClass(unittest.TestCase):

	def test_build_class(self):
		tsv = "ClassName_full\tclass\tClassName_py2\tClass Label\tClass Description\t\n"
		fh = open('tests/temp.tsv', 'w')
		fh.write(tsv)
		fh.close()
		vocabData = model.process_tsv('tests/temp.tsv')
		model.build_class('ClassName_full', model.BaseResource, vocabData)
		from cromulent.model import ClassName_py2
		self.assertEqual('Class Description', ClassName_py2._description)
		os.remove('tests/temp.tsv')
		
class TestBaseResource(unittest.TestCase):

	def setUp(self):
		self.artist = model.Person('00001', 'Jane Doe')
		self.son = model.Person('00002', 'John Doe')

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
		self.assertEqual(model.Acquisition, cl)

	def test_check_reference(self):
		self.assertTrue(self.artist._check_reference('http'))
		self.assertFalse(self.artist._check_reference('xxx'))
		self.assertTrue(self.artist._check_reference({'id': 'xxx'}))
		self.assertFalse(self.artist._check_reference({'xxx': 'yyy'}))
		self.assertTrue(self.artist._check_reference(self.son))
		self.assertTrue(self.artist._check_reference(['http']))
		self.assertFalse(self.artist._check_reference(['xxx', 'yyy']))
		self.assertTrue(self.artist._check_reference(model.Person))

class TestMagicMethods(unittest.TestCase):

	def test_set_magic_lang(self):
		model.factory.default_lang = 'en'
		model.Person._lang_properties = ['label', 'description']
		artist = model.Person('00001', 'Jane Doe')
		self.assertEqual(artist.label, {'en': 'Jane Doe'})
		artist._set_magic_lang('label', 'Janey')
		self.assertEqual(artist.label, {'en': ['Jane Doe', 'Janey']})
		son = model.Person('00002', 'John Doe')
		self.assertRaises(model.DataError, artist._set_magic_lang, 'parent_of', son)

	def test_set_magic_resource(self):
		artist = model.Person('00001', 'Jane Doe')
		son = model.Person('00002', 'John Doe')
		daughter = model.Person('00002', 'Jenny Doe')
		son2 = model.Person('00002', 'Jim Doe')
		artist._set_magic_resource('parent_of', son)
		self.assertEqual(artist.parent_of, son)
		artist._set_magic_resource('parent_of', daughter)
		try:
			self.assertIn(son, artist.parent_of)
			self.assertIn(daughter, artist.parent_of)
		except:
			# 2.6 doesn't have assertIn
			self.assertTrue(son in artist.parent_of)
			self.assertTrue(daughter in artist.parent_of)

		artist._set_magic_resource('parent_of', son2)
		try:
			self.assertIn(son, artist.parent_of)
			self.assertIn(daughter, artist.parent_of)
			self.assertIn(son2, artist.parent_of)
		except:
			self.assertTrue(son in artist.parent_of)
			self.assertTrue(daughter in artist.parent_of)
			self.assertTrue(son2 in artist.parent_of)

	def test_set_magic_resource_inverse(self):
		model.factory.materialize_inverses = True
		artist = model.Person('00001', 'Jane Doe')
		son = model.Person('00002', 'John Doe')
		artist._set_magic_resource('parent_of', son)
		self.assertEqual(son.parent, artist)

	def test_validation_unknown(self):
		model.factory.validate_properties = True
		artist = model.Person('00001', 'Jane Doe')		
		self.assertRaises(model.DataError, artist.__setattr__, 'unknown_property', 1)

	def test_validation_wrong_type(self):
		model.factory.validate_properties = True
		artist = model.Person('00001', 'Jane Doe')	
		self.assertRaises(model.DataError, artist.__setattr__, 'parent_of', 'Bad Value')

	def test_validation_off(self):
		model.factory.validate_properties = False
		artist = model.Person('00001', 'Jane Doe')		
		artist.unknown_property = 1
		self.assertEqual(artist.unknown_property, 1)


if __name__ == '__main__':
	unittest.main()
