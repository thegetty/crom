
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import reader
from cromulent.model import factory, Person, DataError, BaseResource, \
	Dimension, override_okay, AttributeAssignment

from cromulent import vocab

class TestReader(unittest.TestCase):

	def setUp(self):
		self.reader = reader.Reader()
		# ensure we can use parent_of
		override_okay(Person, 'parent_of')
		# Person._properties['parent_of']['multiple'] = 1

	def test_read(self):
		self.assertRaises(DataError, self.reader.read, "")
		self.assertRaises(DataError, self.reader.read, "This is not JSON")
		self.assertRaises(DataError, self.reader.read, "{}")

		whostr = '{"type": "Person", "_label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		whostr = '{"@context": "fishbat", "type": "Person", "_label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		levelstr = '{"type": "Person", "parent_of": {"type": "Person", "_label": "child"}}'
		self.assertTrue(isinstance(self.reader.read(levelstr).parent_of[0], Person))

		basestr = '{"_label": "base"}'
		self.assertTrue(isinstance(self.reader.read(basestr), BaseResource))

		unknown = '{"type":"FishBat"}'
		self.assertRaises(DataError, self.reader.read, unknown)

		unknown2 = '{"type":"Person", "fishbat": "bob"}'
		self.assertRaises(DataError, self.reader.read, unknown)

	def test_attrib_assign(self):
		vocab.add_attribute_assignment_check()

		data = """
		{
		  "id": "https://linked.art/example/activity/12", 
		  "type": "AttributeAssignment", 
		  "assigned": {
		    "id": "https://linked.art/example/name/10", 
			"type": "Name", 
		    "content": "Exhibition Specific Name"
		  }, 
		  "assigned_property": "identified_by", 
		  "assigned_to": {
		    "id": "https://linked.art/example/object/12", 
		    "type": "HumanMadeObject", 
		    "_label": "Real Painting Name"
		  }
		}
		"""
		d = self.reader.read(data)
		self.assertTrue(isinstance(d, AttributeAssignment))


	def test_vocab_collision(self):
		# Test that the algorithm picks the right vocab instance
		# if multiple have the same AAT term but different base class

		data = """
        {
          "type": "LinguisticObject",
          "_label": "Sale recorded in catalog: B-267 0003 (1817) (record number 22947)",
	      "part_of": [
            {
              "type": "LinguisticObject",
              "_label": "Sale Catalog B-267",
              "classified_as": [
                {
                  "id": "http://vocab.getty.edu/aat/300026068",
                  "type": "Type",
                  "_label": "Auction Catalog"
                }
              ]
            }
          ]
        }
        """
		d = self.reader.read(data)
		self.assertTrue(isinstance(d.part_of[0], vocab.AuctionCatalogText))

