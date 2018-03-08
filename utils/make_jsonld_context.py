
import codecs
import json

try:
    from collections import OrderedDict
except:
    try:
        from ordereddict import OrderedDict
    except:
        raise Exception("To run with old pythons you must: easy_install ordereddict")


fn = '../cromulent/data/crm_vocab.tsv'
fh = codecs.open(fn, 'r', 'utf-8')
lines = fh.readlines()
fh.close()

context = OrderedDict()
context['crm'] = "http://www.cidoc-crm.org/cidoc-crm/"
context['rdf'] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
context['rdfs'] = "http://www.w3.org/2000/01/rdf-schema#"
context['dc'] = "http://purl.org/dc/elements/1.1/"
context['dcterms'] = "http://purl.org/dc/terms/"
context['schema'] = "http://schema.org/"
context['skos'] = "http://www.w3.org/2004/02/skos/core#"
context['foaf'] = 'http://xmlns.com/foaf/0.1/'
context['xsd'] = "http://www.w3.org/2001/XMLSchema#"
context["la"] = "https://linked.art/ns/terms/"
context["aat"]  = "http://vocab.getty.edu/aat/"
context["ulan"] = "http://vocab.getty.edu/ulan/"
context["tgn"] = "http://vocab.getty.edu/tgn/"

## These are only aliases. The processing is defined by the spec.
context['id'] = "@id"
context['type'] = "@type"

extension = OrderedDict()
extension['crm'] = "http://www.cidoc-crm.org/cidoc-crm/"

for l in lines:
	l = l[:-1] # chomp
	info= l.split('\t')
	name = info[0]	
	if info[1] == "class":
		# map json key to ontology for @type:@vocab
		ctname = info[2]
		used = info[-1]
		if name.startswith("E"):
			name = "crm:%s" % name
		# split into used and other
		if used == "1":			
			context[ctname] = name
		else:
			extension[ctname] = name
	else:
		ctname = info[2]
		rng = info[7]
		used = info[-2]
		mult = info[11] or '1'
		if context.has_key(ctname):
			print "Already found: %s   (%s vs %s)" % (ctname, context[ctname]['@id'], name)
		else:
			if rng:
				if rng[0] == "E":
					typ = "@id"
				else:
					typ = rng
			else:
				typ = "@id"
			which = context if used == "1" else extension

			if name.startswith("P"):
				name = "crm:%s" % name

			if typ in ["rdfs:Literal", "xsd:dateTime", "xsd:string"]:
				which[ctname] = {"@id": name}
			elif mult == '1':
				which[ctname] = {"@id": name, "@type": typ, "@container":"@set"}
			else:
				which[ctname] = {"@id": name, "@type": typ}

ctxt = {"@context": context}
xctxt = {"@context": extension}

outstr = json.dumps(ctxt, indent=2)
fh = file("../cromulent/data/linked-art.json", 'w')
fh.write(outstr)
fh.close()

outstr = json.dumps(xctxt, indent=2)
fh = file("../cromulent/data/cidoc-extension.json", 'w')
fh.write(outstr)
fh.close()
