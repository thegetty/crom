# -*- coding: utf-8 -*-

import re
import warnings
from collections import namedtuple

from cromulent import model, vocab

#mark - Mapping Dictionaries

# TODO: can this be refactored somewhere?
CURRENCY_MAPPING = {
	'österreichische schilling': 'at shillings',
	'florins': 'de florins',
	'fl': 'de florins',
	'fl.': 'de florins',
	'pounds': 'gb pounds',
	'livres': 'fr livres',
	'guineas': 'gb guineas',
	'reichsmark': 'de reichsmarks'
}

#mark - Dimensions

NUMBER_PATTERN = r'((?:\d+\s+\d+/\d+)|(?:\d+(?:[.,]\d+)?))'
UNIT_PATTERN = r'''('|"|d(?:[.]?|uymen)|pouces?|in(?:ch(?:es)?|[.]?)|'''\
				r'''pieds?|v[.]?|voeten|f(?:eet|oot|t[.]?)|cm)'''
DIMENSION_PATTERN = '(%s\\s*(?:%s)?)' % (NUMBER_PATTERN, UNIT_PATTERN)
DIMENSION_RE = re.compile(r'\s*%s' % (DIMENSION_PATTERN,))

SIMPLE_WIDTH_HEIGHT_PATTERN = r'(?:\s*((?<!\w)[wh]|width|height))?'
SIMPLE_DIMENSIONS_PATTERN_X1 = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)' % (DIMENSION_PATTERN, SIMPLE_WIDTH_HEIGHT_PATTERN)
SIMPLE_DIMENSIONS_RE_X1 = re.compile(SIMPLE_DIMENSIONS_PATTERN_X1)
SIMPLE_DIMENSIONS_PATTERN_X2 = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)'\
	r'(?:,)?\s*(x|by)'\
	r'(?P<d2>(?:\s*%s)+)(?P<d2w>%s)' % (
		DIMENSION_PATTERN,
		SIMPLE_WIDTH_HEIGHT_PATTERN,
		DIMENSION_PATTERN,
		SIMPLE_WIDTH_HEIGHT_PATTERN)
SIMPLE_DIMENSIONS_RE_X2 = re.compile(SIMPLE_DIMENSIONS_PATTERN_X2)

# Haut 14 pouces, large 10 pouces
FRENCH_DIMENSIONS_PATTERN = r'[Hh]aut(?:eur|[.])? (?P<d1>(?:%s\s*)+), '\
							r'[Ll]arge(?:ur|[.])? (?P<d2>(?:%s\s*)+)' % (
								DIMENSION_PATTERN, DIMENSION_PATTERN)
FRENCH_DIMENSIONS_RE = re.compile(FRENCH_DIMENSIONS_PATTERN)

# Hoog. 1 v. 6 d., Breed 2 v. 3 d.
DUTCH_DIMENSIONS_PATTERN = r'(?P<d1w>[Hh]oogh?[.]?|[Bb]reedt?) (?P<d1>(?:%s\s*)+), '\
							r'(?P<d2w>[Hh]oogh?[.]?|[Bb]reedt?) (?P<d2>(?:%s\s*)+)' % (
								DIMENSION_PATTERN, DIMENSION_PATTERN)
DUTCH_DIMENSIONS_RE = re.compile(DUTCH_DIMENSIONS_PATTERN)

Dimension = namedtuple("Dimension", [
	'value',	# numeric value
	'unit',		# unit
	'which'		# e.g. width, height, ...
])

def _canonical_value(value):
	try:
		value = value.replace(',', '.')
		parts = value.split(None, 1)
		if len(parts) > 1 and '/' in parts[1]:
			intpart = int(parts[0])
			numer, denom = map(int, parts[1].split('/', 1))
			fracpart = float(numer)/denom
			value = str(intpart + fracpart)
		if value.startswith('.'):
			value = '0' + value
		return value
	except:
		pass
	return None

def _canonical_unit(value):
	inches = {'pouces', 'pouce', 'duymen', 'd.', 'd', '"'}
	feet = {'pieds', 'pied', 'feet', 'foot', 'voeten', 'v.', 'v', "'"}
	if value is None:
		return None
	value = value.lower()
	if 'in' in value or value in inches:
		return 'inches'
	if 'ft' in value or value in feet:
		return 'feet'
	if 'cm' in value:
		return 'cm'
	return None

def _canonical_which(value):
	if not value:
		return None
	value = value.strip().lower()
	if value.startswith('w'):
		return 'width'
	if value.startswith('h'):
		return 'height'
	warnings.warn('*** Unknown which dimension: %s' % (value,))
	return None

def parse_simple_dimensions(value, which=None):
	'''
	Parse the supplied string for dimensions (value + unit), and return a list of
	`Dimension`s, optionally setting the `which` property to the supplied value.

	Examples:

	1 cm
	2ft
	5 pieds
	'''
	if value is None:
		return None
	value = value.strip()
	dims = []
# 	warnings.warn('DIMENSION: %s' % (value,))
	for match in re.finditer(DIMENSION_RE, value):
		# warnings.warn('--> match %s' % (match,))
		matched_value = _canonical_value(match.group(2))
		if not matched_value:
			warnings.warn('*** failed to canonicalize dimension value: %s' % (match.group(2),))
			return None
		unit_value = match.group(3)
		matched_unit = _canonical_unit(unit_value)
		if unit_value and not matched_unit:
			warnings.warn('*** not a recognized unit: %s' % (unit_value,))
		which = _canonical_which(which)
		dim = Dimension(value=matched_value, unit=matched_unit, which=which)
		dims.append(dim)
	if not dims:
		return None
	return dims

def normalized_dimension_object(dimensions):
	'''
	Normalizes the given `dimensions`, or returns `None` is normalization fails.

	Returns a tuple of the normalized data, and a label which preserves the original
	set of dimensions.

	For example, the input:

		[
			Dimension(value='10', unit='feet', which=None),
			Dimension(value='3', unit='inches', which=None),
		]

	results in the output:

		(
			Dimension(value='123.0', unit='inches', which=None),
			"10 feet, 3 inches"
		)
	'''
	normalized = normalize_dimension(dimensions)
	if not normalized:
		return None
	labels = []
	for dim in dimensions:
		if dim.unit == 'inches':
			labels.append('%s inches' % (dim.value,))
		elif dim.unit == 'feet':
			labels.append('%s feet' % (dim.value,))
		elif dim.unit == 'cm':
			labels.append('%s cm' % (dim.value,))
		elif dim.unit is None:
			labels.append('%s' % (dim.value,))
		else:
			warnings.warn('*** unrecognized unit: {dim.unit}')
			return None
	label = ', '.join(labels)
	return normalized, label

def normalize_dimension(dimensions):
	'''
	Given a list of `Dimension`s, normalize them into a single Dimension (e.g. values in
	both feet and inches become a single dimension of inches).

	If the values cannot be sensibly combined (e.g. inches + centimeters), returns `None`.
	'''
	unknown = 0
	inches = 0
	centimeters = 0
	which = None
	for dim in dimensions:
		which = dim.which
		if dim.unit == 'inches':
			inches += float(dim.value)
		elif dim.unit == 'feet':
			inches += 12 * float(dim.value)
		elif dim.unit == 'cm':
			centimeters += float(dim.value)
		elif dim.unit is None:
			unknown += float(dim.value)
		else:
			warnings.warn('*** unrecognized unit: %s' % (dim.unit,))
			return None
	used_systems = 0
	for values in (inches, centimeters, unknown):
		if values:
			used_systems += 1
	if used_systems != 1:
		warnings.warn('*** dimension used a mix of metric, imperial, and/or unknown: '\
						'%r' % (dimensions,))
		return None
	if inches:
		return Dimension(value=str(inches), unit='inches', which=which)
	if centimeters:
		return Dimension(value=str(centimeters), unit='cm', which=which)
	return Dimension(value=str(centimeters), unit=None, which=which)

def extract_physical_dimensions(dimstr):
	dimensions = dimensions_cleaner(dimstr)
	if dimensions:
		for orig_d in dimensions:
			dimdata = normalized_dimension_object(orig_d)
			if dimdata:
				dimension, label = dimdata
				if dimension.which == 'height':
					dim = vocab.Height()
				elif dimension.which == 'width':
					dim = vocab.Width()
				else:
					dim = vocab.PhysicalDimension()
				dim.identified_by = model.Name(content=label)
				dim.value = dimension.value
				unit = vocab.instances.get(dimension.unit)
				if unit:
					dim.unit = unit
				yield dim

def dimensions_cleaner(value):
	'''
	Attempt to parse a set of dimensions from the given string.

	Returns a tuple of `pipeline.util.Dimension` objects if parsing succeeds,
	None otherwise.
	'''
	if value is None:
		return None
	cleaners = [
		simple_dimensions_cleaner_x2,
		french_dimensions_cleaner_x2,
		dutch_dimensions_cleaner_x2,
		simple_dimensions_cleaner_x1
	]
	for cleaner in cleaners:
		dimension = cleaner(value)
		if dimension:
			return dimension
	return None

def french_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a French-formatted string.'''
	# Haut 14 pouces, large 10 pouces

	match = FRENCH_DIMENSIONS_RE.match(value)
	if match:
		groups = match.groupdict()
		dim1 = parse_simple_dimensions(groups['d1'], 'h')
		dim2 = parse_simple_dimensions(groups['d2'], 'w')
		if dim1 and dim2:
			return (dim1, dim2)
		warnings.warn('dim1: %s %s h' % (dim1, groups['d1']))
		warnings.warn('dim2: %s %s w' % (dim2, groups['d2']))
		warnings.warn('*** Failed to parse dimensions: %s' % (value,))
	return None

def dutch_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a Dutch-formatted string.'''
	# Hoog. 1 v. 6 d., Breed 2 v. 3 d.
	# Breedt 6 v., hoog 3 v

	match = DUTCH_DIMENSIONS_RE.match(value)
	if match:
		groups = match.groupdict()
		height = 'h'
		width = 'w'
		if 'breed' in groups['d1w'].lower():
			height, width = width, height

		dim1 = parse_simple_dimensions(groups['d1'], height)
		dim2 = parse_simple_dimensions(groups['d2'], width)
		if dim1 and dim2:
			return (dim1, dim2)
		warnings.warn('dim1: %s %s h' % (dim1, groups['d1']))
		warnings.warn('dim2: %s %s w' % (dim2, groups['d2']))
		warnings.warn('*** Failed to parse dimensions: %s' % (value,))
	return None

def simple_dimensions_cleaner_x1(value):
	'''Attempt to parse 1 dimension from a string.'''
	# 1 cm
	# 1' 2"
	# 1 ft. 2 in. h

	match = SIMPLE_DIMENSIONS_RE_X1.match(value)
	if match:
		groups = match.groupdict()
		dim1 = parse_simple_dimensions(groups['d1'], groups['d1w'])
		if dim1:
			return (dim1,)
	return None

def simple_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a string.'''
	# 1 cm x 2 in
	# 1' 2" by 3 cm
	# 1 ft. 2 in. h by 3 cm w

	match = SIMPLE_DIMENSIONS_RE_X2.match(value)
	if match:
		groups = match.groupdict()
		dim1 = parse_simple_dimensions(groups['d1'], groups['d1w'])
		dim2 = parse_simple_dimensions(groups['d2'], groups['d2w'])
		if dim1 and dim2:
			return (dim1, dim2)
		warnings.warn('dim1: %s %s %s' % (dim1, groups['d1'], groups['d1w']))
		warnings.warn('dim2: %s %s %s' % (dim2, groups['d2'], groups['d2w']))
		warnings.warn('*** Failed to parse dimensions: %s' % (value,))
	return None

#mark - Monetary Values

def extract_monetary_amount(data):
	'''
	Returns a `MonetaryAmount`, `StartingPrice`, or `EstimatedPrice` object
	based on properties of the supplied `data` dict. If no amount or currency
	data is found in found, returns `None`.

	For `EstimatedPrice`, values will be accessed from these keys:
		- amount: `est_price_amount` or `est_price`
		- currency: `est_price_currency` or `est_price_curr`
		- note: `est_price_note` or `est_price_desc`
		- bibliographic statement: `est_price_citation`

	For `StartingPrice`, values will be accessed from these keys:
		- amount: `start_price_amount` or `start_price`
		- currency: `start_price_currency` or `start_price_curr`
		- note: `start_price_note` or `start_price_desc`
		- bibliographic statement: `start_price_citation`

	For `MonetaryAmount` prices, values will be accessed from these keys:
		- amount: `price_amount` or `price`
		- currency: `price_currency` or `price_curr`
		- note: `price_note` or `price_desc`
		- bibliographic statement: `price_citation`
	'''
	amount_type = 'Price'
	if 'est_price' in data:
		amnt = vocab.EstimatedPrice()
		price_amount = data.get('est_price_amount', data.get('est_price'))
		price_currency = data.get('est_price_currency', data.get('est_price_curr'))
		amount_type = 'Estimated Price'
		note = data.get('est_price_note', data.get('est_price_desc'))
		cite = data.get('est_price_citation')
	elif 'start_price' in data:
		amnt = vocab.StartingPrice()
		price_amount = data.get('start_price_amount', data.get('start_price'))
		price_currency = data.get('start_price_currency', data.get('start_price_curr'))
		amount_type = 'Starting Price'
		note = data.get('start_price_note', data.get('start_price_desc'))
		cite = data.get('start_price_citation')
	else:
		amnt = model.MonetaryAmount()
		price_amount = data.get('price_amount', data.get('price'))
		price_currency = data.get('price_currency', data.get('price_curr'))
		note = data.get('price_note', data.get('price_desc'))
		cite = data.get('price_citation')

	if price_amount or price_currency:
		if cite:
			amnt.referred_to_by = vocab.BibliographyStatement(content=cite)
		if note:
			amnt.referred_to_by = vocab.Note(content=note)

		if price_amount:
			try:
				value = price_amount
				value = value.replace('[?]', '')
				value = value.replace('?', '')
				value = value.strip()
				price_amount = float(value)
				amnt.value = price_amount
			except ValueError:
				amnt._label = price_amount
				amnt.identified_by = model.Name(content=price_amount)
	# 			warnings.warn(f'*** Not a numeric price amount: {value}')
		if price_currency:
			if price_currency in CURRENCY_MAPPING:
				try:
					price_currency = CURRENCY_MAPPING[price_currency.lower()]
				except KeyError:
					pass
			if price_currency in vocab.instances:
				amnt.currency = vocab.instances[price_currency]
			else:
				warnings.warn('*** No currency instance defined for %s' % (price_currency,))
		if price_amount and price_currency:
			amnt._label = '%s %s' % (price_amount, price_currency)
		elif price_amount:
			amnt._label = '%s' % (price_amount,)
		return amnt
	return None
