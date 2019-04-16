
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
lines = fh.readlines()[1:] # Chomp header line
fh.close()

context = OrderedDict()
context['@version'] = 1.1
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

## These are only aliases. The processing is defined by the spec.
context['id'] = "@id"
context['type'] = "@type"

extension = OrderedDict()
extension['@version'] = 1.1
extension['crm'] = "http://www.cidoc-crm.org/cidoc-crm/"


parts = {
	"P9": ["crm:P9_consists_of", "crm:P9i_forms_part_of"],
	"P46": ["crm:P46_is_composed_of", "crm:P46i_forms_part_of"],
	"P106": ["crm:P106_is_composed_of", "crm:P106i_forms_part_of"],
	"P86": ["crm:P86i_contains", "crm:P86_falls_within"],
	"P89": ["crm:P89i_contains", "crm:P89_falls_within"],
	"skos": ["skos:narrower", "skos:broader"],
	"P148": ["crm:P148_has_component", "crm:P148i_is_component_of"],
	"interest": ["la:interest_part", "la:interest_part_of"],
	"set": ["la:has_member", "la:member_of"],
	"P107": ["crm:P107_has_current_or_former_member", "crm:P107i_is_current_or_former_member_of"]
}

scoped_classes = {
	"Activity": "P9",
	"Acquisition": "P9",
	"TransferOfCustody": "P9",
	"Production": "P9",
	"AttributeAssignment": "P9",		
	"ManMadeObject": "P46",
	"LinguisticObject": "P106",
	"VisualItem": "P106", # XXX This is the symbolic partitioning, not the conceptual partitioning of P149
	"Identifier": "P106",
	"TimeSpan": "P86",
	"Place": "P89",
	"Type": "skos",
	"Language": "skos",
	"Material": "skos",
	"MeasurementUnit": "skos",
	"BeginningOfExistence": "P9",
	"EndOfExistence": "P9",
	"Creation": "P9",
	"Formation": "P9",
	"InformationObject": "P106",
	"Transformation": "P9",
	"Joining": "P9",
	"Leaving": "P9",
	"PropositionalObject": "P148",
	"Currency": "skos",
	"Payment": "P9",
	"PropertyInterest": "interest",
	"Name": "P106",
	"Birth": "P9",
	"Death": "P9",
	"Event": "P9",
	"Destruction": "P9",
	"Move": "P9",
	"Modification": "P9",
	"Dissolution": "P9",
	"Period": "P9",
	"PhysicalThing": "P46",
	"PhysicalObject": "P46",
	"PhysicalFeature": "P46",
	"BiologicalObject": "P46",
	"Site": "P46",
	"PhysicalManMadeThing": "P46",
	"ManMadeFeature": "P46",
	"Title": "P106",
	"Inscription": "P106",
	"Mark": "P106",
	"Appellation": "P106",
	"PartAddition": "P9",
	"PartRemoval": "P9",
	"SymbolicObject": "P106",
	"Purchase": "P9",
	"Set": "set",
	"Group": "P107"
}


for l in lines:
	l = l[:-1] # chomp
	info= l.split('\t')
	name = info[0]	
	if info[1] == "class":
		# map json key to ontology for @type:@vocab
		ctname = info[2]
		if name.startswith("E"):
			name = "crm:%s" % name		
		context[ctname] = {"@id": name}
		if ctname in scoped_classes:
			part = parts[scoped_classes[ctname]][0]
			part_of = parts[scoped_classes[ctname]][1]
			if scoped_classes[ctname] in ['set', 'P107']:
				context[ctname]['@context'] = {
					"member": {"@id": part, "@type": "@id", "@container": "@set"},
					"member_of": {"@id": part_of, "@type": "@id", "@container": "@set"}
				}
			else:
				context[ctname]['@context'] = {
					"part": {"@id": part, "@type": "@id", "@container": "@set"},
					"part_of": {"@id": part_of, "@type": "@id", "@container": "@set"}
				}
	else:
		ctname = info[2]
		write = not ctname in ['part', 'part_of', 'member', 'member_of']
		# These need to be added correctly to all parents in the ontology
		# ... as above

		dmn = info[6]
		rng = info[7]
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

			if name.startswith("P"):
				name = "crm:%s" % name

			if write:
				if typ in ["rdfs:Literal", "xsd:string"]:
					context[ctname] = {"@id": name}
				elif mult == '1':
					context[ctname] = {"@id": name, "@type": typ, "@container":"@set"}
				else:
					context[ctname] = {"@id": name, "@type": typ}

			# Otherwise, we're part / part_of, so ignore
			# print "scoped context: %s: %s on %s" % (ctname, name, dmn)

ctxt = {"@context": context}

outstr = json.dumps(ctxt, indent=2)
fh = file("../cromulent/data/linked-art.json", 'w')
fh.write(outstr)
fh.close()
