from cromulent import model
from cromulent.model import factory, DataError, OrderedDict, BaseResource
from cromulent.model import STR_TYPES
from cromulent.multiple_instantiation import EoEActivity
import json

class Reader(object):

	def __init__(self):
		self.uri_object_map = {}
		self.forward_refs = []

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
		elif type(typ) == list:
			if set(typ) == set(["EndOfExistence", "Activity"]):
				clx = EoEActivity
			else:
				raise NotImplementedError("Not sure which of multiple classes to use!")
		else:
			# Get class based on name
			# Not bothering with vocab based classes (yet)
			if typ == "Payment":
				clx = Payment
			else:
				try:
					clx = getattr(model, typ)
				except AttributeError:
					# No such class
					raise DataError("Resource %s has unknown class %s" % (ident, typ) )

		classified = js.get('classfied_as', [])
		what = clx(ident=ident)
		self.uri_object_map[ident] = what
		propInfo = what._list_all_props()

		# sort data by KOH to minimize chance of bad backrefs
		itms = list(js.items())
		itms.sort(key=lambda x: factory.key_order_hash.get(x[0], 10000))

		for (prop, value) in itms:
			# Make everything a list, even if it can't be one
			rng = propInfo.get(prop, None)
			if not rng:
				raise DataError("Unknown property %s" % prop)
	 
			if type(value) != list:
				value = [value]
			for subvalue in value:
				if rng == str:
					setattr(what, prop, subvalue)				
				elif type(subvalue) == dict or isinstance(subvalue, OrderedDict):
					# recurse ...
					val = self.construct(subvalue)
					setattr(what, prop, val)
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
