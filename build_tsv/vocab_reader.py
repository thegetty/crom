from lxml import etree
import codecs

fh = file('cidoc.xml')
data = fh.read()
fh.close()

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
		subProp = subProp[0].replace('http://bibframe.org/vocab/', '')
	else:
		subProp = ""

	uc1 = name.find("_")
	ccname = name[uc1+1:]
	ccname = ccname.replace("-", "")
	stuff.append([name, "property", ccname, label, comment, subProp, domn, rang])

outdata = '\n'.join(['\t'.join(x) for x in stuff])
fh = codecs.open('crm_vocab.tsv', 'w', 'utf-8')
fh.write(outdata)
fh.close()
