
import sys, argparse
from cromulent import model, vocab
factory = model.factory

factory.cache_hierarchy()

parser = argparse.ArgumentParser()
parser.add_argument('what')
parser.add_argument('--okay', dest="okay", type=bool)
parser.add_argument('--filter', dest="filter")
args = parser.parse_args()

def list_all_props(what, filter=None, okay=None):
	props = []
	for k,v in c._all_properties.items():
		if not k in props and \
			(not okay or okay and v.profile_okay) and \
			(filter is None or isinstance(filter, v.range) or \
				filter is v.range):
			props.append(v)
	props.sort(key=lambda x: x.property)
	return props


what = args.what
try:
	c = getattr(model, what)
except:
	try:
		c = getattr(vocab, what)
	except:
		print(f"Unknown model or vocab class: {what}")
		sys.exit(1)

if args.filter:
	try:
		cf = getattr(model, args.filter)
		f = cf()
	except:
		f = None
else:
	cf = None
	f = None


print(f"Main Class: {c.__name__}")
if cf:
	print(f"Filtered To: {cf.__name__}")
else:
	print("Filtered To: None")
print(f"Using Profile: {args.okay}")

instance = c()
ap = list_all_props(c, okay=args.okay, filter=f)

for pi in ap:
	if pi.property in ['close_match', 'exact_match']:
		continue
	print(f"<{what}>  {pi.property} ({pi.predicate}) / {pi.inverse_property} ({pi.inverse_predicate})  <{pi.range.__name__}> ")

