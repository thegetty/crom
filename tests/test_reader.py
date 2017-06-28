
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import reader
from cromulent.model import factory, Person, DataError

class TestReader(unittest.TestCase):

	def setUp(self):
		self.reader = reader.Reader()

	def test_read(self):
		self.assertRaises(DataError, self.reader.read, "")
		self.assertRaises(DataError, self.reader.read, "This is not JSON")
		self.assertRaises(DataError, self.reader.read, "{}")

		whostr = '{"type": "Person", "label": "me"}'
		self.assertTrue(isinstance(self.reader.read(whostr), Person))
		