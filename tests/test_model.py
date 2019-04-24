import unittest 
import sys
import os
import shutil
import json

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
		#model.factory.context_uri = 'http://www.cidoc-crm.org/cidoc-crm/'

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

	#def test_context_uri(self):
	#	self.assertEqual(model.factory.context_uri, 'http://www.cidoc-crm.org/cidoc-crm/')

	def test_set_debug_stream(self):
		strm = open('err_output', 'w')
		model.factory.set_debug_stream(strm)
		self.assertEqual(model.factory.log_stream, strm)

	def test_set_debug(self):
		model.factory.set_debug('error_on_warning')
		self.assertEqual(model.factory.debug_level, 'error_on_warning')
		self.assertRaises(model.ConfigurationError, model.factory.set_debug, 'xxx')
		self.assertRaises(model.MetadataError, model.factory.maybe_warn, "test")

	def test_load_context(self):
		self.assertRaises(model.ConfigurationError, model.factory.load_context, 
			"foo", {"foo":"does_not_exist.txt"})
		model.factory.load_context("foo", {"foo":"tests/test_context.json"})
		self.assertEqual(model.factory.context_json, {"@context":{"id":"@id"}})
		self.assertRaises(model.ConfigurationError, model.factory.load_context, "", {})

class TestFactorySerialization(unittest.TestCase):

	def setUp(self):
		self.collection = model.InformationObject('collection')
		self.collection._label = "Test Object"

	def test_broken_unicode(self):
		model.factory.debug_level = "error_on_warning"
		try:
			badval = b"\xFF\xFE\x02"
		except:
			badval = "\xFF\xFE\x02"
		badjs = {"_label": badval}
		self.assertRaises(model.MetadataError, model.factory._buildString,
			js=badjs)

	def test_toJSON(self):
		model.factory.context_uri = 'http://lod.getty.edu/context.json'
		expect = OrderedDict([
			('@context', model.factory.context_uri),
			('id', u'http://lod.example.org/museum/InformationObject/collection'), 
			('type', 'InformationObject'), ('_label', 'Test Object')])
		outj = model.factory.toJSON(self.collection)
		self.assertEqual(expect, outj)

	def test_toJSON_full(self):
		expect = OrderedDict([(u'@context', 'http://lod.getty.edu/context.json'), 
			(u'@id', u'http://lod.example.org/museum/Person/1'), (u'@type', u'crm:E21_Person'),
			('rdfs:label', 'Test Person')])
		model.factory.context_uri = 'http://lod.getty.edu/context.json'
		model.factory.full_names = True
		p = model.Person("1")
		p._label = "Test Person"
		outj = model.factory.toJSON(p)
		self.assertEqual(expect, outj)
		# reset
		model.factory.full_names = False
		model.factory.context_uri = ""

	def test_toString(self):
		expect = u'{"id":"http://lod.example.org/museum/InformationObject/collection","type":"InformationObject","_label":"Test Object"}'
		outs = model.factory.toString(self.collection)
		self.assertEqual(expect, outs)

	def test_toFile(self):
		self.assertRaises(model.ConfigurationError, model.factory.toFile, self.collection)
		# Test auto filename determination
		model.factory.base_dir = 'tests'
		model.factory.toFile(self.collection)
		self.assertTrue(os.path.isfile('tests/InformationObject/collection.json'))
		# Test explicit filename setting
		model.factory.toFile(self.collection, filename='tests/fishbat.bar')
		self.assertTrue(os.path.isfile('tests/fishbat.bar'))
		# Tidy up
		shutil.rmtree('tests/InformationObject')

	def test_breadth(self):
		x = model.TransferOfCustody()
		e = model.Activity()
		fr = model.Group()
		to = model.Group()
		w = model.ManMadeObject()
		fr._label = "From"
		to._label = "To"
		x.transferred_custody_of = w
		x.transferred_custody_from = fr
		x.transferred_custody_to = to
		e.used_specific_object = w
		e.carried_out_by = to
		w.current_owner = fr
		x.specific_purpose = e
		js = model.factory.toJSON(x)
		# Okay ... if we're breadth first, then custody_from is a resource
		# And now it's the first in the list
		self.assertTrue(isinstance(js['transferred_custody_from'][0], OrderedDict))

	def test_string_list(self):
		x = model.Activity()
		x._label = ["Label 1", "Label 2"]
		js = model.factory.toJSON(x)
		self.assertTrue(js['_label'] == x._label)

	def test_external(self):
		x = model.ExternalResource(ident="1")
		model.factory.elasticsearch_compatible = 1
		js = x._toJSON(done=None)
		self.assertTrue(type(js) == dict)
		model.factory.elasticsearch_compatible = 0
		js = x._toJSON(done=None)
		# testing unicode in 2, str in 3 :(
		self.assertTrue(type(js) != dict)		

	def test_recursion(self):
		x = model.Activity()
		x.part = x
		js = model.factory.toJSON(x)
		# If our recursion checks have regressed, this will barf right here
		self.assertTrue(1)


class TestProcessTSV(unittest.TestCase):

	def test_process_tsv(self):
		expect = {u'subs': [u'E84_Information_Carrier'], u'label': u'Man-Made Object', u'className': u'ManMadeObject', 
		u'subOf': u'E19_Physical_Object|E24_Physical_Man-Made_Thing', u'props': [], u'class': None, u'okay': u'1'}
		fn = 'cromulent/data/crm_vocab.tsv'
		vocabData = model.process_tsv(fn)
		man_made = vocabData['E22_Man-Made_Object']
		del man_made['desc']  # too long and volatile
		try:
			self.assertEqual(expect, man_made)
		except:
			expect[u'subs'] = []
			self.assertEqual(expect, man_made)

class TestBuildClasses(unittest.TestCase):

	def test_build_classes(self):
		tsv = "\nClassName_full\tclass\tClassName_py\tClass Label\tClass Description\t\t1\t\n"
		fh = open('tests/temp.tsv', 'w')
		fh.write(tsv)
		fh.close()
		model.build_classes("tests/temp.tsv", "ClassName_full")
		from cromulent.model import ClassName_py
		self.assertEqual('Class Description', ClassName_py.__doc__)
		os.remove('tests/temp.tsv')

class TestBuildClass(unittest.TestCase):

	def test_build_class(self):
		tsv = "\nClassName_full\tclass\tClassName_py2\tClass Label\tClass Description\t\t1\t\n"
		fh = open('tests/temp.tsv', 'w')
		fh.write(tsv)
		fh.close()
		vocabData = model.process_tsv('tests/temp.tsv')
		model.build_class('ClassName_full', model.BaseResource, vocabData)
		from cromulent.model import ClassName_py2
		self.assertEqual('Class Description', ClassName_py2.__doc__)
		os.remove('tests/temp.tsv')

class TestAutoIdentifiers(unittest.TestCase):

	def test_bad_autoid(self):
		model.factory.auto_id_type = "broken"
		self.assertRaises(model.ConfigurationError, model.factory.generate_id,
			"irrelevant")

	def test_int(self):
		model.factory.auto_id_type = "int"
		p = model.Person()
		p2 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)

	def test_int_per_type(self):
		model.factory.auto_id_type = "int-per-type"
		p = model.Person()
		p2 = model.Person()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)
		p3 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p3.id[-1]))		

	def test_int_per_segment(self):
		model.factory._auto_id_segments = {}
		model.factory.auto_id_type = "int-per-segment"
		model.Activity._uri_segment = model.Person._uri_segment
		p = model.Person()
		p2 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)		
		p3 = model.TimeSpan()
		self.assertEqual(int(p.id[-1]), int(p3.id[-1]))		
			
	def test_uuid(self):
		model.factory.auto_id_type = "uuid"
		p = model.Person()
		self.assertTrue(p.id.startswith('urn:uuid:'))		

	def test_prefixes(self):

		model.factory.prefixes = {'fish':'http://example.org/ns/'}
		p3 = model.Person('fish:3')
		self.assertEqual(p3.id, 'fish:3')
		self.assertEqual(p3._full_id, 'http://example.org/ns/3')

		model.factory.prefixes = {}
		p4 = model.Person('fish:4')
		self.assertTrue(p4.id.startswith(model.factory.base_url))

		
class TestBaseResource(unittest.TestCase):

	def setUp(self):
		self.artist = model.Person('00001', 'Jane Doe')
		self.son = model.Person('00002', 'John Doe')
		model.Person._properties['parent_of']['okayToUse'] = 1

	def test_init(self):
		self.assertEqual(self.artist.id, 'http://lod.example.org/museum/Person/00001')
		self.assertEqual(self.artist.type, 'crm:E21_Person')
		self.assertEqual(self.artist._label, 'Jane Doe')
		self.assertFalse(hasattr(self.artist, 'value'))
		self.assertFalse(hasattr(self.artist, 'has_type'))

	def test_check_prop(self):
		desc = self.artist._check_prop('_label', 'Jane Doe\'s Bio')
		self.assertEqual(desc, 1)
		parent = self.artist._check_prop('parent_of', self.son)
		self.assertEqual(parent, 2)

	def test_list_all_props(self):
		props = list(self.artist._list_all_props().items())
		props.sort()
		if props[0][0] == "_label":
			props = props[1:]
		(lbl, cl) = props[0]
		self.assertEqual('acquired_custody_through', lbl)
		self.assertEqual(model.TransferOfCustody, cl)

	def test_check_reference(self):
		self.assertTrue(self.artist._check_reference('http'))
		self.assertFalse(self.artist._check_reference('xxx'))
		self.assertTrue(self.artist._check_reference({'id': 'xxx'}))
		self.assertFalse(self.artist._check_reference({'xxx': 'yyy'}))
		self.assertTrue(self.artist._check_reference(self.son))
		self.assertTrue(self.artist._check_reference(['http']))
		self.assertFalse(self.artist._check_reference(['xxx', 'yyy']))
		self.assertTrue(self.artist._check_reference(model.Person))

	def test_multiplicity(self):
		model.factory.process_multiplicity = 1
		who = model.Actor()
		mmo = model.ManMadeObject()
		who.current_owner_of = mmo
		mmo.current_owner = who
		self.assertEqual(mmo.current_owner, who)
		self.assertEqual(who.current_owner_of, [mmo])		


class TestMagicMethods(unittest.TestCase):

	def setUp(self):
		model.Person._properties['parent_of']['okayToUse'] = 1
		model.Person._lang_properties = ['label', 'description']

	# Commented out as we don't actually use magic_lang ever
	# It's always a LinguisticObject with .language Type

	# def test_set_magic_lang(self):
	# 	model.factory.default_lang = 'en'
	# 	artist = model.LinguisticObject('00001', value='Jane Doe')
	# 	self.assertEqual(artist.content, {'en': 'Jane Doe'})
	# 	artist._set_magic_lang('content', 'Janey')
	# 	self.assertEqual(artist.content, {'en': ['Jane Doe', 'Janey']})
	# 	son = model.Person('00002', 'John Doe')
	# 	self.assertRaises(model.DataError, artist._set_magic_lang, 'parent_of', son)

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
