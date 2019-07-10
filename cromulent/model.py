
from __future__ import unicode_literals
import os, sys, re
import codecs
import inspect
import uuid
import datetime

KEY_ORDER_DEFAULT = 10000
LINKED_ART_CONTEXT_URI = "https://linked.art/ns/v1/linked-art.json"

# 2.5 and 2.6 are very out of date. Assume 2.7 or better
import json
from collections import OrderedDict, namedtuple

try:
	STR_TYPES = [str, unicode] #Py2.7
	FILE_STREAM_CLASS = file
except:
	import io
	STR_TYPES = [bytes, str] #Py3.x
	FILE_STREAM_CLASS = io.TextIOBase


PropInfo = namedtuple("PropInfo", [
	'property', # the name of the property, eg 'identified_by'
	'predicate', # the name from the ontology, eg 'crm:P1_is_identified_by'
	'range', # the class which is the range of this predicate, eg model.Identifier
	'inverse_property', # the name of the property which is the inverse of this one, eg 'identifies'
	'inverse_predicate', # the predicate for the inverse of this one, eg 'crm:P1i_idenfifies'
	'multiple_okay', # can there be multiple values, eg True
	'profile_okay' # is this property okay according to the profile, eg 0 (no), 1 (yes), 2 (warn)
	])


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

		self.materialize_inverses = False # Create the inverse relationship on the object to the subject
		self.full_names = False # Use full property and class names in output
		self.pipe_scoped_contexts = False # Serialize to "name|Pnn_x_y" for scoped properties (documentation)
		self.validate_properties = True # validate properties are even CRM
		self.validate_profile = True # Validate linked_art specific stuff
		self.validate_range = True # Raise if attempt to set prop to invalid class
		self.validate_multiplicity = True  # Raise if attempt to set n:1 to []
		self.auto_assign_id = True # Automatially assign a URI
		self.process_multiplicity = True # Return multiple with single value as [value]

		self.auto_id_type = "int-per-segment" #  "int", "int-per-type", "int-per-segment", "uuid"
		# self.default_lang = lang  # NOT USED
		self.filename_extension = ".json"  # some people like .jsonld
		self.context_uri = context # Might be a list, or a context value as a dict
		self.context_json = {}

		self.prefixes = {}
		self.prefixes_rev = {}
		self.context_rev = {}
		# Maybe load it up for prefixes
		if load_context:
			# Leave this as a map for future extensions
			context_filemap = {
				LINKED_ART_CONTEXT_URI: 
					os.path.join(os.path.dirname(__file__), 'data', 'linked-art.json')
			}
			context_filemap.update(context_file)
			self.load_context(context, context_filemap)

		self.elasticsearch_compatible = False # return {'id': 'uri'} instead of string
		self.linked_art_boundaries = False # break on linked art API boundaries between classes
		self.id_type_label = True # references are id, type and _label, not just id.

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
		self._all_classes = {}


	def load_context(self, context, context_filemap):

		if not context or not context_filemap:
			raise ConfigurationError("No context provided, and load_context not False")

		if type(context) is not list:
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
				# XXX Fetch from web
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
		# Note that this does not process scoped contexts for member_of / part_of
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

	def __getstate__(self):
		# Make a copy of current object state
		d = self.__dict__.copy()
		# try to flush the stream
		try:
			self.log_stream.flush()
		except:
			# stream instance may not support flush()
			pass
		# Now reify the log stream
		strm = d['log_stream']
		if strm is sys.stdout:
			d['log_stream'] = ("sys.stdout", "stream")
		elif strm is sys.stderr:
			d['log_stream'] = ("sys.stderr", "stream")
		elif isinstance(strm, FILE_STREAM_CLASS):
			d['log_stream'] = (strm.name, "file")
		else:
			d['log_stream'] = None
		return d

	def __setstate__(self, state):
		# State is __dict__ with a reified log_stream as above
		self.__dict__.update(state)
		if self.log_stream:
			if self.log_stream[1] == "stream":
				if self.log_stream[0] == "sys.stdout":
					self.log_stream = sys.stdout
				elif self.log_stream[0] == "sys.stderr":
					self.log_stream = sys.stderr
			elif self.log_stream[1] == "file":
				try:
					self.log_stream = open(self.log_stream[0], 'a') 
				except:
					self.log_stream = None


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
		out = what._toJSON(top=what, done=done)
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
	_all_properties = {}
	_type = ""
	_embed = True


	def _is_uri(self, what):
		uri_schemes = ['urn:uuid:', 'tag:', 'data:', 'mailto:', 'info:', 'ftp:/', 'sftp:/'] 
		for u in uri_schemes:
			if what.startswith(u):
				return True
		return False


	def __init__(self, ident=None):
		self._factory = factory
		if ident is not None:
			if self._is_uri(ident):
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
			elif ident == "":
				# Allow explicit setting of empty string
				self.id = ""
			else:
				# Allow for prefixed term that isn't ambiguously a URI
				curied = ident.split(':', 1)
				if len(curied) == 2 and curied[0] in self._factory.prefixes:
					self.id = ident
					self._full_id = self._factory.prefixes[curied[0]] + curied[1]	
				else:
					self.id = factory.base_url + self.__class__._uri_segment + "/" + ident
		elif factory.auto_assign_id:
			self.id = factory.generate_id(self)
		else:
			# Not auto assigning, and not submitted = blank node
			self.id = ""

	def _toJSON(self, done, top=None):
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

	def __init__(self, ident=None, label="", value="", content="", **kw):
		"""Initialize BaseObject."""
		super(BaseResource, self).__init__(ident)

		# Alias value and content together
		if content and not value:
			value = content

		if self._factory.validate_profile and hasattr(self, '_okayToUse'): 
			if not self._okayToUse:
				raise ProfileError("Class '%s' is configured to not be used" % self.__class__._type)
			elif self._okayToUse == 2:
				self._factory.maybe_warn("Class '%s' is configured to warn on use" % self.__class__._type)

		# Set label and value/content
		if label:
			self._label = label
		# this might raise an exception if value is not allowed on the object
		# but easier to do it in the main init than on many generated subclasses
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

	def __dir__(self):
		d = dir(self.__class__)
		d.extend(self.list_all_props())
		return sorted(d)

	@property
	def type(self):
		for c in self._classhier:
			if c._type:
				return c.__name__

	@type.setter
	def type(self, value):
		raise AttributeError("Must not set 'type' on resources directly")


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

			if self._factory.validate_properties or self._factory.validate_profile or self._factory.validate_range:
				ok = self._check_prop(which, value)
			elif isinstance(value, ExternalResource):
				ok = 2
			else:
				ok = 1

			if ok == 2:
				self._set_magic_resource(which, value)
			else:			
				object.__setattr__(self, which, value)				
		 
	def _check_prop(self, which, value):
		val_props = self._factory.validate_properties
		val_profile = self._factory.validate_profile
		val_range = self._factory.validate_range
		for c in self._classhier:
			if which in c._all_properties:
				pinfo = c._all_properties[which]

				if val_profile:
					okay = pinfo.profile_okay					
					rdf = pinfo.predicate
					if not okay:
						raise ProfileError("Property '%s' / '%s' is configured to not be used" % (which, rdf), self)
					elif okay == 2:
						self._factory.maybe_warn("Property '%s' / '%s' is configured to warn on use" % (which, rdf))

				if val_range:
					rng = pinfo.range
					if rng is str:					
						return 1
					elif type(value) is BaseResource:
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

	def _check_reference(self, data):
		"""True if data is a resource or reference to a resource"""
		# "http://..."
		# {"@id": "http://..."}
		# or list of above
		if type(data) in STR_TYPES:
			return data.startswith('http')
		elif type(data) is dict:
			return 'id' in data
		elif isinstance(data, BaseResource):
			return True
		elif type(data) is list:
			for d in data:
				if type(d) in STR_TYPES and not d.startswith('http'):
					return False
				elif type(d) is dict and not 'id' in d:
					return False
			return True
		else:
			self._factory.maybe_warn("expecing a resource, got: %r" % (data))
			return True
			
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
		if type(value) is not dict:
			raise DataError("Should be a dict or a string when setting %s" % which, self)
		for k,v in value.items():
			if k in current:
				cv = current[k]
				if type(cv) is not list:
					cv = [cv]
				if type(v) is not list:
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

		if self._factory.materialize_inverses or self._factory.process_multiplicity or \
			self._factory.validate_multiplicity:
			inverse = None
			multiple = 1
			for c in self._classhier:
				if which in c._all_properties:
					v = c._all_properties[which]
					multiple = v.multiple_okay
					if v.inverse_property:
						inverse = v.inverse_property
						break

		try:
			current = getattr(self, which)
		except:
			current = None
		if not current:
			object.__setattr__(self, which, value)
		elif type(current) is list:
			current.append(value)
		else:
			if self._factory.validate_multiplicity and not multiple:
				raise ProfileError("Cannot append to %s on %s as multiplicity is 1" % (which, self._type))
			nvalue = [current, value]
			object.__setattr__(self, which, nvalue)

		if self._factory.materialize_inverses or self._factory.process_multiplicity:
			if not inversed and self._factory.materialize_inverses and inverse:
				# set the backwards ref		
				value._set_magic_resource(inverse, self, True)
			if type(current) is not list and multiple and self._factory.process_multiplicity:
				object.__setattr__(self, which, [getattr(self, which)])

	def _toJSON(self, done, top=None):
		"""Serialize as JSON."""
		# If we're already in the graph, return our URI only
		# This should only be called from the factory!

		d = self.__dict__.copy()
		del d['_factory']

		# Can't pass in self as a param
		if top is None:
			top = self

		# id, type, _label is the default.
		if not factory.id_type_label and id(self) in done:
			if self._factory.elasticsearch_compatible:
				return {'id': self.id}
			else:
				return self.id

		# In case of local contexts, not at the root
		# Shouldn't ever happen, but worth testing for
		if 'context' in d:
			d['@context'] = d['context']
			del d['context']

		# Check mandatory properties
		for e in self._required_properties:
			if e not in d:
				raise RequirementError("Resource type '%s' requires '%s' to be set" % (self._type, e), self)

		debug = self._factory.debug_level
		if debug.find("warn") > -1:
			for e in self._warn_properties:
				if e not in d:
					msg = "Resource type '%s' should have '%s' set" % (self._type, e)
					self._factory.maybe_warn(msg)

		# Add back context at the top, if set
		if top is self and self._factory.context_uri: 
			d['@context'] = self._factory.context_uri

		if (self._factory.id_type_label and id(self) in done) or (top is not self and not self._embed):
			# limit to only id, type, label
			nd = {}
			nd['id'] = d['id']
			if self.type:
				nd['type'] = self.type
			try:
				nd['_label'] = d['_label']
			except:
				pass
			d = nd
		else:	
			# otherwise, we're about to serialize the resource completely
			done[id(self)] = 1			

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

				# Should we do this at all? Could be outside of our API serialization scope
				if isinstance(v, ExternalResource):
					if self._factory.linked_art_boundaries and \
						not self._linked_art_boundary_okay(top, k, v):
						# never follow, so just add to done
						done[id(v)] = 1
					else:
						tbd.append(id(v))
				elif type(v) is list:
					for ni in v:
						if isinstance(ni, ExternalResource):
							if self._factory.linked_art_boundaries and \
								not self._linked_art_boundary_okay(top, k, ni):
								# never follow, so just add to done
								done[id(ni)] = 1							
							else:
								tbd.append(id(ni))
					# For completeness should check list-of-datetime here too
				elif isinstance(v, datetime.datetime):
					# replace with string
					kvs[k] = v.strftime("%Y-%m-%dT%H:%M:%SZ")

		for t in tbd:
			if not t in done:
				done[t] = id(self)
			
		for (k,v) in kvs:
			if v and (k[0] != "_" and not k in self._factory.underscore_properties):
				if isinstance(v, ExternalResource):
					if done[id(v)] == id(self):
						del done[id(v)]
					d[k] = v._toJSON(done=done, top=top)
				elif type(v) is list:
					newl = []
					for ni in v:
						if isinstance(ni, ExternalResource):
							if done[id(ni)] == id(self):
								del done[id(ni)]
							newl.append(ni._toJSON(done=done, top=top))
						else:
							# A number or string
							newl.append(ni)
					d[k] = newl				

		if self._factory.full_names:
			nd = {}
			# @context gets ganked by this renaming
			# so add it back in first.
			if top is self:
				nd['@context'] = self._factory.context_uri

			for (k,v) in d.items():
				# look up the rdf predicate in _properties
				for c in reversed(self._classhier):
					if k in c._all_properties:
						nk = c._all_properties[k].predicate
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
			# find class up that has a type and use its name
			# almost certainly the first one
			if self.type:
				d['type'] = self.type

			if self._factory.pipe_scoped_contexts:
				# XXX TODO This should be configurable not hard coded
				if 'part' in d:
					# Calculate which part
					for c in reversed(self._classhier):
						if 'part' in c._all_properties:
							nk = c._all_properties['part'].predicate
							d['part|%s' % nk]  = d['part']
							del d['part']
							break
				if 'part_of' in d:
					# Calculate which part
					for c in reversed(self._classhier):
						if 'part_of' in c._all_properties:
							nk = c._all_properties['part_of'].predicate
							d['part_of|%s' % nk]  = d['part_of']
							del d['part_of']
							break

		if self._factory.order_json:
			return OrderedDict(sorted(d.items(), key=lambda x: KOH.get(x[0], 1000)))
		else:
			return d

	def _linked_art_boundary_okay(self, top, prop, value):
		# Return false to say do not cross this boundary
		# Without replacement, just return True always
		return True

	def list_all_props(self, filter=None, okay=None):
		props = []
		for c in self._classhier:		
			for k,v in c._all_properties.items():
				if not k in props and \
					(not okay or okay and v.profile_okay) and \
					(filter is None or isinstance(filter, v.range) or \
						filter is v.range):
					props.append(k)
		props.sort()
		return props

	def list_my_props(self, filter=None):
		d = self.__dict__.copy()		
		props = []
		for (k,v) in d.items():
			if k[0] != "_" or k in self._factory.underscore_properties:
				# real property
				if filter:
					if isinstance(v, filter):
						props.append(k)
					elif isinstance(v, list):
						for i in v:
							if isinstance(i, filter):
								props.append(k)
								break
				else:
					props.append(k)		
		return props

	def allows_multiple(self, propName):
		""" Does propName allow multiple values on this class """
		for c in self._classhier:
			if propName in c._all_properties:
				v = c._all_properties[propName]
				return bool(v.multiple_okay)
		raise DataError("Cannot set '%s' on '%s'" % (propName, self.__class__.__name__))

# Ontology / Profile manipulation

def override_okay(clss, propName):
	""" set particular property on the class to be okay to use """
	pinfo = clss._all_properties.get(propName, None)
	if pinfo:
		npinfo = PropInfo(pinfo.property, pinfo.predicate, pinfo.range,
			pinfo.inverse_property, pinfo.inverse_predicate, 
			pinfo.multiple_okay, 1)
		clss._all_properties[propName] = npinfo
	else:
		raise DataError("%s does not have a %s property to allow" % 
			(clss.__name__, propName))

def cache_hierarchy():
	""" For each class, walk up the hierarchy and cache the terms """

	# This will work with the existing code, as it will find it in the first
	# test of props on classhier[0], the loop will just terminate straight away

	for c in factory._all_classes.values():
		new_hash = c._all_properties.copy()
		if len(c._classhier) > 1:
			for p in c._classhier[1:]:
				for (prop, info) in p._all_properties.items():
					if not prop in new_hash:
						new_hash[prop] = info
		c._all_properties = new_hash

# Ensure everything can have id, type, label and description
BaseResource._properties = {'id': {"rdf": "@id", "range": str, "okayToUse": 1}, 
	'type': {"rdf": "rdf:type", "range": str, "rangeStr": "rdfs:Class", "okayToUse": 1}, 
	'_label': {"rdf": "rdfs:label", "range": str, "rangeStr": "xsd:string", "okayToUse": 1}
}
BaseResource._all_properties = {
	'id': PropInfo('id', '@id', str, None, None, 0, 1),
	'type': PropInfo('type', 'rdf:type', str, None, None, 0, 1),
	'_label': PropInfo('_label', 'rdfs:label', str, None, None, 0, 1)
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
	c._all_properties = {}
	c._okayToUse = int(data['okay'])

	factory._all_classes[name] = c

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

		# can't guarantee all classes have been built at this stage :(
		c._properties[ccname] = {"rdf": "crm:%s" % name, 
			"rangeStr": rng,
			"inverseRdf": invRdf,
			"okayToUse": okay,
			"multiple": mult}
 
	# Build subclasses
	for s in data['subs']:
		build_class(s, c, vocabData)

def build_classes(fn=None, topClass=None):
	# Default to building our core dataset
	if not fn:
		dd = os.path.join(os.path.dirname(__file__), 'data')
		fn = os.path.join(dd, 'crm_vocab.tsv')
		topClass = 'E1_CRM_Entity'

	vocabData = process_tsv(fn)

	# Everything can have an id, a type, a label, a description
	build_class(topClass, BaseResource, vocabData)

	# And reset definitions now we have class objects
	for v in vocabData.values():
		c = v['class']
		if c is BaseResource:
			continue
		for (name, value) in c._properties.items():
			# recreate with namedtuple
			rngs = value.get('rangeStr', None)
			if not rngs:
				# Precomputed ones like rdf:type
				continue

			inverse = None
			rngd = vocabData.get(value['rangeStr'], None)
			if rngs in ['rdfs:Literal', 'xsd:dateTime', 'xsd:string', 'rdfs:Class']:
					rng = str 
			elif not rngd:
				raise ConfigurationError("Failed to get range for %s property %s - %s" % (c, name, rngs))
			else:
				rng = rngd['class']
				# and add inverse prop name from range
				for (ik, iv) in rng._properties.items():
					if iv['inverseRdf'] == value['rdf']:
						inverse = ik
						break

			c._all_properties[name] = PropInfo(name,
				value['rdf'], rng, inverse,
				value.get('inverseRdf', None),
				value.get('multiple', 1),
				value.get('okayToUse', 0)
			)

	# set all of the classhiers
	for v in vocabData.values():
		c = v['class']
		c._classhier = inspect.getmro(c)[:-1]
		try:
			del c._properties
		except:
			# Never had it set?
			pass




# XXX This should be invoked rather than inline so the module can be loaded
# and a different context used. But for now ...

# Build the factory first, so properties can be added to key_order
factory = CromulentFactory("http://lod.example.org/museum/", context="https://linked.art/ns/v1/linked-art.json")
build_classes()
# Need to then configure the boundary classes after they're created
