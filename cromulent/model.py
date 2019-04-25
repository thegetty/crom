
from __future__ import unicode_literals
import os, sys, re
import codecs
import inspect
import uuid
import datetime

### Mappings for duplicate properties ###
### See build_tsv/vocab_reader

KEY_ORDER_DEFAULT = 10000
LINKED_ART_CONTEXT_URI = "https://linked.art/ns/v1/linked-art.json"
CRM_EXT_CONTEXT_URI = "https://linked.art/ns/v1/cidoc-extension.json"

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

class CromulentError(Exception):
	"""Base exception class"""

	resource = None

	def __init__(self, msg, resource=None):
		"""Initialize CidocError."""
		self.args = [msg]
		self.resource = resource

class ConfigurationError(CromulentError):
	"""Raised when an object (likely the factory) isn't configured properly for the current operation."""
	pass

class MetadataError(CromulentError):
	"""Base metadata exception."""
	pass

class RequirementError(MetadataError):
	"""Raised when schema/profile/metadata requirements not met."""
	pass

class DataError(MetadataError):
	"""Raised when data is not valid/allowed."""
	pass

class ProfileError(MetadataError):
	"""Raised when a class or property not in the configured profile is used"""
	pass

class CromulentFactory(object):

	def __init__(self, base_url="", base_dir="", lang="", full_names=False, 
		context="", context_file={}, load_context=True):
		self.base_url = base_url
		self.base_dir = base_dir

		self.debug_level = "warn"
		self.log_stream = sys.stderr

		self.materialize_inverses = False
		self.full_names = False
		self.pipe_scoped_contexts = False
		self.validate_properties = True
		self.validate_profile = True
		self.validate_range = True
		self.auto_assign_id = True
		self.process_multiplicity = True

		self.auto_id_type = "int-per-segment" #  "int", "int-per-type", "int-per-segment", "uuid"
		self.default_lang = lang
		self.filename_extension = ".json"
		# context_uri might actually be a list of URIs, and/or dicts
		self.context_uri = context
		self.context_json = {}

		self.prefixes = {}
		self.prefixes_rev = {}
		self.context_rev = {}
		# Maybe load it up for prefixes
		if load_context:
			context_filemap = {
				LINKED_ART_CONTEXT_URI: 
					os.path.join(os.path.dirname(__file__), 'data', 'linked-art.json'),
				CRM_EXT_CONTEXT_URI:
					os.path.join(os.path.dirname(__file__), 'data', 'cidoc-extension.json')
			}
			context_filemap.update(context_file)
			self.load_context(context, context_filemap)

		self.elasticsearch_compatible = False
		self.serialize_all_resources = False
		self.id_type_label = True

		self.json_indent = 2
		self.order_json = True
		self.key_order_hash = {"@context": 0, "id": 1, "type": 2, 
			"_label": 5, "value": 6}
		self.full_key_order_hash = {"@context": 0, "@id": 1, "rdf:type": 2, "@type": 2,
			"rdfs:label": 5, "rdf:value": 6}
		self.key_order_default = 10000

		self.underscore_properties = ["_label"]

		self._auto_id_types = {}
		self._auto_id_segments = {}
		self._auto_id_int = -1

	def load_context(self, context, context_filemap):

		if not context or not context_filemap:
			raise ConfigurationError("No context provided, and load_context not False")

		if type(context) != list:
			context = [context]

		js = {'@context': {}}
		for ct in context:
			fn = context_filemap.get(ct, "")
			if fn:
				try:
					fh = open(fn)
					data = fh.read()
					fh.close()
				except IOError:
					raise ConfigurationError("Provided context file does not exist")
			else:
				# Fetch from web
				data = "{}"

			try:
				ctx = json.loads(data)
				js['@context'].update(ctx['@context'])
			except:
				raise ConfigurationError("Provided context does not have valid JSON")				
		# this is the merged context information, not any single one
		self.context_json = js
		self.process_context()

	def process_context(self):
		# Filter context looking for prefixes
		# And make reverse mapping
		for (k,v) in self.context_json['@context'].items():
			if type(v) in STR_TYPES and v[-1] in ['/', '#']:
				self.prefixes[k] = v
				self.prefixes_rev[v] = k
			elif k == "@version":
				continue
			else:
				if type(v) in STR_TYPES:
					rdf = v
				else:
					rdf = v['@id']
				self.context_rev[rdf] = k

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

	def generate_id(self, what):
		if self.auto_id_type == "int":
			# increment and return
			self._auto_id_int += 1
			slug = self._auto_id_int
		elif self.auto_id_type == "int-per-segment":
			curr = self._auto_id_segments.get(what._uri_segment, -1)
			curr += 1
			self._auto_id_segments[what._uri_segment] = curr
			slug = self._auto_id_segments[what._uri_segment]
		elif self.auto_id_type == "int-per-type":
			t = type(what).__name__
			curr = self._auto_id_types.get(t, -1)
			curr += 1
			self._auto_id_types[t] = curr
			slug = self._auto_id_types[t]
		elif self.auto_id_type == "uuid":
			return "urn:uuid:%s" % uuid.uuid4()
		else:
			raise ConfigurationError("Unknown auto-id type")

		return self.base_url + what.__class__._uri_segment + "/" + str(slug)		

	def toJSON(self, what, done=None):
		""" Serialize what, making sure of no infinite loops """
		if not done:
			done = {}
		out = what._toJSON(top=True, done=done)
		return out

	def _collapse_json(self, text, collapse):
		js_indent = self.json_indent
		lines = text.splitlines()
		out = [lines[0]]
		while lines:
			l = lines.pop(0)
			indent = len(re.split('\S', l, 1)[0])
			if indent and l.rstrip()[-1] in ['[', '{']:
				curr = indent
				temp = []
				stemp = []
				while lines and curr <= indent:
					if temp and curr == indent:
						break
					temp.append(l[curr:])
					stemp.append(l.strip())
					l = lines.pop(0)
					indent = len(re.split('\S', l, 1)[0])					
				temp.append(l[curr:])
				stemp.append(l.lstrip())

				short = " " * curr + ''.join(stemp)
				if len(short) < collapse:
					out.append(short)
				else:
					ntext = '\n'.join(temp)
					nout = self._collapse_json(ntext, collapse)					
					for no in nout:
						out.append(" " * curr + no)
			elif indent:
				out.append(l)
		out.append(l)
		return out

	def collapse_json(self, text, collapse):
		return '\n'.join(self._collapse_json(text, collapse))

	def _buildString(self, js, compact=True, collapse=0):
		"""Build string from JSON."""
		try:
			if compact:
				out = json.dumps(js, separators=(',',':'))
			else:
				out = json.dumps(js, indent=self.json_indent)
		except:
			out = ""
			self.maybe_warn("Can't decode %r" % js)
			raise
		if collapse:
			out = self.collapse_json(out, collapse)
		return out 		

	def toString(self, what, compact=True, collapse=0, done=None):
		"""Return JSON setialization as string."""
		if not done:
			done = {}
		js = self.toJSON(what, done=done)
		return self._buildString(js, compact, collapse)

	def toFile(self, what, compact=True, filename="", done=None):
		"""Write to local file.

		Creates directories as necessary
		"""
		# TODO:  if self.serialize_all_resources:
		# then create separate files for every object, not just top level
		if not done:
			done = {}
		js = self.toJSON(what, done=done)

		if not filename:
			myid = js['id']
			mdb = self.base_url
			if not myid.startswith(mdb):
				raise ConfigurationError("The id of that object is not the base URI in the Factory")
			mdd = self.base_dir
			if not mdd:
				raise ConfigurationError("Directory on Factory must be set to write to file")
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
			filename = os.path.join(mdd, fp)

		fh = open(filename, 'w')
		out = self._buildString(js, compact)
		fh.write(out)
		fh.close()
		return out

class ExternalResource(object):
	"""Base class for all resources, including external references"""
	
	_factory = None
	_uri_segment = ""
	id = ""
	_full_id = ""
	_properties = {}
	_type = ""
	_niceType = ""
	_embed = True

	def __init__(self, ident=""):
		self._factory = factory
		if ident:
			if ident.startswith('urn:uuid'):
				self.id = ident
			elif ident.startswith('http'):
				# Try to find prefixable term
				hashed = ident.rsplit('#', 1)
				if len(hashed) == 1:
					(pref, rest) = ident.rsplit('/', 1)
					pref += "/"
				else:
					(pref, rest) = hashed
					pref += "#"

				if pref in self._factory.prefixes_rev:
					self._full_id = ident
					ident = "%s:%s" % (self._factory.prefixes_rev[pref], rest)

				self.id = ident
			else:
				# Allow for prefixed term
				curied = ident.split(':', 1)
				if len(curied) == 2 and curied[0] in self._factory.prefixes:
					self.id = ident
					self._full_id = self._factory.prefixes[curied[0]] + curied[1]	
				else:
					self.id = factory.base_url + self.__class__._uri_segment + "/" + ident

		elif factory.auto_assign_id:
			self.id = factory.generate_id(self)
		else:
			self.id = ""

	def _toJSON(self, done, top=False):
		if self._factory.elasticsearch_compatible:
			return {'id': self.id}
		else:
			return self.id

class BaseResource(ExternalResource):
	"""Base class for all resources with classes"""

	_integer_properties = []
	_object_properties = []
	_required_properties = []
	_warn_properties = []
	_classification = ""
	_classhier = []

	def __init__(self, ident="", label="", value="", **kw):
		"""Initialize BaseObject."""
		super(BaseResource, self).__init__(ident)

		if self._factory.validate_profile and hasattr(self, '_okayToUse'): 
			if not self._okayToUse:
				raise ProfileError("Class '%s' is configured to not be used" % self.__class__._type)
			elif self._okayToUse == 2:
				self.maybe_warn("Class '%s' is configured to warn on use" % self.__class__._type)

		# Set info other than identifier
		self.type = self.__class__._type
		if label:
			self._label = label
		# this might raise an exception if value is not allowed on the object
		# but easier to do it in the main init than on generated subclasses
		if value:
			try:
				self.value = value
			except:
				try:
					self.content = value
				except:
					raise ProfileError("Class '%s' does not hold values" % self.__class__._type)
		# Custom post initialization function for autoconstructed classes
		self._post_init(**kw)

	def _post_init(self, **kw):
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
			# _label goes through here, but it would below anyway, as it takes a Literal
			object.__setattr__(self, which, value)			
		else:
			# Allow per-class setters
			if hasattr(self, 'set_%s' % which):
				fn = getattr(self, 'set_%s' % which)
				return fn(value)

			if self._factory.validate_properties or self._factory.validate_profile or self._factory_validate_range:
				ok = self._check_prop(which, value)
			elif isinstance(value, ExternalResource):
				ok = 2
			else:
				ok = 1

			if ok == 2:
				self._set_magic_resource(which, value)
			else:			
				object.__setattr__(self, which, value)				

	def _prop_okay(self, which):
		for c in self._classhier:
			if which in c._properties:
				return c._properties[which]['okayToUse']		 

	def _check_prop(self, which, value):
		val_props = self._factory.validate_properties
		val_profile = self._factory.validate_profile
		val_range = self._factory.validate_range
		for c in self._classhier:
			if which in c._properties:
				if val_profile:
					okay = c._properties[which]['okayToUse']					
					rdf = c._properties[which]['rdf']
					if not okay:
						raise ProfileError("Property '%s' / '%s' is configured to not be used" % (which, rdf), self)
					elif okay == 2:
						self.maybe_warn("Property '%s' / '%s' is configured to warn on use" % (which, rdf))

				if val_range:
					rng = c._properties[which]['range']
					if rng == str:					
						return 1
					elif type(value) == BaseResource:
						# Allow direct instances of base resource anywhere
						# this is an override for external URIs
						return 2
					elif isinstance(value, rng):
						return 2
					else:
						raise DataError("Can't set '%s' on resource of type '%s' to '%r'" % (which, self._type, value), self)
				# Found it, but not validating range and either okay or not validating profile
				return 1
		if val_props:
			raise DataError("Can't set unknown field '%s' on resource of type '%s'" % (which, self._type), self)
		else:
			# Not validating ANYTHING
			return 1


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

		# N.B. This function is never used, but retained in case we somehow need language setting
		# in the future

		try:
			current = getattr(self, which)
		except:
			current = {}
		if type(value) in STR_TYPES:
			# use default language from factory
			value = {self._factory.default_lang: value}
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
			value = [current, value]
			object.__setattr__(self, which, value)

		if self._factory.materialize_inverses or self._factory.process_multiplicity:
			inverse = None
			multiple = 1
			for c in self._classhier:
				if which in c._properties:
					v = c._properties[which]
					if 'multiple' in v:
						multiple = v['multiple']
					if 'inverse' in v and v['inverse']:
						inverse = v['inverse']
						break
			if not inversed and self._factory.materialize_inverses and inverse:
				# set the backwards ref		
				value._set_magic_resource(inverse, self, True)
			if type(current) != list and multiple and self._factory.process_multiplicity:
				object.__setattr__(self, which, [getattr(self, which)])

	def _toJSON(self, done, top=False):
		"""Serialize as JSON."""
		# If we're already in the graph, return our URI only
		# This should only be called from the factory!

		d = self.__dict__.copy()
		del d['_factory']

		if not factory.id_type_label and (self.id in done or set(d.keys()) == set(['id', 'type'])):
			if self._factory.elasticsearch_compatible:
				return {'id': self.id}
			else:
				return self.id

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

		# Add back context at the top, if set
		if top and self._factory.context_uri: 
			d['@context'] = self._factory.context_uri

		if (self._factory.id_type_label and self.id in done) or (not top and not self._embed):
			# limit to only id, type, label
			nd = {}
			nd['id'] = d['id']
			try:
				nd['type'] = d['type']
			except:
				pass
			try:
				nd['_label'] = d['_label']
			except:
				pass
			d = nd
		else:	
			# otherwise, we're about to serialize the resource completely
			done[self.id] = 1			

		# Need to do in order now to get done correctly ordered
		KOH = self._factory.key_order_hash
		kodflt = self._factory.key_order_default
		kvs = sorted(d.items(), key=lambda x: KOH.get(x[0], kodflt))

		tbd = []
		for (k, v) in kvs:
			# some _foo might be carried through, eg _label or _comment
			if not v or (k[0] == "_" and not k in self._factory.underscore_properties):
				del d[k]
			else:
				if isinstance(v, ExternalResource):
					tbd.append(v.id)
				elif type(v) == list:
					for ni in v:
						if isinstance(ni, ExternalResource):
							tbd.append(ni.id)
						# For completeness should check datetime here too
				elif isinstance(v, datetime.datetime):
					# replace with string
					kvs[k] = v.strftime("%Y-%m-%dT%H:%M:%SZ")

		for t in tbd:
			if not t in done:
				done[t] = self.id
			
		for (k,v) in kvs:
			if v and (k[0] != "_" and not k in self._factory.underscore_properties):
				if isinstance(v, ExternalResource):
					if done[v.id] == self.id:
						del done[v.id]
					d[k] = v._toJSON(done=done)
				elif type(v) == list:
					newl = []
					for ni in v:
						if isinstance(ni, ExternalResource):
							if done[ni.id] == self.id:
								del done[ni.id]
							newl.append(ni._toJSON(done=done))
						else:
							# A number or string
							newl.append(ni)
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
			elif self.__class__._niceType:
				d['type'] = self.__class__._niceType
			elif d['type'] == self.__class__._type:
				d['type'] = self.__class__.__name__
			else:
				# ??!!
				raise ConfigurationError("Class is badly configured for type")

			if self._factory.pipe_scoped_contexts:
				# XXX TODO This should be configurable not hard coded
				if 'part' in d:
					# Calculate which part
					for c in reversed(self._classhier):
						if 'part' in c._properties:
							nk = c._properties['part']['rdf']
							d['part|%s' % nk]  = d['part']
							del d['part']
							break
				if 'part_of' in d:
					# Calculate which part
					for c in reversed(self._classhier):
						if 'part_of' in c._properties:
							nk = c._properties['part_of']['rdf']
							d['part_of|%s' % nk]  = d['part_of']
							del d['part_of']
							break

		if self._factory.order_json:
			return OrderedDict(sorted(d.items(), key=lambda x: KOH.get(x[0], 1000)))
		else:
			return d

# Ensure everything can have id, type, label and description
BaseResource._properties = {'id': {"rdf": "@id", "range": str, "okayToUse": 1}, 
	'type': {"rdf": "rdf:type", "range": str, "okayToUse": 1}, 
	'_label': {"rdf": "rdfs:label", "range": str, "okayToUse": 1}
}
BaseResource._classhier = (BaseResource, ExternalResource)

def process_tsv(fn):
	fh = codecs.open(fn, 'r', 'utf-8')
	lines = fh.readlines()[1:] # chomp header line
	fh.close()
	vocabData = {"rdf:Resource": 
		{"props": [], "label": "Resource", "className": "Resource", 
		"subs":[], "desc": "", "class": BaseResource, "okay": 1}}

	for l in lines:
		l = l[:-1] # chomp
		info= l.split('\t')
		name = info[0]	
		if info[1] == "class":
			data = {"subOf": info[5], "label": info[3], 'className': info[2],
				"desc": info[4], "class": None, "props": [], "subs": [], "okay": info[6]}
			vocabData[name] = data
		else:
			# property
			data = {"name": name, "subOf": info[5], "label": info[3], "propName": info[2],
			"desc": info[4], "range": info[7], "inverse": info[8], "okay": info[10], "multiple": info[11]}
			try:
				what = vocabData[info[6]]
			except:
				what = vocabData["rdf:Resource"]
			what["props"].append(data)

			koh = int(info[9])
			if koh != KEY_ORDER_DEFAULT:
				factory.full_key_order_hash[data['propName']] = koh
				factory.key_order_hash[data['name']] = koh

	# invert subclass hierarchy
	for k, v in vocabData.items():
		if k != "rdf:Resource":		
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
		try:	
			c.__bases__ += (parent,)
		except:
			print("MRO FAILURE: %r --> %r + %r" % (c, c.__bases__, parent))
			raise
		return

	c = type(name, (parent,), {'__doc__': data['desc']})
	globals()[name] = c
	data['class'] = c
	c._type = "crm:%s" % crmName
	c._uri_segment = name
	c._properties = {}
	c._okayToUse = int(data['okay'])

	# Set up real properties
	for p in data['props']:
		name = p['name']
		rng = p['range']
		ccname = p['propName']
		if p['inverse']:
			i = p['inverse']
			if i[0] == "P":
				invRdf = "crm:%s" % i
			else:
				invRdf = i
		else:
			invRdf = ""

		okay = p['okay']
		if not okay:
			okay = '1'
		okay = int(okay)
		mult = p['multiple']
		if not mult:
			mult = '0'
		mult = int(mult)

		# can't guarantee classes have been built yet :(
		c._properties[ccname] = {"rdf": "crm:%s" % name, 
			"rangeStr": rng,
			"inverseRdf": invRdf,
			"okayToUse": okay,
			"multiple": mult}
 
	# Build subclasses
	for s in data['subs']:
		build_class(s, c, vocabData)

def build_classes(fn=None, top=None):
	# Default to building our core dataset
	if not fn:
		dd = os.path.join(os.path.dirname(__file__), 'data')
		fn = os.path.join(dd, 'crm_vocab.tsv')
		top = 'E1_CRM_Entity'

	vocabData = process_tsv(fn)

	# Everything can have an id, a type, a label, a description
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


# XXX This should be invoked rather than inline so the module can be loaded
# and a different context used. But for now ...

# Build the factory first, so properties can be added to key_order
factory = CromulentFactory("http://lod.example.org/museum/", context="https://linked.art/ns/v1/linked-art.json")
build_classes()

