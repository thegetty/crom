
from __future__ import unicode_literals
import os, sys, subprocess
import codecs
import inspect

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
	subprocess.check_output #should be OK in python2.7 up
except:
	#python2.6, see <http://python-future.org/standard_library_imports.html>
	from future.standard_library import install_aliases
	install_aliases()

try:
	STR_TYPES = [str, unicode] #Py2
except:
	STR_TYPES = [bytes, str] #Py3


class CidocError(Exception):
	"""Base exception for iiif_prezi."""

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


class StructuralError(MetadataError):
	"""Raised when there are structural problem with an object/metadata."""
	pass


class RequirementError(MetadataError):
	"""Raised when metadata requirements not met."""
	pass


class DataError(MetadataError):
	"""Raised when metadata is not valid/allowed."""
	pass

class CidocFactory(object):

	def __init__(self, base_url="", base_dir="", lang="", context="", full_names=False):
		self.base_url = base_url
		self.base_dir = base_dir
		self.default_lang = lang
		self.context_uri = context

		self.debug_level = "warn"
		self.log_stream = sys.stderr

		self.namespaces = {}
		self.class_map = {}
		self.property_map = {}

		self.full_names = True
		self.key_order_hash = {"@context": 0, "id": 1, "type": 2, "label": 3, "value": 4, "is_identified_by": 10 }
		self.full_key_order_hash = {"@context": 0, "@id": 1, "rdf:type": 2, "rdfs:label": 3, "rdf:value": 4, 
			"dc:description": 5,
			"crm:p1_is_identified_by": 10 }


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
		mdb = self._factory.base_url
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
	_lang_properties = ["label", "has_note"]
	_required_properties = []
	_warn_properties = []
	_uri_segment = ""

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

	def __setattr__(self, which, value):
		"""Attribute setting magic for error checking and resource/literal handling."""
		try:
			types = [str, unicode, list, dict] #Py2
		except: 
			types = [bytes, str, list, dict] #Py3

		if which == 'context':
			raise DataError("Must not set the JSON LD context directly")
		elif which[0] == "_" or not value:
			object.__setattr__(self, which, value)			
		else:
			ok = self._check_prop(which, value)
			if not ok:
				raise DataError("Can't set non-standard field '%s' on resource of type '%s'" % (which, self._type))

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
			if c._properties.has_key(which):
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
				if not props.has_key(k):
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
				if type(d) in STR_TYPES and not data.startswith('http'):
					return False
				elif type(d) == dict and not 'id' in d:
					return False
			return True
		else:
			print("expecing a resource, got: %r" % (data))
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
			raise DataError("Should be a dict or a string")
		for k,v in value.items():
			if current.has_key(k):
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
	
	def _set_magic_resource(self, which, value):
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
			new = current.append(value)
			object.__setattr__(self, which, new)
		else:
			new = [current, value]
			object.__setattr__(self, which, new)


	def _toJSON(self, top=False):
		"""Serialize as JSON."""
		# If we're already in the graph, return our URI only

		# This should only be called from the factory!

		if self._factory.done.has_key(self.id):
			return self.id

		d = self.__dict__.copy()

		for (k, v) in list(d.items()): #list makes copy in Py3
			if not v or k[0] == "_":
				del d[k]
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
		self._factory.done[self.id] = 1
		# Recurse
		for k,v in d.items():
			if isinstance(v, BaseResource):
				d[k] = v._toJSON()
			elif type(v) == list:
				newl = []
				for ni in v:
					if isinstance(ni, BaseResource):
						newl.append(v._toJSON())
				d[k] = newl

		if self._factory.full_names:
			nd = {}
			# @context gets ganked by this renaming
			# so add it back in first.
			if top:
				nd['@context'] = self._factory.context_uri

			for (k,v) in d.items():
				# look up the rdf predicate in _properties
				for c in self._classhier:
					if c._properties.has_key(k):
						nk = c._properties[k]['rdf']
						nd[nk] = v
						break
			d = nd
			KOH = self._factory.full_key_order_hash
		else:
			# Use existing programmer-friendly names
			KOH = self._factory.key_order_hash
		return OrderedDict(sorted(d.items(), key=lambda x: KOH.get(x[0], 1000)))


	def _should_be_minimal(self, what):
		"""Return False."""
		return False

def process_tsv(fn='crm_vocab.tsv'):
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
			"desc": info[4], "range": info[7]}
			what = vocabData[info[6]]
			what["props"].append(data)

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
	if globals().has_key(name):
		c = globals()[name]
		c.__bases__ += (parent,)
		return

	c = type(name, (parent,), {})
	globals()[name] = c
	data['class'] = c
	c._type = "crm:%s" % crmName
	c._description = data['desc']
	c._uri_segment = name
	c._properties = {}

	# Set up real properties
	for p in data['props']:
		name = p['name']
		rng = p['range']
		ccname = p['propName']
		# can't guarantee classes have been built yet :(
		c._properties[ccname] = {"rdf": "crm:%s" % name, "rangeStr": rng}

	# Build subclasses
	for s in data['subs']:
		build_class(s, c, vocabData)


def build_classes(fn='crm_vocab.tsv'):
	vocabData = process_tsv(fn)

	# Everything can have an id, a type and a label
	BaseResource._properties = {'id': {"rdf": "@id", "range": str}, 
		'type': {"rdf": "rdf:type", "range": str}, 
		'label': {"rdf": "rdfs:label", "range": str},
		'description': {"rdf": "dc:description", "range": str}
	}

	build_class('E1_CRM_Entity', BaseResource, vocabData)

	# And add property definitions now we have class objects
	for v in vocabData.values():
		c = v['class']
		for p in c._properties.values():
			try:	
				p['range'] = vocabData[p['rangeStr']]['class']
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

	# Add some necessary extras outside of the ontology
	SymbolicObject._properties['value'] = {"rdf": "rdfs:value", "range": str}
	TimeSpan._properties['begin_of_the_begin'] = {"rdf": "crm:p82a_begin_of_the_begin", "range":str}
	TimeSpan._properties['begin_of_the_end'] = {"rdf": "crm:p81b_begin_of_the_end", "range":str}
	TimeSpan._properties['end_of_the_begin'] = {"rdf": "crm:p81a_end_of_the_begin", "range":str}
	TimeSpan._properties['end_of_the_end'] = {"rdf": "crm:p82b_end_of_the_end", "range":str}

build_classes()
factory = CidocFactory("http://lod.example.org/museum/")
