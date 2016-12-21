
from __future__ import unicode_literals
import os, sys
import codecs
import inspect

### Mappings for duplicate properties ###
### See build_tsv/vocab_reader

try:
    import json
except:
    # Fallback for 2.5
    import simplejson as json

try:
    # Only available in 2.7+
    # This makes the code a bit messy, but eliminates the need
    # for the locally hacked ordered json encoder
    from collections import OrderedDict
except:
    # Backported...
    try:
        from ordereddict import OrderedDict
    except:
        raise Exception("To run with old pythons you must: easy_install ordereddict")

try:
	STR_TYPES = [str, unicode] #Py2
except:
	STR_TYPES = [bytes, str] #Py3

class CidocError(Exception):
	"""Base exception class"""

	resource = None

	def __init__(self, msg, resource=None):
		"""Initialize CidocError."""
		self.args = [msg]
		self.resource = resource

class ConfigurationError(CidocError):
	"""Raised when an object (likely the factory) isn't configured properly for the current operation."""
	pass

class MetadataError(CidocError):
	"""Base metadata exception."""
	pass

class RequirementError(MetadataError):
	"""Raised when schema/profile/metadata requirements not met."""
	pass

class DataError(MetadataError):
	"""Raised when data is not valid/allowed."""
	pass

class CidocFactory(object):

	def __init__(self, base_url="", base_dir="", lang="", context="", full_names=False):
		self.base_url = base_url
		self.base_dir = base_dir

		self.debug_level = "warn"
		self.log_stream = sys.stderr
		self.done = {}

		self.materialize_inverses = False
		self.full_names = False
		self.validate_properties = True
		self.default_lang = lang
		self.filename_extension = ".json"
		self.context_uri = context
		self.elasticsearch_compatible = False

		self.key_order_hash = {"@context": 0, "id": 1, "type": 2, 
			"label": 5, "value": 6, "description": 7}
		self.full_key_order_hash = {"@context": 0, "@id": 1, "rdf:type": 2, "@type": 2,
			"rdfs:label": 5, "rdf:value": 6,  "dc:description": 7}
		self.key_order_default = 10000

	def set_debug_stream(self, strm):
		"""Set debug level."""
		self.log_stream = strm

	def set_debug(self, typ):
		"""Set behavior on errors and warnings.

		error = squash warnings
		warn = display warnings
		error_on_warning = raise exception for a warning rather than continuing
		"""
		if typ in ['error', 'warn', 'error_on_warning']:
			self.debug_level = typ
		else:
			raise ConfigurationError("Only levels are 'error', 'warn' and 'error_on_warning'")

	def maybe_warn(self, msg):
		"""warn method that respects debug_level property."""
		if self.debug_level == "warn":
			self.log_stream.write(msg + "\n")
			try:	
				self.log_stream.flush()
			except:
				pass
		elif self.debug_level == "error_on_warning":
			# We don't know the type, just raise a MetadataError
			raise MetadataError(msg)

	def toJSON(self, what):
		""" Serialize what, making sure of no infinite loops """
		self.done = {}
		out = what._toJSON(top=True)
		self.done = {}
		return out

	def _buildString(self, js, compact=True):
		"""Build string from JSON."""
		try:
			if type(js) == dict:
				if compact:
					out = json.dumps(js, sort_keys=True, separators=(',',':'))
				else:
					out = json.dumps(js, sort_keys=True, indent=2)
			else:
				if compact:
					out = json.dumps(js, separators=(',',':'))
				else:
					out = json.dumps(js, indent=2)
		except UnicodeDecodeError:
			self.maybe_warn("Can't decode %r" % js)
			out = ""
		return out 		

	def toString(self, what, compact=True):
		"""Return JSON setialization as string."""
		js = self.toJSON(what)
		return self._buildString(js, compact)

	def toFile(self, what, compact=True):
		"""Write to local file.

		Creates directories as necessary
		"""
		mdd = self.base_dir
		if not mdd:
			raise ConfigurationError("Directory on Factory must be set to write to file")

		js = self.toJSON(what)
		# Now calculate file path based on URI of top object
		# ... which is self for those of you following at home
		myid = js['id']
		mdb = self.base_url
		if not myid.startswith(mdb):
			raise ConfigurationError("The id of that object is not the base URI in the Factory")
		fp = myid[len(mdb):]	
		bits = fp.split('/')
		if len(bits) > 1:
			mydir = os.path.join(mdd, '/'.join(bits[:-1]))		
			try:
				os.makedirs(mydir)
			except OSError:
				pass

		if self.filename_extension:
			fp = fp + self.filename_extension

		fh = open(os.path.join(mdd, fp), 'w')
		out = self._buildString(js, compact)
		fh.write(out)
		fh.close()
		return out

class BaseResource(object):
	"""Base class for all resources."""

	_properties = {}
	_integer_properties = []
	_object_properties = []
	_lang_properties = []
	_required_properties = []
	_warn_properties = []
	_uri_segment = ""
	_type = ""
	_niceType = ""
	_classification = ""

	def __init__(self, ident="", label="", value="", **kw):
		"""Initialize BaseObject."""

		# Just add the factory from a global rather than passing it around C style
		self._factory = factory
		if ident:
			if ident.startswith('http'):
				self.id = ident
			else:
				self.id = factory.base_url + self.__class__._uri_segment + "/" + ident
		else:
			self.id = ""
		self.type = self.__class__._type
		if label:
			self.label = label
		# this might raise an exception if value is not allowed on the object
		# but easier to do it in the main init than on generated subclasses
		if value:
			self.value = value

		self._post_init()

	def _post_init(self):
		# Expect this to be overridden / replaced
		pass

	def __setattr__(self, which, value):
		"""Attribute setting magic for error checking and resource/literal handling."""
		try:
			types = [str, unicode, list, dict] #Py2
		except: 
			types = [bytes, str, list, dict] #Py3

		if which == 'context':
			raise DataError("Must not set the JSON LD context directly", self)
		elif which[0] == "_" or not value:
			object.__setattr__(self, which, value)			
		else:
			if self._factory.validate_properties:
				ok = self._check_prop(which, value)
				if not ok:
					raise DataError("Can't set non-standard field '%s' on resource of type '%s'" % (which, self._type), self)
			else:
				ok = 1

			# Allow per class setter functions to do extra magic
			if hasattr(self, which) and hasattr(self, 'set_%s' % which):
				fn = getattr(self, 'set_%s' % which)
				return fn(value)
			elif which in self._lang_properties:
				self._set_magic_lang(which, value)
			elif ok == 2:
				self._set_magic_resource(which, value)
			else:			
				object.__setattr__(self, which, value)				

	def _check_prop(self, which, value):
		for c in self._classhier:
			if which in c._properties:
				rng = c._properties[which]['range']
				if rng == str:					
					return 1
				elif isinstance(value, rng):
					return 2
				else:
					return 0
		return 0

	def _list_all_props(self):
		props = {}
		for c in self._classhier:		
			for k,v in c._properties.items():
				if not k in props:
					props[k] = v['range']
		return props

	def _check_reference(self, data):
		"""True if data is a resource or reference to a resource"""
		# "http://..."
		# {"@id": "http://..."}
		# or list of above
		if type(data) in STR_TYPES:
			return data.startswith('http')
		elif type(data) == dict:
			return 'id' in data
		elif isinstance(data, BaseResource):
			return True
		elif type(data) == list:
			for d in data:
				if type(d) in STR_TYPES and not d.startswith('http'):
					return False
				elif type(d) == dict and not 'id' in d:
					return False
			return True
		else:
			self._factory.maybe_warn("expecing a resource, got: %r" % (data))
			return True
			
	def maybe_warn(self, msg):
		"""warn that respects debug settings."""
		msg = "WARNING: " + msg
		self._factory.maybe_warn(msg)

	def _set_magic_lang(self, which, value):
		"""Magical handling of languages for string properties."""
		# Input:  string, and use "" or default_lang
		#         dict of lang: value
		# Merge with existing values

		try:
			current = getattr(self, which)
		except:
			current = {}
		if type(value) in STR_TYPES:
			# use default language from factory
			value = {factory.default_lang: value}
		if type(value) != dict:
			raise DataError("Should be a dict or a string when setting %s" % which, self)
		for k,v in value.items():
			if k in current:
				cv = current[k]
				if type(cv) != list:
					cv = [cv]
				if type(v) != list:
					v = [v]
				for vi in v:	
					cv.append(vi)
				current[k] = cv
			else:
				current[k] = v
		object.__setattr__(self, which, current)
	
	def _set_magic_resource(self, which, value, inversed=False):
		"""Set resource property.
		allow: string/object/dict, and magically generate list thereof
		"""
		try:
			current = getattr(self, which)
		except:
			current = None
		if not current:
			object.__setattr__(self, which, value)
		elif type(current) == list:
			current.append(value)
		else:
			new = [current, value]
			object.__setattr__(self, which, new)

		if not inversed and factory.materialize_inverses:
			# set the backwards ref
			inverse = None
			for c in self._classhier:
				if which in c._properties:
					v = c._properties[which]
					if 'inverse' in v:
						inverse = v['inverse']
						break
			if inverse:	
				value._set_magic_resource(inverse, self, True)

	def _toJSON(self, top=False):
		"""Serialize as JSON."""
		# If we're already in the graph, return our URI only
		# This should only be called from the factory!

		if self.id in self._factory.done:
			if self._factory.elasticsearch_compatible:
				return {'id': self.id}
			else:
				return self.id

		d = self.__dict__.copy()

		# In case of local contexts, not at the root
		if 'context' in d:
			d['@context'] = d['context']
			del d['context']
		for e in self._required_properties:
			if e not in d:
				raise RequirementError("Resource type '%s' requires '%s' to be set" % (self._type, e), self)
		debug = self._factory.debug_level
		if debug.find("warn") > -1:
			for e in self._warn_properties:
				if e not in d:
					msg = "Resource type '%s' should have '%s' set" % (self._type, e)
					self.maybe_warn(msg)
		if top:
			d['@context'] = self._factory.context_uri

		# WARNING:  This means that individual factories are NOT thread safe
		self._factory.done[self.id] = 1

		# Need to do in order now to get done correctly ordered
		KOH = self._factory.key_order_hash
		kodflt = self._factory.key_order_default
		kvs = sorted(d.items(), key=lambda x: KOH.get(x[0], kodflt))

		for (k, v) in kvs:
			if not v or k[0] == "_":
				del d[k]
			else:
				if isinstance(v, BaseResource):
					d[k] = v._toJSON()
				elif type(v) == list:
					newl = []
					for ni in v:
						if isinstance(ni, BaseResource):
							newl.append(ni._toJSON())
					d[k] = newl

		if self._factory.full_names:
			nd = {}
			# @context gets ganked by this renaming
			# so add it back in first.
			if top:
				nd['@context'] = self._factory.context_uri

			for (k,v) in d.items():
				# look up the rdf predicate in _properties
				for c in reversed(self._classhier):
					if k in c._properties:
						nk = c._properties[k]['rdf']
						nd[nk] = v
						break

			# Ensure full version uses basic @type
			if "rdf:type" in nd:
				nd['@type'] = nd['rdf:type']
				del nd['rdf:type']

			# And type gets ganked for overlay classes (Painting)
			# plus for stupidity classes (DestructionActivity)
			# so add this back too
			if not "@type" in nd or not nd['@type']:
				# find class up that has a type and use its name
				for c in reversed(self._classhier):
					if c._type:
						nd['@type'] = c._type

			d = nd
			KOH = self._factory.full_key_order_hash
		else:
			# Use existing programmer-friendly names for classes too
			if not 'type' in d:
				# find class up that has a type and use its name
				for c in self._classhier:
					if c._type:
						d['type'] = c.__name__
						break
			elif d['type'] == self.__class__._type:
				d['type'] = self.__class__.__name__
			elif self.__class__._niceType:
				d['type'] = self.__class__._niceType
			else:
				# ??!!
				raise ConfigurationError("Class is badly configured for type")

		return OrderedDict(sorted(d.items(), key=lambda x: KOH.get(x[0], 1000)))

def process_tsv(fn):
	fh = codecs.open(fn, 'r', 'utf-8')
	lines = fh.readlines()
	fh.close()
	vocabData = {}

	for l in lines:
		l = l[:-1] # chomp
		info= l.split('\t')
		name = info[0]	
		if info[1] == "class":
			data = {"subOf": info[5], "label": info[3], 'className': info[2],
				"desc": info[4], "class": None, "props": [], "subs": []}
			vocabData[name] = data
		else:
			# property
			data = {"name": name, "subOf": info[5], "label": info[3], "propName": info[2],
			"desc": info[4], "range": info[7], "inverse": info[8]}
			what = vocabData[info[6]]
			what["props"].append(data)
			# Add to KOH here, as object doesn't need to know it
			koh = int(info[9])
			if koh != factory.key_order_default:
				factory.key_order_hash[data['propName']] = koh
				factory.full_key_order_hash[data['name']] = koh

	# invert subclass hierarchy
	for k, v in vocabData.items():
		sub = v['subOf']
		# | separated list
		for s in sub.split('|'):
			if s:
				try:
					vocabData[s]['subs'].append(k)
				except:
					pass
	return vocabData

# Build class heirarchy recursively
def build_class(crmName, parent, vocabData):
	data = vocabData[crmName]
	name = str(data['className'])

	# check to see if we already exist
	# nb globals() here is only this module
	if name in globals():
		c = globals()[name]
		c.__bases__ += (parent,)
		return

	c = type(name, (parent,), {'__doc__': data['desc']})
	globals()[name] = c
	data['class'] = c
	c._type = "crm:%s" % crmName
	c._uri_segment = name
	c._properties = {}

	# Set up real properties
	for p in data['props']:
		name = p['name']
		rng = p['range']
		ccname = p['propName']
		invRdf = "crm:%s" % p["inverse"]
		# can't guarantee classes have been built yet :(
		c._properties[ccname] = {"rdf": "crm:%s" % name, 
			"rangeStr": rng,
			"inverseRdf": invRdf}
 
	# Build subclasses
	for s in data['subs']:
		build_class(s, c, vocabData)


def build_classes(fn=None, top='E1_CRM_Entity'):
	if not fn:
		dd = os.path.join(os.path.dirname(__file__), 'data')
		fn = os.path.join(dd, 'crm_vocab.tsv')

	vocabData = process_tsv(fn)

	# Everything can have an id, a type, a label, a description
	BaseResource._properties = {'id': {"rdf": "@id", "range": str}, 
		'type': {"rdf": "rdf:type", "range": str}, 
		'label': {"rdf": "rdfs:label", "range": str},
		'description': {"rdf": "dc:description", "range": str}
	}

	build_class(top, BaseResource, vocabData)

	# And add property definitions now we have class objects
	for v in vocabData.values():
		c = v['class']
		for p in c._properties.values():
			try:	
				rng = vocabData[p['rangeStr']]['class']
				# and add inverse prop name from range
				p['range'] = rng
				for (ik, iv) in rng._properties.items():
					if iv['inverseRdf'] == p['rdf']:
						p['inverse'] = ik
						break
			except:
				p['range'] = str
			try:
				del p['rangeStr']
			except:
				pass

	# set all of the classhiers
	for v in vocabData.values():
		c = v['class']
		c._classhier = inspect.getmro(c)[:-1]

# Build the factory first, so properties can be added to key_order
factory = CidocFactory("http://lod.example.org/museum/")
build_classes()
