#!/usr/bin/env python3

import unittest
try:
	from contextlib import suppress
except:
	# Python 2.7
	suppress = None
import pprint
from datetime import datetime
from cromulent import model, vocab
from cromulent.extract import extract_monetary_amount
import cromulent.extract

CUSTOM_MAPPING = {
	'xxx': vocab.register_instance('xxx custom currency', {'parent': model.Currency, 'id': '999999999', 'label': 'My Dollars'}),
	'zzz': 'us dollars'
}

class TestCurrencyExtraction(unittest.TestCase):
	'''
	Test the ability to extract currency data.
	'''
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_extract_simple(self):
		e = extract_monetary_amount({
			'price': '10.0',
			'currency': 'pounds'
		})
		self.assertEqual(e.type, 'MonetaryAmount')
		self.assertEqual(e._label, '10.00 pounds')
		self.assertEqual(e.value, 10)
		c = e.currency
		self.assertEqual(c.type, 'Currency')
		self.assertEqual(c._label, 'British Pounds')

	def test_extract_comma_separated(self):
		e = extract_monetary_amount({
			'price': '1,280.5',
			'currency': 'pounds'
		})
		self.assertEqual(e.type, 'MonetaryAmount')
		self.assertEqual(e._label, '1,280.50 pounds')
		self.assertEqual(e.value, 1280.50)
		c = e.currency
		self.assertEqual(c.type, 'Currency')
		self.assertEqual(c._label, 'British Pounds')

	def test_extract_label_digits(self):
		e = extract_monetary_amount({
			'price': '1,280.5',
			'currency': 'pounds'
		}, truncate_label_digits=4)
		self.assertEqual(e.type, 'MonetaryAmount')
		self.assertEqual(e._label, '1,280.5000 pounds')
		self.assertEqual(e.value, 1280.50)
		c = e.currency
		self.assertEqual(c.type, 'Currency')
		self.assertEqual(c._label, 'British Pounds')

	def test_extract_multiple_comma_separated(self):
		e = extract_monetary_amount({
			'price': '1,310,720.5',
			'currency': 'pounds'
		})
		self.assertEqual(e.type, 'MonetaryAmount')
		self.assertEqual(e._label, '1,310,720.50 pounds')
		self.assertEqual(e.value, 1310720.5)
		c = e.currency
		self.assertEqual(c.type, 'Currency')
		self.assertEqual(c._label, 'British Pounds')

	def test_extract_est(self):
		e = extract_monetary_amount({
			'est_price': '12.0',
			'currency': 'pounds'
		})
		self.assertEqual(e.value, 12)
		c = e.currency
		self.assertEqual(e.classified_as[0]._label, 'Estimated Price')
		self.assertEqual(e.currency._label, 'British Pounds')

	def test_extract_start(self):
		e = extract_monetary_amount({
			'start_price': '8.5',
			'currency': 'pounds'
		})
		self.assertEqual(e.value, 8.5)
		c = e.currency
		self.assertEqual(e.classified_as[0]._label, 'Starting Price')
		self.assertEqual(e.currency._label, 'British Pounds')

	def test_extract_custom_currency_key(self):
		d = {
			'price': '7',
			'currency': 'zzz'
		}
		with self.assertRaises(AttributeError):
			e = extract_monetary_amount(d)
			self.assertEqual(e.currency._label, 'Custom Currency')
		
		e = extract_monetary_amount(d, currency_mapping=CUSTOM_MAPPING)
		self.assertEqual(e.value, 7)
		self.assertEqual(e.currency._label, 'US Dollars')

	def test_extract_custom_currency_instance(self):
		d = {
			'price': '7',
			'currency': 'xxx'
		}
		with self.assertRaises(AttributeError):
			e = extract_monetary_amount(d)
			self.assertEqual(e.currency._label, 'Custom Currency')
		
		e = extract_monetary_amount(d, currency_mapping=CUSTOM_MAPPING)
		self.assertEqual(e.value, 7)
		self.assertEqual(e.currency._label, 'My Dollars')

	def test_extract_price_with_citation(self):
		d = {
			'price': '7',
			'currency': 'pounds',
			'citation': 'crom test suite'
		}
		e = extract_monetary_amount(d, add_citations=True)
		self.assertEqual(e.value, 7)
		self.assertEqual(e.currency._label, 'British Pounds')
		self.assertEqual(e.referred_to_by[0].content, 'crom test suite')


if __name__ == '__main__':
	unittest.main()
