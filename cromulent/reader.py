from . import model
from .model import factory, DataError, OrderedDict
from .extra import EoEActivity, Payment

def read(data):
	if not data:
		raise DataError("No data provided: %r" % data)
	elif type(data) in [str, unicode]:
		try:
			data = json.loads(data)
		except:
			raise DataError("Data is not valid JSON")
	return construct(data)

def construct(js):
	# pass in json, get back object
	if '@context' in js:
		del js['@context']

	ident = js.get('id', '')
	typ = js.get('type', None)
	del js['id']
	del js['type']

	if not typ:
		raise DataError("Resource does not have a type set %s" % ident)
	if type(typ) == list:
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
	propInfo = what._list_all_props()

	for (prop, value) in js.items():
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
				val = construct(subvalue)
				setattr(what, prop, val)
			elif type(subvalue) in [str, unicode]:
				# raw URI to be made into a class of type rng
				val = rng(ident=subvalue)
				setattr(what, prop, val)
			else:
				# No idea!!
				raise DataError("Value %r is not expected for %s" % (subvalue, prop))

	return what

