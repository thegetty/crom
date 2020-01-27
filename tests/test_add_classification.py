
import unittest 

try:
	from collections import OrderedDict
except:
	# 2.6
	from ordereddict import OrderedDict

from cromulent import model, vocab
from cromulent.model import factory

class TestAddClassification(unittest.TestCase):
	def test_add_classification(self):
		amnt = model.MonetaryAmount(ident='')
		amnt.value = 7.0
		self.assertNotIn('Asking Price', factory.toString(amnt))
		vocab.add_classification(amnt, vocab.AskingPrice)
		self.assertIn('Asking Price', factory.toString(amnt))

if __name__ == '__main__':
	unittest.main()
