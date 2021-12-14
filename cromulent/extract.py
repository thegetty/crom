# -*- coding: utf-8 -*-

import re
import warnings
from collections import namedtuple
from contextlib import contextmanager

import locale
import calendar
from contextlib import contextmanager, suppress
from datetime import datetime, timedelta

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

NEXT_FINER_DIMENSION_UNIT = {
	'inches': None,
	'feet': 'inches',
	'cm': None,
	'fr_feet': 'fr_inches',
	'fr_inches': 'ligne'
}
NUMBER_PATTERN = r'((?:\d+\s+\d+/\d+)|(?:\d+/\d+)|(?:\d+(?:[.,]\d+)?))'
UNIT_PATTERN = r'''('|"|d(?:[.]?|uymen)|pouc[e.]s?|in(?:ch(?:es)?|[.]?)|'''\
				r'''pieds?|v[.]?|voeten|f(?:eet|oot|t[.]?)|cm|lignes?|linges?)'''
DIMENSION_PATTERN = '(%s\\s*(?:%s)?)' % (NUMBER_PATTERN, UNIT_PATTERN)
DIMENSION_RE = re.compile(r'\s*%s' % (DIMENSION_PATTERN,))

SIMPLE_WIDTH_HEIGHT_PATTERN = r'(?:\s*((?<!\w)[wh]|width|height))?'
SIMPLE_DIMENSIONS_PATTERN_X1 = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)' % (DIMENSION_PATTERN, SIMPLE_WIDTH_HEIGHT_PATTERN)
SIMPLE_DIMENSIONS_RE_X1 = re.compile(SIMPLE_DIMENSIONS_PATTERN_X1)
SIMPLE_DIMENSIONS_PATTERN_X2a = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)'\
	r'(?:,)?\s*(x|by)'\
	r'(?P<d2>(?:\s*%s)+)(?P<d2w>%s)' % (
		DIMENSION_PATTERN,
		SIMPLE_WIDTH_HEIGHT_PATTERN,
		DIMENSION_PATTERN,
		SIMPLE_WIDTH_HEIGHT_PATTERN)
SIMPLE_DIMENSIONS_PATTERN_X2b = ''\
	r'(?P<d1w>%s)\s*(?P<d1>(?:%s\s*)+)'\
	r'*(?:(?:,)?\s*(x|by)|,\s*)'\
	r'(?P<d2w>%s)\s*(?P<d2>(?:\s*%s)+)' % (
		SIMPLE_WIDTH_HEIGHT_PATTERN,
		DIMENSION_PATTERN,
		SIMPLE_WIDTH_HEIGHT_PATTERN,
		DIMENSION_PATTERN)
SIMPLE_DIMENSIONS_RE_X2a = re.compile(SIMPLE_DIMENSIONS_PATTERN_X2a)
SIMPLE_DIMENSIONS_RE_X2b = re.compile(SIMPLE_DIMENSIONS_PATTERN_X2b)

# Haut 14 pouces, large 10 pouces
FRENCH_DIMENSIONS_PATTERN = r'[Hh](?:(?:aut(?:eur|[.])?)|[.])\s*(?P<d1>(?:%s\s*)+),? '\
							r'[Ll](?:(?:arge?(?:ur|[.])?)|[.])\s*(?P<d2>(?:%s\s*)+)' % (
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
		elif len(parts) == 1 and '/' in parts[0]:
			intpart = 0
			numer, denom = map(int, parts[0].split('/', 1))
			fracpart = float(numer)/denom
			value = str(intpart + fracpart)
		if value.startswith('.'):
			value = '0' + value
		
		try:
			return int(value)
		except ValueError:
			return float(value)
	except:
		pass
	return None

def _canonical_unit(value):
	inches = {'duymen', 'd.', 'd', '"'}
	feet = {'pieds', 'pied', 'feet', 'foot', 'voeten', 'v.', 'v', "'"}
	fr_inches = {'pouces', 'pouce', 'pouc.'}
	fr_feet = {'pieds', 'pied'}
	if value is None:
		return None
	value = value.lower()
	if value in fr_inches:
		return 'fr_inches'
	if value in fr_feet:
		return 'fr_feet'
	if 'ligne' in value or 'linge' in value:
		return 'ligne'
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

	last_unit = None
	for match in re.finditer(DIMENSION_RE, value):
		# warnings.warn('--> match %s' % (match,))
		matched_value = _canonical_value(match.group(2))
		if not matched_value:
			warnings.warn('*** failed to canonicalize dimension value: %s' % (match.group(2),))
			return None
		unit_value = match.group(3)
		matched_unit = _canonical_unit(unit_value)
		if matched_unit is None:
			matched_unit = NEXT_FINER_DIMENSION_UNIT.get(last_unit)
		if unit_value and not matched_unit:
			warnings.warn('*** not a recognized unit: %s' % (unit_value,))
		which = _canonical_which(which)
		dim = Dimension(value=matched_value, unit=matched_unit, which=which)
		last_unit = matched_unit
		dims.append(dim)
	if not dims:
		return None
	return dims

def normalized_dimension_object(dimensions, source=None, **kwargs):
	'''
	Normalizes the given `dimensions`, or returns `None` is normalization fails.

	Returns a tuple of the normalized data, and a label which preserves the original
	set of dimensions.

	For example, the input:

		[
			Dimension(value=10, unit='feet', which=None),
			Dimension(value=3, unit='inches', which=None),
		]

	results in the output:

		(
			Dimension(value=123.0, unit='inches', which=None),
			"10 feet, 3 inches"
		)
	'''
	normalized = normalize_dimension(dimensions, source=source, **kwargs)
	if not normalized:
		return None
	labels = []
	for dim in dimensions:
		if dim.unit == 'inches':
			units = ('inch', 'inches')
		elif dim.unit == 'feet':
			units = ('foot', 'feet')
		elif dim.unit == 'fr_feet':
			units = ('French foot', 'French feet')
		elif dim.unit == 'fr_inches':
			units = ('French inch', 'French inches')
		elif dim.unit == 'cm':
			units = ('cm', 'cm')
		elif dim.unit == 'ligne':
			units = ('ligne', 'lignes')
		elif dim.unit is None:
			units = ('', '')
		else:
			warnings.warn('*** unrecognized unit: {dim.unit}')
			return None
		unit = units[0] if (float(dim.value) == 1.0) else units[1]
		if unit:
			label = '%s %s' % (dim.value, unit)
		else:
			label = str(dim.value)
		labels.append(label)
	label = ', '.join(labels)
	return normalized, label

def normalize_dimension(dimensions, source=None):
	'''
	Given a list of `Dimension`s, normalize them into a single Dimension (e.g. values in
	both feet and inches become a single dimension of inches).

	If the values cannot be sensibly combined (e.g. inches + centimeters), returns `None`.
	'''
	unknown = 0
	inches = 0
	fr_inches = 0
	centimeters = 0
	used_unknown = False
	used_inches = False
	used_fr_inches = False
	used_centimeters = False
	which = None
	for dim in dimensions:
		which = dim.which
		if dim.unit == 'inches':
			inches += dim.value
			used_inches = True
		elif dim.unit == 'feet':
			inches += 12 * dim.value
			used_inches = True
		elif dim.unit == 'cm':
			centimeters += dim.value
			used_centimeters = True
		elif dim.unit == 'fr_feet':
			fr_inches += 12.0 * dim.value
			used_fr_inches = True
		elif dim.unit == 'fr_inches':
			fr_inches += dim.value
			used_fr_inches = True
		elif dim.unit == 'ligne':
			fr_inches += dim.value / 12.0
			used_fr_inches = True
		elif dim.unit is None:
			unknown += dim.value
			used_unknown = True
		else:
			warnings.warn('*** unrecognized unit: %s' % (dim.unit,))
			return None

	used_systems = 0
	for used in (used_inches, used_fr_inches, used_centimeters, used_unknown):
		if used:
			used_systems += 1
	if used_systems != 1:
		if source:
			warnings.warn('*** dimension used a mix of metric, imperial, and/or unknown: '\
							'%r; source is %r' % (dimensions, source))
		else:
			warnings.warn('*** dimension used a mix of metric, imperial, and/or unknown: '\
							'%r' % (dimensions,))
		return None
	if fr_inches:
		return Dimension(value=fr_inches, unit='fr_inches', which=which)
	if inches:
		return Dimension(value=inches, unit='inches', which=which)
	if centimeters:
		return Dimension(value=centimeters, unit='cm', which=which)
	return Dimension(value=unknown, unit=None, which=which)

def extract_physical_dimensions(dimstr, **kwargs):
	dimensions = dimensions_cleaner(dimstr, **kwargs)
	if dimensions:
		for orig_d in dimensions:
			dimdata = normalized_dimension_object(orig_d, source=dimstr)
			if dimdata:
				dimension, label = dimdata
				if dimension.which == 'height':
					dim = vocab.Height(ident='')
				elif dimension.which == 'width':
					dim = vocab.Width(ident='')
				else:
					dim = vocab.PhysicalDimension(ident='')
				dim.value = dimension.value
				dim.identified_by = model.Name(ident='', content=label)
				unit = vocab.instances.get(dimension.unit)
				if unit:
					dim.unit = unit
				yield dim

def dimensions_cleaner(value, default_unit=None):
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
		dimensions = cleaner(value)
		if dimensions:
			if default_unit:
				for i, d_list in enumerate(dimensions):
					for j, d in enumerate(d_list):
						if d.unit is None:
							dimensions[i][j] = Dimension(value=d.value, unit=default_unit, which=d.which)
			return dimensions
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

	for pattern in (SIMPLE_DIMENSIONS_RE_X2a, SIMPLE_DIMENSIONS_RE_X2b):
		match = pattern.match(value)
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

def extract_monetary_amount(data, add_citations=False, currency_mapping=CURRENCY_MAPPING, source_mapping=None, truncate_label_digits=2):
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
	if 'price' in data or 'price_amount' in data or 'amount' in data:
		amnt = model.MonetaryAmount(ident='')
		price_amount = data.get('price_amount', data.get('price', data.get('amount')))
		price_currency = data.get('currency', data.get('price_currency', data.get('price_curr')))
		note = data.get('price_note', data.get('price_desc', data.get('note')))
		cite = data.get('price_citation', data.get('citation'))
		source = data.get('price_source', '')
	elif 'est_price' in data or 'est_price_amount' in data:
		amnt = vocab.EstimatedPrice(ident='')
		price_amount = data.get('est_price_amount', data.get('est_price'))
		price_currency = data.get('currency', data.get('est_price_currency', data.get('est_price_curr')))
		amount_type = 'Estimated Price'
		note = data.get('est_price_note', data.get('est_price_desc', data.get('note')))
		cite = data.get('est_price_citation', data.get('citation'))
		source = data.get('est_price_source', data.get('est_price_so', ''))
	elif 'start_price' in data or 'start_price_amount' in data:
		amnt = vocab.StartingPrice(ident='')
		price_amount = data.get('start_price_amount', data.get('start_price'))
		price_currency = data.get('currency', data.get('start_price_currency', data.get('start_price_curr')))
		amount_type = 'Starting Price'
		note = data.get('start_price_note', data.get('start_price_desc', data.get('note')))
		cite = data.get('start_price_citation', data.get('citation'))
		source = data.get('start_price_source', data.get('start_price_so', ''))
	else:
		return None

	price_amount_label = price_amount
	if price_amount or price_currency:
		if cite and add_citations:
			amnt.referred_to_by = vocab.BibliographyStatement(ident='', content=cite)
		if note:
			amnt.referred_to_by = vocab.Note(ident='', content=note)

		if price_amount:
			try:
				value = price_amount
				value = value.replace('[?]', '')
				value = value.replace('?', '')
				value = value.strip()
				if re.search(re.compile(r',\d\d\d'), value):
					value = value.replace(',', '')
				value = float(value)
				
				label_fmt = '{:,.%df}' % truncate_label_digits
				price_amount_label = label_fmt.format(value)

				amnt.value = value
			except ValueError:
				amnt._label = price_amount
				amnt.identified_by = model.Name(ident='', content=price_amount)
	# 			warnings.warn(f'*** Not a numeric price amount: {value}')
		if price_currency:
			price_currency_key = price_currency
			try:
				price_currency_key = currency_mapping[price_currency_key.lower()]
			except KeyError:
				pass
			if isinstance(price_currency_key, model.BaseResource):
				amnt.currency = price_currency_key
			elif price_currency_key in vocab.instances:
				amnt.currency = vocab.instances[price_currency_key]
			else:
				warnings.warn('*** No currency instance defined for %s' % (price_currency_key,))
		if price_amount_label and price_currency:
			amnt._label = '%s %s' % (price_amount_label, price_currency)
		elif price_amount:
			amnt._label = '%s' % (price_amount,)
		return amnt
	return None



# Datetime Cleaning (from Getty Pipeline code)
# https://github.com/thegetty/pipeline/blob/master/pipeline/util/cleaners.py 

def date_parse(value, delim):
	# parse a / or - or . date or range

	bits = value.split(delim)
	if len(bits) == 2:
		# YYYY/ range
		b1 = bits[0].strip()
		b2 = bits[1].strip()
		if len(b2) < 3 :
			b2 = "%s%s" % (b1[:len(b1)-len(b2)], b2)
		elif len(b2) > 4:
			print("Bad range: %s" % value)
			return None
		try:
			return [datetime(int(b1),1,1), datetime(int(b2)+1,1,1)]
		except:
			print("Broken delim: %s" % value)
			return None
	elif len(bits) == 3:
		# YYYY/MM/DD or YY/YY/YYYY or DD.MM.YYYY or YYYY.MM.DD
		m = int(bits[1])
		if len(bits[0]) == 4:
			y = int(bits[0])
			d = int(bits[2])
		else:
			y = int(bits[2])
			d = int(bits[0])
		if m == 0:
			m = 1
		if d == 0:
			d = 1
		if m > 12:
			# swap them
			d, m = m, d
		try:
			yearmonthday = datetime(y,m,d)
			return [yearmonthday, yearmonthday+timedelta(days=1)]
		except:
			print("Bad // value: %s" % value)
	else:
		print("broken / date: %s" % value)
	return None

def date_cleaner(value):

	# FORMATS:

	# YYYY[?]
	# YYYY/MM/DD
	# DD/MM/YYYY
	# ca. YYYY
	# aft[er|.] YYYY
	# bef[ore|.] YYYY
	# YYYY.MM.DD
	# YYYY/(Y|YY|YYYY)
	# YYYY-YY
	# YYY0s
	# YYYY-
	# YYYY Mon
	# YYYY Month DD

	if value:
		value = value.replace("?",'')
		value = value.replace('est', '')
		value = value.replace("()", '')
		value = value.replace(' or ', '/')
		value = value.strip()
		value = value.replace('by ', 'bef.')
		value = value.replace('c.', 'ca.')
		value = value.replace('CA.', 'ca.')
		value = value.replace('af.', 'aft.')

	if not value:
		return None

	elif value.startswith("|"):
		# Broken? null it out
		return None

	elif len(value) <= 4 and value.isdigit():
		# year only
		return [datetime(int(value),1,1), datetime(int(value)+1,1,1)]

	elif value.startswith('v.'):
		value = value[2:].strip()
		return None

	elif value.startswith('-') and value[1:].isdigit():
		# BCE year
		# These are problematic, as python datetime.datetime() doesn't support them :(
		return [int(value), int(value)+1]

	elif value.endswith('s'):
		# 1950s
		if len(value) == 5 and value[:4].isdigit():
			y = int(value[:4])
			return [datetime(y,1,1), datetime(y+10,1,1)]
		else:
			warnings.warn("Bad YYYYs date: %s" % value)
			return None

	elif len(value) == 5 and value[:4].isdigit() and value.endswith('-'):
		y = int(value[:4])
		return [datetime(y,1,1), None]

	elif value.startswith("ca"):
		# circa x
		value = value[3:].strip()
		if len(value) == 4 and value.isdigit():
			y = int(value)
			return [datetime(y-CIRCA,1,1), datetime(y+CIRCA,1,1)]
		else:
			# Try and parse it
			if value.find('/') > -1:
				val = date_parse(value, '/')
			elif value.find('-') > -1:
				val = date_parse(value, '-')

			if not val:
				warnings.warn("bad circa: %s" % value)
				return None

			val[0] -= CIRCA_D
			val[1] += CIRCA_D
			return val

	elif value.startswith('aft'):
		# after x
		value = value.replace('aft.', '')
		value = value.replace('after ', '')
		value = value.strip()
		try:
			y = int(value)
		except:
			warnings.warn("Bad aft value: %s" % value)
			return None
		return [datetime(y,1,1), None]

	elif value.startswith('bef'):
		value = value.replace('bef.', '')
		value = value.replace('before ', '')
		value = value.strip()
		y = int(value)
		return [None, datetime(y,1,1)]

	elif value.find('/') > -1:
		# year/year or year/month/date
		# 1885/90
		# 07/02/1897
		return date_parse(value, '/')

	elif value.find('.') > -1:
		return date_parse(value, '.')

	elif value.find('-') > -1:
		# 0 could be -983 for 983 BCE
		return date_parse(value, '-')

	elif value.find(';') > -1:
		return date_parse(value, ';')

	else:
		with c_locale(), suppress(ValueError):
			yearmonthday = datetime.strptime(value, '%Y %B %d')
			if yearmonthday:
				return [yearmonthday, yearmonthday+timedelta(days=1)]

		with c_locale(), suppress(ValueError):
			yearmonth = datetime.strptime(value, '%Y %b')
			if yearmonth:
				year = yearmonth.year
				month = yearmonth.month
				maxday = calendar.monthrange(year, month)[1]
				d = datetime(year, month, 1)
				r = [d, d+timedelta(days=maxday)]
				return r

		warnings.warn('fell through to: {value!r}'.format(value=value))
		return None

@contextmanager
def c_locale():
	l = locale.getlocale()
	locale.setlocale(locale.LC_ALL, 'C')
	try:
		yield
	finally:
		locale.setlocale(locale.LC_ALL, l)

