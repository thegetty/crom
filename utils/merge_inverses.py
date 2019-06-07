from lxml import etree
import codecs

NS = {'rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
	'xsd':"http://www.w3.org/2001/XMLSchema#",
	'rdfs':"http://www.w3.org/2000/01/rdf-schema#",
	'dcterms':"http://purl.org/dc/terms/",
	'owl':"http://www.w3.org/2002/07/owl#",
	'crm':"http://www.cidoc-crm.org/cidoc-crm/",
	'xml': "http://www.w3.org/XML/1998/namespace"
}

fh = file('data/inverses.xml')
data = fh.read()
fh.close()
dom = etree.XML(data)

inverses = {}
props = dom.xpath("//rdf:Property",namespaces=NS)
for p in props:
	name = p.xpath('@rdf:about', namespaces=NS)[0]
	try:
		inv = p.xpath('./owl:inverseOf/@rdf:resource', namespaces=NS)[0]
		inverses[name] = inv
	except:
		pass

fh = file('data/cidoc.xml')
data = fh.read()
fh.close()
dom = etree.XML(data)

# Now insert them into the right blocks

for (n,i) in inverses.items():
	try:
		elem = dom.xpath('//rdf:Property[@rdf:about="%s"]' % n, namespaces=NS)[0]
		if not elem.xpath('./owl:inverseOf', namespaces=NS):
			inv = etree.SubElement(elem, "{http://www.w3.org/2002/07/owl#}inverseOf")
			inv.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", i)
			inv.tail = "\n"
	except:
		print "Could not find property %s" % n


# And rewrite the file

fh = file('data/cidoc_inversed.xml', 'w')
fh.write(etree.tostring(dom, pretty_print=True))
fh.close()
