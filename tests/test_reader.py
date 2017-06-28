
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import reader
from cromulent.model import factory, Person, DataError, BaseResource
from cromulent.extra import EoEActivity

class TestReader(unittest.TestCase):

	def setUp(self):
		self.reader = reader.Reader()
		# ensure we can use parent_of
		Person._properties['parent_of']['okayToUse'] = 1

	def test_read(self):
		self.assertRaises(DataError, self.reader.read, "")
		self.assertRaises(DataError, self.reader.read, "This is not JSON")
		self.assertRaises(DataError, self.reader.read, "{}")

		whostr = '{"type": "Person", "label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		whostr = '{"@context": "fishbat", "type": "Person", "label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))

		levelstr = '{"type": "Person", "parent_of": {"type": "Person", "label": "child"}}'
		self.assertTrue(isinstance(self.reader.read(levelstr).parent_of, Person))

		basestr = '{"label": "base"}'
		self.assertTrue(isinstance(self.reader.read(basestr), BaseResource))

		eoeact = '{"type": ["EndOfExistence", "Activity"], "label":"boo crm"}'
		self.assertTrue(isinstance(self.reader.read(eoeact), EoEActivity))

		unknown = '{"type":"FishBat"}'
		self.assertRaises(DataError, self.reader.read, unknown)


