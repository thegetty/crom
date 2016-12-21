from lxml import etree
import codecs

fh = file('cidoc_inverse.xml')
data = fh.read()
fh.close()

default_key_order = 10000

# Order imposed by the library
# @context = 0, id = 1, rdf:type = 2
# rdfs:label = 5, rdf:value = 6, dc:description = 7

key_order_hash = {
	"classified_as": 3,  
	"identified_by": 10,

	"carried_out_by": 18, 
	"used_specific_object": 19,
	"timespan": 20, 
	"begin_of_the_begin": 21, 
	"end_of_the_begin": 22, 
	"begin_of_the_end": 23, 
	"end_of_the_end": 24,
	"started_by": 25, 
	"finished_by": 28,

	"transferred_title_of": 50, 
	"transferred_title_from": 51, 
	"transferred_title_to": 52,
	"sales_price": 49,
	"consists_of": 100, 
	"composed_of": 101
 }



if True:
	property_overrides = {
		"P45": "made_of",
		"P7i": "location_of",
		"P5": "subState",
		"P5i": "subState_of",
		"P20i": "specific_purpose_of",
		"P42": "assigned_type",
		"P42i": "type_assigned_by",
		"P37": "assigned_identifier",
		"P37i": "identifier_assigned_by",

		# P9 - consists_of
		# P9i - forms_part_of
		"P46": "part",
		"P46i": "part_of",
		"P86": "temporally_within",
		"P86i": "temporally_contains",
		"P89": "spatially_within",
		"P89i": "spatially_contains",
		# P106 - composed_of
		"P106i": "composed_from",

		"P78": "time_identified_by",
		"P78i": "identifies_time",
		"P87": "place_identified_by",
		"P87i": "identifies_place",
		"P131": "actor_identified_by",
		"P131i": "identifies_actor",
		"P149": "concept_identified_by",
		"P149i": "identifies_concept",
		"P35i": "condition_identified_by",

		"P90": "has_value", # to avoid collision with rdf:value,
		"P2": "classified_as", # to avoid collision with rdf:type

		"P133": "distinct_from",
		"P164i": "timespan_of_presence",

		"P151i": "participated_in_formation",
		"P165i": "included_in",
		"P132": "volume_overlaps_with",
		"P135i": "type_created_by"
	}
else:
	property_overrides = {}

NS = {'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	'xsd':"http://www.w3.org/2001/XMLSchema#",
	'rdfs':"http://www.w3.org/2000/01/rdf-schema#",
	'dcterms':"http://purl.org/dc/terms/",
	'owl':"http://www.w3.org/2002/07/owl#",
	'crm':"http://www.cidoc-crm.org/cidoc-crm/",
	'xml': "http://www.w3.org/XML/1998/namespace"
}

dom = etree.XML(data)
stuff = []

classes = dom.xpath("//rdfs:Class", namespaces=NS)

for c in classes:
	label = c.xpath('./rdfs:label[@xml:lang="en"]/text()', namespaces=NS)[0]
	try:
		comment = c.xpath('./rdfs:comment/text()', namespaces=NS)[0]
		comment = comment.strip()
		comment = comment.replace('\n', '\\n').replace('\t', ' ')
	except:
		comment = ""
	name = c.xpath('@rdf:about', namespaces=NS)[0]

	subCls = c.xpath('./rdfs:subClassOf/@rdf:resource', namespaces=NS)
	if subCls:
		# could be multiples
		subCls = '|'.join(subCls)
	else:
		subCls = ""

	uc1 = name.find("_")
	ccname = name[uc1+1:]
	ccname = ccname.replace("_or_", "_Or_").replace("_of_", "_Of_")
	ccname = ccname.replace('-', '').replace('_', '')

	stuff.append([name, "class", ccname, label, comment, subCls])

props = dom.xpath("//rdf:Property",namespaces=NS)
for p in props:
	label = p.xpath('./rdfs:label[@xml:lang="en"]/text()', namespaces=NS)[0]
	try:
		comment = p.xpath('./rdfs:comment/text()', namespaces=NS)[0]
		comment = comment.strip()
		comment = comment.replace('\n', '\\n').replace('\t', ' ')
	except:
		comment = ""
	name = p.xpath('@rdf:about', namespaces=NS)[0]
	domn = p.xpath('./rdfs:domain/@rdf:resource', namespaces=NS)
	if domn:		
		domn = domn[0]
		for (k,v) in NS.items():
			domn = domn.replace(v,"%s:" % k)
	else:
		domn = ""
	rang = p.xpath('./rdfs:range/@rdf:resource', namespaces=NS)
	if rang:
		rang = rang[0]
		for (k,v) in NS.items():
			rang = rang.replace(v,"%s:" % k)
	else:
		rang = ""
	subProp = p.xpath('./rdfs:subPropertyOf/@rdf:resource', namespaces=NS)
	if subProp:
		subProp = subProp[0]
	else:
		subProp = ""

	inverse = p.xpath('./owl:inverseOf/@rdf:resource', namespaces=NS)
	if inverse:
		inverse = inverse[0]
	else:
		inverse = ""

	uc1 = name.find("_")
	pno = name[:uc1]
	if property_overrides.has_key(pno):
		ccname = property_overrides[pno]
	else:
		ccname = name[uc1+1:]
		ccname = ccname.replace("-", "")
		if ccname.startswith("is_"):
			ccname = ccname[3:]
		elif ccname.startswith("has_") or ccname.startswith("had_") or ccname.startswith("was_"):
			ccname = ccname[4:]

	koi = str(key_order_hash.get(ccname, default_key_order))
	stuff.append([name, "property", ccname, label, comment, subProp, domn, rang, inverse, koi])

outdata = '\n'.join(['\t'.join(x) for x in stuff])
fh = codecs.open('../cromulent/data/crm_vocab.tsv', 'w', 'utf-8')
fh.write(outdata)
fh.close()
