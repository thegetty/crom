
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import reader
from cromulent.model import factory, Person, DataError, BaseResource, Dimension

class TestReader(unittest.TestCase):

	def setUp(self):
		self.reader = reader.Reader()
		# ensure we can use parent_of
		Person._properties['parent_of']['okayToUse'] = 1

	def test_read(self):
		self.assertRaises(DataError, self.reader.read, "")
		self.assertRaises(DataError, self.reader.read, "This is not JSON")
		self.assertRaises(DataError, self.reader.read, "{}")

		whostr = '{"type": "Person", "_label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		whostr = '{"@context": "fishbat", "type": "Person", "_label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		levelstr = '{"type": "Person", "parent_of": {"type": "Person", "_label": "child"}}'
		self.assertTrue(isinstance(self.reader.read(levelstr).parent_of, Person))

		basestr = '{"_label": "base"}'
		self.assertTrue(isinstance(self.reader.read(basestr), BaseResource))

		unknown = '{"type":"FishBat"}'
		self.assertRaises(DataError, self.reader.read, unknown)

		unknown2 = '{"type":"Person", "fishbat": "bob"}'
		self.assertRaises(DataError, self.reader.read, unknown)

		# somewhere else, rdf_value has been added
		try:
			del Dimension._properties['value']
		except:
			# maybe not?
			pass

