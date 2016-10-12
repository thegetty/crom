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

names = []

props = dom.xpath("//rdf:Property",namespaces=NS)
for p in props:
	name = p.xpath('@rdf:about', namespaces=NS)[0]
	names.append(name)

for p in props:
	name = p.xpath('@rdf:about', namespaces=NS)[0]	
	fu = name.find('_')
	pid = name[:fu]
	if pid[-1] == "i":
		pid = pid[:-1]
	if pid[-1] in ['a', 'b']:
		# No inverses for botb eote
		continue
	inverse = ""
	for i in names:
		if i.startswith(pid) and i != name:
			inverse = i
			break

	# add an element: <owl:inverseOf rdf:resource="name"/>
	owl = etree.Element("{%s}inverseOf" % NS['owl'], nsmap={'owl':NS['owl']})
	owl.set("{%s}resource" % NS['rdf'], inverse)
	p.append(owl)

# Now pretty print dom
outstr = etree.tostring(dom, pretty_print=True)
outstr = outstr.replace("\n<owl:", "\n    <owl:")
outstr = outstr.replace("/></rdf:Property", "/>\n</rdf:Property")
fh = file('cidoc_inverse.xml', 'w')
fh.write(outstr)
fh.close()
