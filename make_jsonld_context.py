# make_jsonld_context

import codecs
import json

try:
    from collections import OrderedDict
except:
    try:
        from ordereddict import OrderedDict
    except:
        raise Exception("To run with old pythons you must: easy_install ordereddict")


fn='build_tsv/crm_vocab.tsv'
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

context['id'] = {"@id": "@id", "@type": "@id"}
context['type'] = {"@id": "@type", "@type": "@id"}

for l in lines:
	l = l[:-1] # chomp
	info= l.split('\t')
	name = info[0]	
	if info[1] == "class":
		# map json key to ontology for @type:@vocab
		ctname = info[2]
		context[ctname] = "crm:%s" % name
	else:
		ctname = info[2]
		rng = info[7]
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
			context[ctname] = {"@id": "crm:%s" % name, "@type": typ} 

# Language Map:
# "@container": "@language"

context['label'] = {"@id": "rdfs:label"}
context['value'] = {"@id": "rdf:value"}
context['description'] = {"@id": "dc:description"}
context['height'] = {"@id": "schema:height", "@type": "@id"}
context['width'] = {"@id": "schema:width", "@type": "@id"}
context['familyName'] = {"@id": "schema:familyName"}
context['givenName'] = {"@id": "schema:givenName"}
context['nationality'] = {"@id": "schema:nationality", "@type": "@id"}
context['culture'] = {"@id": "schema:genre"}

outstr = json.dumps(context, indent=2)

fh = file("crm_context.jsonld", 'w')
fh.write(outstr)
fh.close()


