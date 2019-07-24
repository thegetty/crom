#!/usr/bin/env python3

import unittest
import pprint
from datetime import datetime
from cromulent.extract import Dimension
import cromulent.extract

class TestDateCleaners(unittest.TestCase):
	'''
	Test the ability to recognize and parse various formats of dates.
	'''
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_parse_simple_dimensions(self):
		'''
		Test the documented formats that `cromulent.extract.parse_simple_dimensions` can parse
		and ensure that it returns the expected data.
		'''
		tests = {
			"3'": [Dimension('3', 'feet', None)],
			'3 feet': [Dimension('3', 'feet', None)],
			'3 foot': [Dimension('3', 'feet', None)],
			'3 ft': [Dimension('3', 'feet', None)],
			'3 ft.': [Dimension('3', 'feet', None)],
			'2"': [Dimension('2', 'inches', None)],
			'2 in': [Dimension('2', 'inches', None)],
			'2 in.': [Dimension('2', 'inches', None)],
			'2 inch': [Dimension('2', 'inches', None)],
			'2 inches': [Dimension('2', 'inches', None)],
			'2 duymen': [Dimension('2', 'inches', None)],
			'2 d.': [Dimension('2', 'inches', None)],
			'2 d': [Dimension('2', 'inches', None)],
			'''2'8"''': [Dimension('2', 'feet', None), Dimension('8', 'inches', None)],
			'4cm': [Dimension('4', 'cm', None)],
			'2 pieds 3 pouces': [Dimension('2', 'feet', None), Dimension('3', 'inches', None)],
			'1 pied 7 pouces': [Dimension('1', 'feet', None), Dimension('7', 'inches', None)],
			'8 pouce': [Dimension('8', 'inches', None)],
			'8 pouces': [Dimension('8', 'inches', None)],
			'8 1/2 pouces': [Dimension('8.5', 'inches', None)],
			'8 1/4 pouces': [Dimension('8.25', 'inches', None)],
			'8 1/8 pouces': [Dimension('8.125', 'inches', None)],
			'1': [Dimension('1', None, None)],
		}

		for value, expected in tests.items():
			dims = cromulent.extract.parse_simple_dimensions(value)
			if expected is not None:
				self.assertIsInstance(dims, list)
				self.assertEqual(dims, expected, msg='dimensions: %r' % (value,))
			else:
				self.assertIsNone(dims)

	def test_dimension_cleaner(self):
		'''
		Test the documented formats that `cromulent.extract.dimensions_cleaner` can parse
		and ensure that it returns the expected data.
		'''
		tests = {
			'''2 in by 1 in''': ([Dimension('2', 'inches', None)], [Dimension('1', 'inches', None)]),
			'''2'2"h x 2'8"w''': ([Dimension('2', 'feet', 'height'), Dimension('2', 'inches', 'height')], [Dimension('2', 'feet', 'width'), Dimension('8', 'inches', 'width')]),
			'''1'3"x4cm h''': ([Dimension('1', 'feet', None), Dimension('3', 'inches', None)], [Dimension('4', 'cm', 'height')]),
			'''1'3" by 4"''': ([Dimension('1', 'feet', None), Dimension('3', 'inches', None)], [Dimension('4', 'inches', None)]),
			'Haut 14 pouces, large 10 pouces': ([Dimension('14', 'inches', 'height')], [Dimension('10', 'inches', 'width')]),
			'Haut. 48 pouces, large 68 pouces': ([Dimension('48', 'inches', 'height')], [Dimension('68', 'inches', 'width')]),
			'1 by 4': ([Dimension('1', None, None)], [Dimension('4', None, None)]),
			'Hoog. 6 v., breed 3 v': ([Dimension('6', 'feet', 'height')], [Dimension('3', 'feet', 'width')]),
			'Breedt 6 v., hoog 3 v': ([Dimension('6', 'feet', 'width')], [Dimension('3', 'feet', 'height')]),
			'20 cm x 24,5 cm': ([Dimension('20', 'cm', None)], [Dimension('24.5', 'cm', None)]),
			'2 w by 5 h': ([Dimension('2', None, 'width')], [Dimension('5', None, 'height')]),
		}

		for value, expected in tests.items():
			dims = cromulent.extract.dimensions_cleaner(value)
			if expected is not None:
				self.assertIsInstance(dims, tuple)
# 				print('===== got:')
# 				pprint.pprint(dims)
# 				print('----- expected:')
# 				pprint.pprint(expected)
# 				print('=====')
				self.assertEqual(dims, expected, msg='dimensions: %r' % (value,))
			else:
				self.assertIsNone(dims)

if __name__ == '__main__':
	unittest.main()
