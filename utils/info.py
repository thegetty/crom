
import sys, argparse
from cromulent import model, vocab

parser = argparse.ArgumentParser()
parser.add_argument('what')
parser.add_argument('--okay', '--profile', dest="okay", type=bool)
parser.add_argument('--filter', dest="filter")
args = parser.parse_args()

def list_all_props(what, filter=None, okay=None):
	props = []
	ks = []
	for c in what._classhier:	
		for k,v in c._all_properties.items():
			if not k in ks and \
				(not okay or (okay and v.profile_okay)) and \
				(filter is None or isinstance(filter, v.range) or \
					filter is v.range):
				props.append(v)
				ks.append(k)
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


print(f"Main Class: \033[95m{c.__name__}\033[0m")
if cf:
	print(f"Filtered To: \033[95m{cf.__name__}\033[0m")
else:
	print("Filtered To: None")
print(f"Using Profile: {args.okay}")

instance = c()
ap = list_all_props(instance, okay=args.okay, filter=f)

ap2 = instance.list_all_props(okay=args.okay, filter=f)


for pi in ap:
	if pi.property in ['close_match', 'exact_match']:
		continue
	out = f"{pi.property} ({pi.predicate})"
	if pi.inverse_property:
		inv = f"{pi.inverse_property} ({pi.inverse_predicate})"
	else:
		inv = ""
	if pi.range == str:
		rng = "\033[93mLiteral"
	else:
		rng = pi.range.__name__
	# old skool colorizing
	print(f"\033[95m{what:<15} \033[92m{out:<50} / {inv:<50} \033[95m{rng}\033[0m")

