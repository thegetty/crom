from lxml import etree
import codecs
import json

default_key_order = 10000

# Order imposed by the library
# @context = 0, id = 1, rdf:type = 2
# rdfs:label = 5, rdf:value = 6, dc:description = 7

fh = file('../cromulent/data/key_order.json')
data = fh.read()
fh.close()
key_order_hash = json.loads(data)

# Allow configuration of overrides for the mapping of ontology to python/json
fh = file('../cromulent/data/overrides.json')
data = fh.read()
fh.close()
property_overrides = json.loads(data)

# Allow subsetting of CRM into in-use / not-in-use to enable the library
# to warn on instantiation of not-in-use properties or classes
fh = file('crm-profile.json')
data = fh.read()
fh.close()
profile_flags = json.loads(data)


NS = {'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	'xsd':"http://www.w3.org/2001/XMLSchema#",
	'rdfs':"http://www.w3.org/2000/01/rdf-schema#",
	'dcterms':"http://purl.org/dc/terms/",
	'owl':"http://www.w3.org/2002/07/owl#",
	'crm':"http://www.cidoc-crm.org/cidoc-crm/",
	'xml': "http://www.w3.org/XML/1998/namespace"
}

fh = file('cidoc_inverse.xml')
data = fh.read()
fh.close()
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

	useflag = str(profile_flags.get(name, 0))
	stuff.append([name, "class", ccname, label, comment, subCls, useflag])

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
	useflag = str(profile_flags.get(name, 0))
	stuff.append([name, "property", ccname, label, comment, subProp, domn, rang, inverse, koi, useflag])

outdata = '\n'.join(['\t'.join(x) for x in stuff])
fh = codecs.open('../cromulent/data/crm_vocab.tsv', 'w', 'utf-8')
fh.write(outdata)
fh.close()
