import pprint
import re
from collections import namedtuple
from cromulent import model, vocab

number_pattern = r'((?:\d+\s+\d+/\d+)|(?:\d+(?:[.,]\d+)?))'
unit_pattern = r'''('|"|d[.]?|duymen|pouces?|inches|inch|in[.]?|pieds?|v[.]?|voeten|feet|foot|ft[.]?|cm)'''
dimension_pattern = '(%s\\s*(?:%s)?)' % (number_pattern, unit_pattern)
dimension_re = re.compile(r'\s*%s' % (dimension_pattern,))

simple_width_height_pattern = r'(?:\s*((?<!\w)[wh]|width|height))?'
simple_dimensions_pattern_x1 = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)' % (dimension_pattern, simple_width_height_pattern)
simple_dimensions_re_x1 = re.compile(simple_dimensions_pattern_x1)
simple_dimensions_pattern_x2 = ''\
	r'(?P<d1>(?:%s\s*)+)(?P<d1w>%s)'\
	r'(?:,)?\s*(x|by)'\
	r'(?P<d2>(?:\s*%s)+)(?P<d2w>%s)' % (
		dimension_pattern,
		simple_width_height_pattern,
		dimension_pattern,
		simple_width_height_pattern)
simple_dimensions_re_x2 = re.compile(simple_dimensions_pattern_x2)

# Haut 14 pouces, large 10 pouces
french_dimensions_pattern = r'[Hh]aut(?:eur)? (?P<d1>(?:%s\s*)+), [Ll]arge(?:ur)? (?P<d2>(?:%s\s*)+)' % (dimension_pattern, dimension_pattern)
french_dimensions_re = re.compile(french_dimensions_pattern)

# Hoog. 1 v. 6 d., Breed 2 v. 3 d.
dutch_dimensions_pattern = r'(?P<d1w>[Hh]oogh?[.]?|[Bb]reedt?) (?P<d1>(?:%s\s*)+), (?P<d2w>[Hh]oogh?[.]?|[Bb]reedt?) (?P<d2>(?:%s\s*)+)' % (dimension_pattern, dimension_pattern)
dutch_dimensions_re = re.compile(dutch_dimensions_pattern)

Dimension = namedtuple("Dimension", [
	'value',	# numeric value
	'unit',		# unit
	'which'		# e.g. width, height, ...
])

def _canonical_value(value):
	value = value.replace(',', '.')
	value = value.replace(' 1/4', '.25')
	value = value.replace(' 1/2', '.5')
	value = value.replace(' 3/4', '.75')
	if '/' in value:
		return None
	if value.startswith('.'):
		value = '0' + value
	return value

def _canonical_unit(value):
	if value is None:
		return None
	value = value.lower()
	if 'in' in value or value in ('pouces', 'pouce', 'duymen', 'd.', 'd') or value == '"':
		return 'inches'
	elif 'ft' in value or value in ('pieds', 'pied', 'feet', 'foot', 'voeten', 'v.', 'v') or value == "'":
		return 'feet'
	elif 'cm' in value:
		return 'cm'
	return None

def _canonical_which(value):
	if not value:
		return None
	value = value.strip().lower()
	if value.startswith('w'):
		return 'width'
	elif value.startswith('h'):
		return 'height'
	print('*** Unknown which dimension: %s' % (value,))
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
# 	print('DIMENSION: %s' % (value,))
	for m in re.finditer(dimension_re, value):
		# print('--> match %s' % (m,))
		v = _canonical_value(m.group(2))
		if not v:
			print('*** failed to canonicalize dimension value: %s' % (m.group(2),))
			return None
		unit_value = m.group(3)
		u = _canonical_unit(unit_value)
		if unit_value and not u:
			print('*** not a recognized unit: %s' % (unit_value,))
		which = _canonical_which(which)
		d = Dimension(value=v, unit=u, which=which)
		dims.append(d)
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
	nd = normalize_dimension(dimensions)
	if not nd:
		return None
	labels = []
	for d in dimensions:
		if d.unit == 'inches':
			labels.append('%s inches' % (d.value,))
		elif d.unit == 'feet':
			labels.append('%s feet' % (d.value,))
		elif d.unit == 'cm':
			labels.append('%s cm' % (d.value,))
		elif d.unit is None:
			labels.append('%s' % (d.value,))
		else:
			print('*** unrecognized unit: {d.unit}')
			return None
	label = ', '.join(labels)
	return nd, label

def normalize_dimension(dimensions):
	'''
	Given a list of `Dimension`s, normalize them into a single Dimension (e.g. values in
	both feet and inches become a single dimension of inches).

	If the values cannot be sensibly combined (e.g. inches + centimeters), returns `None`.
	'''
	unknown = 0
	inches = 0
	cm = 0
	which = None
	for d in dimensions:
		which = d.which
		if d.unit == 'inches':
			inches += float(d.value)
		elif d.unit == 'feet':
			inches += 12 * float(d.value)
		elif d.unit == 'cm':
			cm += float(d.value)
		elif d.unit is None:
			unknown += float(d.value)
		else:
			print('*** unrecognized unit: %s' % (d.unit,))
			return None
	used_systems = 0
	for v in (inches, cm, unknown):
		if v:
			used_systems += 1
	if used_systems != 1:
		print('*** dimension used a mix of unit systems (metric, imperial, and/or unknown): %r' % (dimensions,))
		return None
	elif inches:
		return Dimension(value=str(inches), unit='inches', which=which)
	elif cm:
		return Dimension(value=str(cm), unit='cm', which=which)
	else:
		return Dimension(value=str(cm), unit=None, which=which)

def extract_physical_dimensions(dimstr):
	dimensions = dimensions_cleaner(dimstr)
	if dimensions:
		for orig_d in dimensions:
			dimdata = normalized_dimension_object(orig_d)
			if dimdata:
				d, label = dimdata
				if d.which == 'height':
					dim = vocab.Height()
				elif d.which == 'width':
					dim = vocab.Width()
				else:
					dim = vocab.PhysicalDimension()
				dim.identified_by = model.Name(content=label)
				dim.value = d.value
				unit = vocab.instances.get(d.unit)
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
	for f in cleaners:
		d = f(value)
		if d:
			return d
	return None

def french_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a French-formatted string.'''
	# Haut 14 pouces, large 10 pouces

	m = french_dimensions_re.match(value)
	if m:
		d = m.groupdict()
		d1 = parse_simple_dimensions(d['d1'], 'h')
		d2 = parse_simple_dimensions(d['d2'], 'w')
		if d1 and d2:
			return (d1, d2)
		else:
			print('d1: %s %s h' % (d1, d['d1']))
			print('d2: %s %s w' % (d2, d['d2']))
			print('*** Failed to parse dimensions: %s' % (value,))
	return None

def dutch_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a Dutch-formatted string.'''
	# Hoog. 1 v. 6 d., Breed 2 v. 3 d.
	# Breedt 6 v., hoog 3 v

	m = dutch_dimensions_re.match(value)
	if m:
		d = m.groupdict()
		h = 'h'
		w = 'w'
		if 'breed' in d['d1w'].lower():
			h, w = w, h

		d1 = parse_simple_dimensions(d['d1'], h)
		d2 = parse_simple_dimensions(d['d2'], w)
		if d1 and d2:
			return (d1, d2)
		else:
			print('d1: %s %s h' % (d1, d['d1']))
			print('d2: %s %s w' % (d2, d['d2']))
			print('*** Failed to parse dimensions: %s' % (value,))
	return None

def simple_dimensions_cleaner_x1(value):
	'''Attempt to parse 1 dimension from a string.'''
	# 1 cm
	# 1' 2"
	# 1 ft. 2 in. h

	m = simple_dimensions_re_x1.match(value)
	if m:
		d = m.groupdict()
		d1 = parse_simple_dimensions(d['d1'], d['d1w'])
		if d1:
			return (d1,)
	return None

def simple_dimensions_cleaner_x2(value):
	'''Attempt to parse 2 dimensions from a string.'''
	# 1 cm x 2 in
	# 1' 2" by 3 cm
	# 1 ft. 2 in. h by 3 cm w

	m = simple_dimensions_re_x2.match(value)
	if m:
		d = m.groupdict()
		d1 = parse_simple_dimensions(d['d1'], d['d1w'])
		d2 = parse_simple_dimensions(d['d2'], d['d2w'])
		if d1 and d2:
			return (d1, d2)
		else:
			print('d1: %s %s %s' % (d1, d['d1'], d['d1w']))
			print('d2: %s %s %s' % (d2, d['d2'], d['d2w']))
			print('*** Failed to parse dimensions: %s' % (value,))
	return None
