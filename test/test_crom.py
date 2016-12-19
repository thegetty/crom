import unittest 
import sys
import os
import shutil
from collections import OrderedDict

from crmpy import cidoc_orm
from mock import create_autospec



class TestFactorySetupDefaults(unittest.TestCase):

	def test_init_defaults(self):
		self.assertEqual(cidoc_orm.factory.base_url, 'http://lod.example.org/museum/')
		self.assertEqual(cidoc_orm.factory.debug_level, 'warn')
		self.assertEqual(cidoc_orm.factory.log_stream, sys.stderr)
		self.assertFalse(cidoc_orm.factory.materialize_inverses)
		self.assertFalse(cidoc_orm.factory.full_names)
		self.assertEqual(cidoc_orm.factory.key_order_hash, {"@context": 0, "id": 1, "type": 2, "has_type": 3, 
			"label": 4, "value": 4, "has_note": 5, "description": 5, "is_identified_by": 10 })
		self.assertEqual(cidoc_orm.factory.full_key_order_hash, {"@context": 0, "@id": 1, "rdf:type": 2, 
			"rdfs:label": 4, "rdf:value": 4, 
			"dc:description": 5,
			"crm:P1_is_identified_by": 10,
			"crm:P2_has_type": 3,
			"crm:P3_has_note": 4,
			"crm:P12i_was_present_at": 40,
			"schema:genre": 8,
			"crm:P45_consists_of": 14,
			"crm:P108i_was_produced_by": 20,
			"crm:P52_has_current_owner": 21,
			"crm:P55_has_current_location": 22,
			"crm:P104_is_subject_to": 30
		})

class TestFactorySetup(unittest.TestCase):

	def setUp(self):
		cidoc_orm.factory.base_url = 'http://data.getty.edu/provenance/'
		cidoc_orm.factory.base_dir = 'test/provenance_base_dir'
		cidoc_orm.factory.default_lang = 'en'
		cidoc_orm.factory.context_uri = 'http://www.cidoc-crm.org/cidoc-crm/'

	def tearDown(self):
		cidoc_orm.factory.base_url = 'http://lod.example.org/museum/'
		cidoc_orm.factory.log_stream = sys.stderr
		cidoc_orm.factory.debug_level = 'warn'

	def test_base_url(self):
		self.assertEqual(cidoc_orm.factory.base_url, 'http://data.getty.edu/provenance/')

	def test_base_dir(self):
		self.assertEqual(cidoc_orm.factory.base_dir, 'test/provenance_base_dir')

	def test_default_lang(self):
		self.assertEqual(cidoc_orm.factory.default_lang, 'en')

	def test_context_uri(self):
		self.assertEqual(cidoc_orm.factory.context_uri, 'http://www.cidoc-crm.org/cidoc-crm/')

	def test_set_debug_stream(self):
		strm = open('err_output', 'w')
		cidoc_orm.factory.set_debug_stream(strm)
		self.assertEqual(cidoc_orm.factory.log_stream, strm)

	def test_set_debug(self):
		cidoc_orm.factory.set_debug('error_on_warning')
		self.assertEqual(cidoc_orm.factory.debug_level, 'error_on_warning')
		self.assertRaises(cidoc_orm.ConfigurationError, cidoc_orm.factory.set_debug, 'xxx')

class TestFactorySerialization(unittest.TestCase):

	def setUp(self):
		self.collection = cidoc_orm.InformationObject('collection')

	def test_toJSON(self):
		expect = OrderedDict([(u'@context', u''), ('id', u'http://lod.example.org/museum/InformationObject/collection'), 
			('type', 'InformationObject')])
		outj = cidoc_orm.factory.toJSON(self.collection)
		self.assertEqual(expect, outj)

	def test_toString(self):
		expect = u'{"@context":"","id":"http://lod.example.org/museum/InformationObject/collection","type":"InformationObject"}'
		outs = cidoc_orm.factory.toString(self.collection)
		self.assertEqual(expect, outs)

	def test_toFile(self):
		self.assertRaises(cidoc_orm.ConfigurationError, cidoc_orm.factory.toFile, self.collection)
		cidoc_orm.factory.base_dir = 'test'
		cidoc_orm.factory.toFile(self.collection)
		self.assertTrue(os.path.isfile('test/InformationObject/collection'))
		shutil.rmtree('test/InformationObject')

class TestProcessTSV(unittest.TestCase):

	def test_process_tsv(self):
		expect = {u'subs': [u'E84_Information_Carrier'], u'label': u'Man-Made Object', u'className': u'ManMadeObject', 
		u'subOf': u'E19_Physical_Object|E24_Physical_Man-Made_Thing', u'props': [], u'class': None, 
		u'desc': u'This class comprises physical objects purposely created by human activity.\\nNo assumptions are made as to the extent of modification required to justify regarding an object as man-made. For example, an inscribed piece of rock or a preserved butterfly are both regarded as instances of E22 Man-Made Object.'}
		vocabData = cidoc_orm.process_tsv()
		man_made = vocabData['E22_Man-Made_Object']
		self.assertEqual(expect, man_made)

class TestBuildClasses(unittest.TestCase):

	def test_build_classes(self):
		mock_function = create_autospec(cidoc_orm.build_classes)
		mock_function()
		mock_function.assert_called_with()

class TestBuildClass(unittest.TestCase):

	def test_build_class(self):
		vocabData = cidoc_orm.process_tsv()
		mock_function = create_autospec(cidoc_orm.build_class)
		mock_function('E22_Man-Made_Object', cidoc_orm.PhysicalManMadeThing, vocabData)
		mock_function.assert_called_with('E22_Man-Made_Object', cidoc_orm.PhysicalManMadeThing, vocabData)
		
class TestBaseResource(unittest.TestCase):

	def setUp(self):
		self.artist = cidoc_orm.Person('00001', 'Jane Doe')
		self.son = cidoc_orm.Person('00002', 'John Doe')

	def test_init(self):
		self.assertEqual(self.artist.id, 'http://lod.example.org/museum/Person/00001')
		self.assertEqual(self.artist.type, 'crm:E21_Person')
		self.assertEqual(self.artist.label, 'Jane Doe')
		self.assertFalse(hasattr(self.artist, 'value'))
		self.assertFalse(hasattr(self.artist, 'has_type'))

	def test_check_prop(self):
		desc = self.artist._check_prop('description', 'Jane Doe\'s Bio')
		self.assertEqual(desc, 1)
		parent = self.artist._check_prop('is_parent_of', self.son)
		self.assertEqual(parent, 2)
		birth = self.artist._check_prop('was_born', 1977)
		self.assertEqual(birth, 0)
		no_key = self.artist._check_prop('knew', 'Jen Smith')
		self.assertEqual(no_key, 0)

	def test_list_all_props(self):
		expect = {u'left_by': cidoc_orm.Leaving, u'was_removed_by': cidoc_orm.PartRemoval, 
		u'has_current_location': cidoc_orm.Place, u'has_dimension': cidoc_orm.Dimension, 
		u'right_held_by': cidoc_orm.Actor, u'volume_overlaps_with': cidoc_orm.SpacetimeVolume, 
		u'actor_is_identified_by': cidoc_orm.ActorAppellation, u'moved_by': cidoc_orm.Move, 
		u'is_referred_to_by': cidoc_orm.PropositionalObject, u'is_parent_of': cidoc_orm.Person, 
		u'has_representation': cidoc_orm.VisualItem, u'motivated': cidoc_orm.Activity, 
		u'has_note': str, u'falls_within': cidoc_orm.SpacetimeVolume, 
		u'surrendered_title_through': cidoc_orm.Acquisition, u'has_contact_point': cidoc_orm.ContactPoint, 
		u'has_right_on': cidoc_orm.LegalObject, u'provides_reference_space_for': cidoc_orm.Place, 
		u'supported_type_creation': cidoc_orm.TypeCreation, u'defines_place': cidoc_orm.Place, 
		u'is_documented_in': cidoc_orm.Document, u'was_assessed_by': cidoc_orm.ConditionAssessment, 
		u'has_parent': cidoc_orm.Person, u'was_assigned_by': cidoc_orm.AttributeAssignment, 
		u'witnessed': cidoc_orm.Period, u'surrendered_custody_through': cidoc_orm.TransferOfCustody, 
		u'participated_in': cidoc_orm.Event, u'is_subject_to': cidoc_orm.Right, u'label': str, 
		u'shows_features_of': cidoc_orm.Thing, u'has_former_or_current_keeper': cidoc_orm.Actor, 
		u'was_father_for': cidoc_orm.Birth, u'has_spatial_projection': cidoc_orm.Place, 
		u'received_custody_through': cidoc_orm.TransferOfCustody, u'was_taken_out_of_existence_by': cidoc_orm.EndOfExistence, 
		u'has_former_or_current_owner': cidoc_orm.Actor, u'is_separated_from': cidoc_orm.SpacetimeVolume, 
		u'was_joined_by': cidoc_orm.Joining, u'died_in': cidoc_orm.Death, 
		u'was_transformed_by': cidoc_orm.Transformation, u'exemplifies': cidoc_orm.Type, 
		u'is_current_keeper_of': cidoc_orm.PhysicalThing, u'bears_feature': cidoc_orm.PhysicalFeature, 
		u'is_composed_of': cidoc_orm.PhysicalThing, u'was_used_for': cidoc_orm.Activity, 
		u'has_former_or_current_location': cidoc_orm.Place, u'is_identified_by': cidoc_orm.Appellation, 
		u'made_of': cidoc_orm.Material, u'is_current_owner_of': cidoc_orm.PhysicalThing, 
		u'is_former_or_current_keeper_of': cidoc_orm.PhysicalThing, u'has_number_of_parts': str, 
		u'physically_part_of': cidoc_orm.PhysicalThing, u'contains': cidoc_orm.SpacetimeVolume, 
		u'type': str, u'is_depicted_by': cidoc_orm.PhysicalManMadeThing, u'was_present_at': cidoc_orm.Event, 
		u'acquired_title_through': cidoc_orm.Acquisition, u'was_classified_by': cidoc_orm.TypeAssignment, 
		u'was_destroyed_by': cidoc_orm.Destruction, u'has_section_definition': cidoc_orm.SectionDefinition, 
		u'has_temporal_projection': cidoc_orm.TimeSpan, u'was_brought_into_existence_by': cidoc_orm.BeginningOfExistence, 
		u'changed_ownership_through': cidoc_orm.Acquisition, u'is_former_or_current_owner_of': cidoc_orm.PhysicalThing, 
		u'was_born': cidoc_orm.Birth, u'is_current_or_former_curator_of': cidoc_orm.Collection, 
		u'has_preferred_identifier': cidoc_orm.Identifier, u'has_current_keeper': cidoc_orm.Actor, 
		u'occupies': cidoc_orm.Place, u'has_section': cidoc_orm.Place, u'performed': cidoc_orm.Activity, 
		u'is_listed_in': cidoc_orm.AuthorityDocument, u'id': str, u'has_current_owner': cidoc_orm.Actor, 
		u'influenced': cidoc_orm.Activity, u'has_current_permanent_location': cidoc_orm.Place, 
		u'had_as_general_use': cidoc_orm.Type, u'gave_birth': cidoc_orm.Birth, u'carries': cidoc_orm.SymbolicObject, 
		u'was_measured_by': cidoc_orm.Measurement, u'is_subject_of': cidoc_orm.PropositionalObject, 
		u'was_attributed_by': cidoc_orm.AttributeAssignment, u'was_added_by': cidoc_orm.PartAddition, 
		u'description': str, u'has_condition': cidoc_orm.ConditionState, 
		u'custody_transferred_through': cidoc_orm.TransferOfCustody, u'is_current_or_former_member_of': cidoc_orm.Group, 
		u'resulted_from': cidoc_orm.Transformation, u'has_type': cidoc_orm.Type, 
		u'features_are_also_found_on': cidoc_orm.Thing, u'had_presence': cidoc_orm.Presence, 
		u'has_current_or_former_residence': cidoc_orm.Place, u'possesses': cidoc_orm.Right}
		props = self.artist._list_all_props()
		self.assertEqual(expect, props)

	def test_check_reference(self):
		self.assertTrue(self.artist._check_reference('http'))
		self.assertFalse(self.artist._check_reference('xxx'))
		self.assertTrue(self.artist._check_reference({'id': 'xxx'}))
		self.assertFalse(self.artist._check_reference({'xxx': 'yyy'}))
		self.assertTrue(self.artist._check_reference(self.son))
		self.assertTrue(self.artist._check_reference(['http']))
		self.assertFalse(self.artist._check_reference(['xxx', 'yyy']))
		self.assertTrue(self.artist._check_reference(cidoc_orm.Person))

class TestMagicMethods(unittest.TestCase):

	def test_set_magic_lang(self):
		cidoc_orm.factory.default_lang = 'en'
		cidoc_orm.Person._lang_properties = ['label', 'description']
		artist = cidoc_orm.Person('00001', 'Jane Doe')
		self.assertEqual(artist.label, {'en': 'Jane Doe'})
		artist._set_magic_lang('label', 'Janey')
		self.assertEqual(artist.label, {'en': ['Jane Doe', 'Janey']})
		son = cidoc_orm.Person('00002', 'John Doe')
		self.assertRaises(cidoc_orm.DataError, artist._set_magic_lang, 'is_parent_of', son)

	def test_set_magic_resource(self):
		artist = cidoc_orm.Person('00001', 'Jane Doe')
		son = cidoc_orm.Person('00002', 'John Doe')
		daughter = cidoc_orm.Person('00002', 'Jenny Doe')
		son2 = cidoc_orm.Person('00002', 'Jim Doe')
		artist._set_magic_resource('is_parent_of', son)
		self.assertEqual(artist.is_parent_of, son)
		artist._set_magic_resource('is_parent_of', daughter)
		self.assertIn(son, artist.is_parent_of)
		self.assertIn(daughter, artist.is_parent_of)
		artist._set_magic_resource('is_parent_of', son2)
		self.assertIn(son, artist.is_parent_of)
		self.assertIn(daughter, artist.is_parent_of)
		self.assertIn(son2, artist.is_parent_of)

	def test_set_magic_resource_inverse(self):
		cidoc_orm.factory.materialize_inverses = True
		artist = cidoc_orm.Person('00001', 'Jane Doe')
		son = cidoc_orm.Person('00002', 'John Doe')
		artist._set_magic_resource('is_parent_of', son)
		self.assertEqual(son.has_parent, artist)





if __name__ == '__main__':
	unittest.main()
