import unittest 
import sys
import os
import shutil
import json
import pickle
from collections import OrderedDict
from cromulent import model
from cromulent.model import override_okay


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

	def test_pickle(self):
		model.factory.log_stream = sys.stderr
		srlz = pickle.dumps(model.factory)
		newfac = pickle.loads(srlz)
		self.assertTrue(model.factory.log_stream is newfac.log_stream)



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
		w = model.HumanMadeObject()
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

	def test_pipe_scoped(self):
		x = model.Activity()
		y = model.Activity()
		x.part = y
		model.factory.pipe_scoped_contexts = True
		js = model.factory.toJSON(x)
		self.assertTrue('part|crm:P9_consists_of' in js)
		model.factory.pipe_scoped_contexts = False
		js = model.factory.toJSON(x)		
		self.assertTrue('part|crm:P9_consists_of' not in js)		
		self.assertTrue('part' in js)

	def test_collapse_json(self):
		p = model.Person()
		p.classified_as = model.Type(ident="http://example.org/Type", label="Test")
		res1 = model.factory.toString(p, compact=False, collapse=60) # all new lines
		res2 = model.factory.toString(p, compact=False, collapse=120) # compact list of type
		self.assertEqual(len(res1.splitlines()), 12)
		self.assertEqual(len(res2.splitlines()), 6)


class TestProcessTSV(unittest.TestCase):

	def test_process_tsv(self):
		expect = {u'subs': [u'E84_Information_Carrier'], u'label': u'Human-Made Object', u'className': u'HumanMadeObject', 
		u'subOf': u'E19_Physical_Object|E24_Physical_Human-Made_Thing', u'props': [], u'class': None, u'okay': u'1'}
		fn = 'cromulent/data/crm_vocab.tsv'
		vocabData = model.process_tsv(fn)
		man_made = vocabData['E22_Human-Made_Object']
		del man_made['desc']  # too long and volatile
		# check subs specifically - could be coming from an extension
		if man_made['subs'] != expect['subs']:
			del man_made['subs']
			del expect['subs']
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
		model.factory.auto_assign_id = True
		model.factory.auto_id_type = "broken"
		self.assertRaises(model.ConfigurationError, model.factory.generate_id,
			"irrelevant")

	def test_int(self):
		model.factory.auto_assign_id = True
		model.factory.auto_id_type = "int"
		p = model.Person()
		p2 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)

	def test_int_per_type(self):
		model.factory.auto_assign_id = True
		model.factory.auto_id_type = "int-per-type"
		p = model.Person()
		p2 = model.Person()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)
		p3 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p3.id[-1]))		

	def test_int_per_segment(self):
		model.factory.auto_assign_id = True
		model.factory._auto_id_segments = {}
		model.factory.auto_id_type = "int-per-segment"
		model.Activity._uri_segment = model.Person._uri_segment
		p = model.Person()
		p2 = model.Activity()
		self.assertEqual(int(p.id[-1]), int(p2.id[-1])-1)		
		p3 = model.TimeSpan()
		self.assertEqual(int(p.id[-1]), int(p3.id[-1]))		
			
	def test_uuid(self):
		model.factory.auto_assign_id = True
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

	def test_other_uris(self):
		p1 = model.Person(ident="tag:some-info-about-person")
		self.assertEqual(p1.id, "tag:some-info-about-person")
		p2 = model.Person(ident="info:ulan/500012345")
		self.assertEqual(p2.id, "info:ulan/500012345")
		p3 = model.Person(ident="some:random:thing:with:colons")
		self.assertFalse(p3.id == "some:random:thing:with:colons")

	def test_no_ident(self):

		model.factory.auto_assign_id = True
		p1 = model.Person()	# auto assigned	 
		p2 = model.Person(ident=None) # auto assigned
		p3 = model.Person(ident="") # bnode explicitly

		self.assertTrue(p1.id.startswith('http'))
		self.assertTrue(p2.id.startswith('http'))
		self.assertEqual(p3.id, '')

		model.factory.auto_assign_id = False
		p4 = model.Person() # bnode is default
		p5 = model.Person(ident=None) # bnode is default
		p6 = model.Person(ident="") # bnode explicitly

		self.assertEqual(p4.id, '')
		self.assertEqual(p5.id, '')
		self.assertEqual(p6.id, '')

		
class TestBaseResource(unittest.TestCase):

	def setUp(self):
		override_okay(model.Person, 'parent_of')
		self.artist = model.Person('00001', 'Jane Doe')
		self.son = model.Person('00002', 'John Doe')

	def test_init(self):
		self.assertEqual(self.artist.id, 'http://lod.example.org/museum/Person/00001')
		self.assertEqual(self.artist._type, 'crm:E21_Person')
		self.assertEqual(self.artist.type, 'Person')
		self.assertEqual(self.artist._label, 'Jane Doe')
		self.assertFalse(hasattr(self.artist, 'value'))
		self.assertFalse(hasattr(self.artist, 'has_type'))

	def test_check_prop(self):
		desc = self.artist._check_prop('_label', 'Jane Doe\'s Bio')
		self.assertEqual(desc, 1)
		parent = self.artist._check_prop('parent_of', self.son)
		self.assertEqual(parent, 2)

	def test_list_all_props(self):
		props = self.artist.list_all_props()
		props.sort()
		self.assertEqual(props[-1], 'witnessed')
		self.assertTrue('_label' in props)
		self.assertTrue('identified_by' in props)

	def test_list_my_props(self):
		p1 = model.Person()
		p1.classified_as = model.Type()
		props = p1.list_my_props()
		self.assertEqual(set(props), set(['classified_as', 'id']))
		props = p1.list_my_props(filter=model.Type)
		self.assertEqual(props, ['classified_as'])

	def test_allows_multiple(self):
		p = model.Person()
		self.assertTrue(p.allows_multiple('classified_as'))
		self.assertFalse(p.allows_multiple('born'))
		self.assertRaises(model.DataError, p.allows_multiple, 'fish')

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
		model.factory.process_multiplicity = True
		who = model.Actor()
		mmo = model.HumanMadeObject()
		prod = model.Production()
		mmo.produced_by = prod
		who.current_owner_of = mmo
		mmo.current_owner = who
		self.assertEqual(mmo.current_owner, [who])
		self.assertEqual(who.current_owner_of, [mmo])		
		self.assertEqual(mmo.produced_by, prod)

	def test_init_params(self):
		p1 = model.Person(ident="urn:uuid:1234")
		self.assertEqual(p1.id, "urn:uuid:1234")
		p2 = model.Person(ident="http://schema.org/Foo")
		self.assertEqual(p2.id, "schema:Foo")
		p3 = model.Name(content="Test")
		self.assertEqual(p3.content, "Test")

	def test_dir(self):
		props = dir(self.artist)
		self.assertTrue('identified_by' in props)


class TestPropertyCache(unittest.TestCase):

	def test_cache_hierarchy(self):
		o = model.HumanMadeObject()
		self.assertEqual(o._all_properties, {})
		model.cache_hierarchy()
		self.assertTrue(len(o._all_properties) > 50)
		

class TestMagicMethods(unittest.TestCase):

	def setUp(self):
		override_okay(model.Person, 'parent_of')
		# model.Person._properties['parent_of']['multiple'] = 1

	def test_set_magic_resource(self):
		artist = model.Person('00001', 'Jane Doe')
		son = model.Person('00002', 'John Doe')
		daughter = model.Person('00002', 'Jenny Doe')
		son2 = model.Person('00002', 'Jim Doe')
		artist._set_magic_resource('parent_of', son)
		self.assertEqual(artist.parent_of, [son])
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
		self.assertEqual(son.parent, [artist])
		model.factory.materialize_inverses = False

	def test_validate_profile_off(self):
		model.factory.validate_profile = False
		ia = model.IdentifierAssignment()
		# If it's not turned off this should raise
		model.factory.validate_profile = True
		self.assertRaises(model.ProfileError, model.IdentifierAssignment)		
		p1 = model.Person()
		self.assertRaises(model.ProfileError, p1.__setattr__, 'documented_in', "foo")

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
		model.factory.validate_properties = True

	def test_validate_multiplicity(self):
		model.factory.validate_multiplicity = True
		who = model.Person()
		b1 = model.Birth()
		who.born = b1
		b2 = model.Birth()
		self.assertRaises(model.ProfileError, who.__setattr__, 'born', b2)
		model.factory.validate_multiplicity = False
		who.born = b2
		self.assertEqual(who.born, [b1, b2])


if __name__ == '__main__':
	unittest.main()
