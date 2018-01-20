
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
		if not name.startswith("la:"):
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

			if typ in ["rdfs:Literal", "xsd:dateTime"]:
				which[ctname] = {"@id": "crm:%s" % name}
			elif mult == '1':
				which[ctname] = {"@id": "crm:%s" % name, "@type": typ, "@container":"@set"}
			else:
				which[ctname] = {"@id": "crm:%s" % name, "@type": typ}

# Language Map:   label, has_note, description  ?
# "@container": "@language"

context['label'] = {"@id": "rdfs:label"}
context['value'] = {"@id": "rdf:value"}
context['description'] = {"@id": "dc:description", "@container": "@set"}
context['style'] = {"@id": "schema:genre", "@type": "@id", "@container": "@set"}
context['conforms_to'] = {'@id': "dcterms:conformsTo", "@type": "@id"}
context['format'] = {"@id": "dc:format"}
context['exact_match'] = {"@id": "skos:exactMatch", "@type": "@id", "@container": "@set"}
context['close_match'] = {"@id": "skos:closeMatch", "@type": "@id", "@container": "@set"}
context['related'] = {"@id": "dcterms:relation", "@type": "@id", "@container": "@set"}
context['subject'] = {"@id": "dcterms:subject", "@type": "@id", "@container": "@set"}

# Add in Provenance extension 
context["Payment"] = "la:Payment"
context["paid_from"] = {
      "@id": "la:paid_from",
      "@type": "@id",
      "@container": "@set"
    }
context["paid_to"] = {
      "@id": "la:paid_to",
      "@type": "@id",
      "@container": "@set"
    }
context["paid_amount"] = {
      "@id": "la:paid_amount",
      "@type": "@id",
      "@container": "@set"
    }

context["LegalClaim"] = "la:LegalClaim"

context['instantiates'] = {
	"@id": "la:instantiates",
	"@type": "@id"
}
context['jurisdiction'] = {
	"@id": "la:jurisdiction",
	"@type": "@id"
}
context['claimed_by'] = {
	"@id": "la:claimed_by",
	"@type": "@id",
	"@container": "@set"
}

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
