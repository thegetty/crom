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
names = []
inverses = {}

props = dom.xpath("//rdf:Property",namespaces=NS)
for p in props:
	name = p.xpath('@rdf:about', namespaces=NS)[0]
	names.append(name)

for p in props:
	name = p.xpath('@rdf:about', namespaces=NS)[0]	
	fu = name.find('_')
	pid = name[:fu]
	if pid[-1] in ['a', 'b']:
		# No inverses for botb eote
		continue
	inverse = ""
	if pid[-1] == "i":
		pid = pid[:-1]
	else:
		pid = pid + "i"
	pid += "_"

	for i in names:
		if i.startswith(pid) and i != name:
			inverse = i
			break
	if inverse:
		inverses[name] = inverse

# Now print ONLY the inverses
outlines = [
'<rdf:RDF xml:lang="en" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xml:base="http://www.cidoc-crm.org/cidoc-crm/" xmlns:la="http://linked.art/ns/terms/">'
]

for n in names:
	if n in inverses:
		outlines.append('  <rdf:Property rdf:about="%s">' % n )
		outlines.append('    <owl:inverseOf rdf:resource="%s"/>' % inverses[n])
		outlines.append('  </rdf:Property>')
outlines.append('</rdf:RDF>')
outstr = '\n'.join(outlines)

fh = file('data/inverses.xml', 'w')
fh.write(outstr)
fh.close()
