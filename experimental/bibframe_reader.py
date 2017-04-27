from lxml import etree
import codecs
import json

default_key_order = 10000

NS = {'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	'xsd':"http://www.w3.org/2001/XMLSchema#",
	'rdfs':"http://www.w3.org/2000/01/rdf-schema#",
	'dcterms':"http://purl.org/dc/terms/",
	'owl':"http://www.w3.org/2002/07/owl#",
	'crm':"http://www.cidoc-crm.org/cidoc-crm/",
	'skos':"http://www.w3.org/2004/02/skos/core#",
	'xml': "http://www.w3.org/XML/1998/namespace"
}

fh = file('bibframe.rdf')
data = fh.read()
fh.close()
dom = etree.XML(data)
stuff = []

property_overrides = {}

classes = dom.xpath("//rdfs:Class", namespaces=NS)

if not classes:
	classes = dom.xpath('//owl:Class', namespaces=NS)

for c in classes:
	label = c.xpath('./rdfs:label/text()', namespaces=NS)[0]
	try:
		comment = c.xpath('./rdfs:comment/text()', namespaces=NS)
		if not comment:
			comment = c.xpath('./skos:definition/text()', namespaces=NS)
		if comment:
			comment = comment[0]
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

	uc1 = name.rfind("/")
	ccname = name[uc1+1:]
	ccname = ccname.replace("_or_", "_Or_").replace("_of_", "_Of_")
	ccname = ccname.replace('-', '').replace('_', '')

	stuff.append([name, "class", ccname, label, comment, subCls])

props = dom.xpath("//rdf:Property",namespaces=NS)
if not props:
	props = dom.xpath('//owl:DatatypeProperty', namespaces=NS)
	props.extend(dom.xpath('owl:ObjectProperty', namespaces=NS))

for p in props:
	label = p.xpath('./rdfs:label/text()', namespaces=NS)[0]
	try:
		comment = p.xpath('./rdfs:comment/text()', namespaces=NS)
		if not comment:
			comment = c.xpath('./skos:definition/text()', namespaces=NS)
		if comment:
			comment = comment[0]
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

	# koi = str(key_order_hash.get(ccname, default_key_order))
	koi = "10000"
	stuff.append([name, "property", ccname, label, comment, subProp, domn, rang, inverse, koi])

outdata = '\n'.join(['\t'.join(x) for x in stuff])
fh = codecs.open('bibframe_vocab.tsv', 'w', 'utf-8')
fh.write(outdata)
fh.close()
