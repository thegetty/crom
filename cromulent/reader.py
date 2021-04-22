from cromulent import model, vocab
from cromulent.model import factory, DataError, OrderedDict, BaseResource
from cromulent.model import STR_TYPES

import json

class Reader(object):

	def __init__(self):
		self.uri_object_map = {}
		self.forward_refs = []
		self.vocab_props = ['assigned_property']

	def read(self, data):
		if not data:
			raise DataError("No data provided: %r" % data)
		elif type(data) in STR_TYPES:
			try:
				data = json.loads(data)
			except:
				raise DataError("Data is not valid JSON")
		if not data:
			raise DataError("No Data provided")
		self.uri_object_map = {}
		self.forward_refs = []
		try:
			what = self.construct(data)
			self.process_forward_refs()
			self.uri_object_map = {}
			self.forward_refs = []
			return what
		except:
			raise

	def process_forward_refs(self):
		for (what, prop, uri) in self.forward_refs:
			if uri in self.uri_object_map:
				setattr(what, prop, self.uri_object_map[uri])
			else:
				raise NotImplementedError("No class information for %s.%s = %s".format(what, prop, uri))

	def construct(self, js):
		# pass in json, get back object
		if '@context' in js:
			del js['@context']

		ident = js.get('id', '')
		typ = js.get('type', None)
		try:
			del js['id']
		except:
			# blank node
			pass
		try:
			del js['type']
		except:
			# external resource with properties but no class
			pass

		if typ == None:
			clx = BaseResource
		else:
			# Get class based on name
			try:
				clx = getattr(model, typ)
			except AttributeError:
				# No such class
				raise DataError("Resource %s has unknown class %s" % (ident, typ) )

		# now check vocab.ext_classes to try and refine
		if 'classified_as' in js:
			trash = None 
			for c in js['classified_as']:
				i = c['id'] if hasattr(c, 'id') else ''
				for cx in dir(vocab):
					what = getattr(vocab, cx)
					# crying cat face -- type as a @property returns the function, not the value
					# when calling it on a class rather than an instance
					try:
						mytype = what._classhier[0].__name__
					except AttributeError:
						continue
					if  (cx[0].isupper() and not hasattr(model, cx) and type(what) == type) and \
						(typ is None or mytype == typ) and \
						(i in [x.id for x in what._classification]):
						clx = what
						# Trash the classification
						trash = c
						break
				if trash is not None:
					break
			if trash is not None:
				js['classified_as'].remove(trash)

		what = clx(ident=ident)
		self.uri_object_map[ident] = what
		propList = what.list_all_props()

		# sort data by KOH to minimize chance of bad backrefs
		itms = list(js.items())
		itms.sort(key=lambda x: factory.key_order_hash.get(x[0], 10000))

		for (prop, value) in itms:
			if not prop in propList:
				raise DataError("Unknown property %s on %s" % (prop, clx.__name__))

			# Climb looking for range
			for c in what._classhier:		
				if prop in c._all_properties:
					rng = c._all_properties[prop].range
					break

			if type(value) != list:
				value = [value]
			for subvalue in value:
				if rng == str:
					setattr(what, prop, subvalue)				
				elif type(subvalue) == dict or isinstance(subvalue, OrderedDict):
					# recurse ...
					val = self.construct(subvalue)
					setattr(what, prop, val)
				elif type(subvalue) in STR_TYPES and prop in self.vocab_props:
					# keep as string
					setattr(what, prop, subvalue)
				elif type(subvalue) in STR_TYPES:
					# raw URI to be made into a class of type rng
					# or back reference
					if subvalue in self.uri_object_map:
						setattr(what, prop, self.uri_object_map[subvalue])
					elif rng in [model.Type, BaseResource]:
						# Always a X, often no more info
						setattr(what, prop, rng(ident=subvalue))
					else:
						self.forward_refs.append([what, prop, subvalue])
				else:
					# No idea!!
					raise DataError("Value %r is not expected for %s" % (subvalue, prop))

		return what


