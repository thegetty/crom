
import json
from cidoc_orm import factory, TimeSpan, ManMadeObject, Type, Identifier, \
	Production, Person, Place, Group, Material, Type, Mark, Right, Document, \
	Activity
import re

# Meta meta
ext_classes = {
	"TMSNumber": {"parent": Identifier, "vocab": "aat", "id": "300404621"},	
	"AccessionNumber": {"parent": Identifier, "vocab": "aat", "id": "300312355"},	
	"Inscription": {"parent": Mark, "vocab": "aat", "id": "300028702"},
	"Signature": {"parent": Mark, "vocab": "aat", "id": "300028705"},
	"Exhibition": {"parent": Activity, "vocab": "aat", "id": "300054766"},
	"Painting": {"parent": ManMadeObject, "vocab": "aat", "id": "300033618"},
	"Sculpture": {"parent": ManMadeObject, "vocab": "aat", "id": "300047090"},
	"Drawing": {"parent": ManMadeObject, "vocab": "aat", "id": "300033973"},
	"Miniature": {"parent": ManMadeObject, "vocab": "aat", "id": "300033936"},
	"Tapestry": {"parent": ManMadeObject, "vocab": "aat", "id": "300205002"},
	"Furniture": {"parent": ManMadeObject, "vocab": "aat", "id": "300037680"},
	"Mosaic": {"parent": ManMadeObject, "vocab": "aat", "id": "300015342"},
	"Photograph": {"parent": ManMadeObject, "vocab": "aat", "id": "300046300"},
	"Drawing": {"parent": ManMadeObject, "vocab": "aat", "id": "300033973"},
	"Coin": {"parent": ManMadeObject, "vocab": "aat", "id": "300037222"},
	"Vessel": {"parent": ManMadeObject, "vocab": "aat", "id": "300193015"},
	"PhotographPrint": {"parent": ManMadeObject, "vocab": "aat", "id": "300127104"},
	"PhotographAlbum": {"parent": ManMadeObject, "vocab": "aat", "id": "300026695"},
	"PhotographBook": {"parent": ManMadeObject, "vocab": "aat", "id": "300265728"}
}

# Jewelry
# Text Book Album
# Implement

# Note many sub types of Vessels, including
# Bowl, Flask, Beaker, Cup, Jar, Amphora, 

for (name,v) in ext_classes.items():
	c = type(name, (v['parent'],), {})
	c._p2_has_type = "http://vocab.getty.edu/%s/%s" % (v['vocab'], v['id'])
	globals()[name] = c

aat_type_mapping = {
	"Painting": Painting,
	"Paintings": Painting,
	"Drawing": Drawing,
	"Furniture": Furniture,
	"Coin": Coin,
	"Sculpture": Sculpture,
	"Vessels": Vessel
}

#	"panel": "300014657"  # A wooden support

aat_part_mapping = {
	"supports": "300014844"  # The thing that is painted on
}

aat_material_mapping = {
	"watercolor": "300015045",
	"oil": "300015050",
	"tempera": "300015062",
	"canvas": "300014078",
	"oak": "300012264",
	"gold leaf": "300264831",
	"paper": "300014109",
	"copper": "300011020",
	"terracotta": "300010669",
	"glass": "300010797",
	"chalk": "300011727",
	"bronze": "300010957",
	"marble": "300011443",
	"albumen silver print": "300127121",
	"gelatin silver print": "300128695",
	"silver": "300011029"
}

aat_culture_mapping = {
	"french": "300111188",
	"italian": "300111198",
	"german": "300111192",
	"dutch": "300020929"
}

dim_type_mapping = {
	"height": "300055644",
	"width": "300055647",
	"depth": "300072633",
	"diameter": "300055624",
	"weight": "300056240"
}


# Meta
class CreditLine(Right):
	def __init__(self, *args, **kw):
		super(CreditLine, self).__init__(*args, **kw)
		# XXX Find a good Type for this
		self.has_type = Type("http://example.org/ns/creditline")
CreditLine._properties['value'] = {"rdf": "rdfs:value", "range": str}

class SourceCreditLine(CreditLine):
	def __init__(self, *args, **kw):
		super(SourceCreditLine, self).__init__(*args, **kw)
		# XXX Find a good Type for this
		self.has_type = []
		self.has_type = Type("http://example.org/ns/sourcecreditline")

class Department(Group):
	def __init__(self, *args, **kw):
		super(Department, self).__init__(*args, **kw)
		self.is_current_or_former_member_of = Museum


# Monkey patch Type's _toJSON to only emit full data if not just URI+type
def typeToJSON(self, top=False):
	props = self.__dict__.keys()
	if len(props) > 3:
		return super(Type, self)._toJSON()
	else:
		return self.id

Type._toJSON = typeToJSON
Person._properties['familyName'] = {"rdf": "schema:familyName", "range": str}
Person._properties['givenName'] = {"rdf": "schema:givenName", "range": str}
ManMadeObject._properties['culture'] = {"rdf": "schema:genre", "range": Type}


factory.base_url = "http://data.getty.edu/museum/"
factory.default_lang = "en"

departments = {}
locations = {}

GettyTrust = Group("http://vocab.getty.edu/ulan/500115987")
GettyTrust.label = "J. Paul Getty Trust"
Museum = Group("http://vocab.getty.edu/ulan/500115988")
Museum.is_current_or_former_member_of = GettyTrust
Museum.label = "J Paul Getty Museum"

painting_on_re = re.compile("^(.+?) on (.+?)$")
painting_and_re = re.compile("^(.+?) and (.+?)$")

def parse_materials(materials, typ):

	mats = []
	if typ == Painting:
		# Test for X on Y
		mat = materials.lower()
		m = painting_on_re.match(mat)

		if m:
			paint = m.groups()[0]

			# x and y
			m2 = painting_and_re.match(paint)
			if m2:
				paints = m2.groups()
			else:
				paints = [paint]
			for p in paints:
				if aat_material_mapping.has_key(p):
					mats.append(Material("http://vocab.getty.edu/aat/%s" % aat_material_mapping[p]))
				else:
					pass
					# print "Paint: %s" % paint

			support = m.groups()[1]
			if aat_material_mapping.has_key(support):
				mats.append(Material("http://vocab.getty.edu/aat/%s" % aat_material_mapping[support]))
			else:
				# look for common adjectives, ()s
				swords = support.split(' ')
				for sw in swords:
					if aat_material_mapping.has_key(sw):
						mats.append(Material("http://vocab.getty.edu/aat/%s" % aat_material_mapping[sw]))					

	return mats


fh = file('record_cache.json')
data = fh.read()
fh.close()
cache = json.loads(data)


# Load up people
fh = file('500_people.json')
data = fh.read()
fh.close()
peoplel = json.loads(data)
people = {}
for who in peoplel:
	whoid = str(who['id'])
	if people.has_key(whoid):
		continue
	else:
		wrec = {'id': whoid}
		wrec['type'] = who['type']
		wrec['date'] = who['display_date']
		wrec['name'] = who['display_name']
		wrec['nationality'] = who['display_nationality']
		wrec['birthplace'] = who['display_birthplace']
		wrec['deathplace'] = who['display_deathplace']
		wrec['institution'] = who['display_institution']
		wrec['image'] = who['display_image']
		wrec['biography'] = who['display_biography']
		people[whoid] = wrec 

print "Processing..."

#recs = cache.values()
recs = [cache['645']]

ldrecs = []
for rec in recs:
	ident = str(rec['id'])

	# Build a Foo type of MMO
	clslabel = rec['classification']['name']
	clsid = str(rec['classification']['id'])
	ot = rec['object_types'] # {'primary': {}, '???': {}}
	try:
		otid = str(ot['primary']['id'])
		otlabel = ot['primary']['display_value']
	except:
		otid = ""
		otlabel = ""

	if clslabel == "Photographs":
		if otlabel == "Print":
			obj = PhotographPrint(ident)
		elif otlabel == "Album":
			obj = PhotographAlbum(ident)
		elif otlabel == "Book":
			obj = PhotographBook(ident)
		elif otlabel.lower() == "cased object":
			# Treat as print?
			obj = PhotographPrint(ident)
		else:
			print "Unknown photograph subtype: %s" % otlabel
	elif aat_type_mapping.has_key(otlabel):
		obj = aat_type_mapping[otlabel](ident)
	elif aat_type_mapping.has_key(clslabel):
		obj = aat_type_mapping[clslabel](ident)
	else:
		obj = ManMadeObject(ident)
		# print "ot: '%s' ; cls: '%s'" % (otlabel, clslabel)
		t = Type(str(clsid))
		t.label = clslabel
		obj.has_type = t

	tms = TMSNumber(ident)
	tms.value = ident
	obj.is_identified_by = tms

	recno = rec['number']
	accno = AccessionNumber(recno)
	accno.value = recno
	obj.is_identified_by = accno

	obj.label = rec['title']
	try:
		obj.description = rec['description']['display']['value']
	except:
		pass

	production = Production(ident)
	obj.was_produced_by = production
	ts = TimeSpan(ident)
	ts.description = rec['date']
	# XXX Parse date string for dates
	production.has_timespan = ts

	# XXX if there are multiple makers with different roles,
	# create a super Production with components, and each
	# role gets a separate component

	for mk in rec['makers']:
		mkid = str(mk['id'])
		role = mk['role']

		who = Person(mkid)

		# Find in person db or deref
		first = mk['name_first']
		last = mk['name_last']

		try:
			person = people[mkid]
			who.label = person['name']
			who.description = person['biography']
			who.givenName = first
			who.familyName = last
			who.birthPlace = Place()
			who.deathPlace = Place()
			who.birthDate = ""
			who.deathDate = ""
		except:
			pass

		production.carried_out_by = who
		# XXX Link to ULAN

	# found, depicted, created

	if rec['places'] and rec['places'].has_key('place_created'):
		p = rec['places']['place_created']
		pid = str(p['id'])
		where = Place(pid)
		where.label = p['display_value']
		production.took_place_at = where

	# XXX Check for place_depicted (find out all possible keys)

	m = Material(ident)
	m.description = rec['medium']
	obj.consists_of = m
	mats = parse_materials(rec['medium'], obj.__class__)
	if mats:
		for mat in mats:
			m.defines_typical_wholes_for = mat

	dpt = rec['department']
	dptid = dpt['id']
	try:
		dept = departments[dptid]
	except:
		dept = Department(str(dpt['id']))
		dept.label = dpt['name']
		departments[dptid] = dept
	obj.has_current_owner = dept

	if rec['location']:
		loc = rec['location'][0]
		locid = str(loc['id'])
		try:
			where = locations[locid]
		except:
			where = Place(locid)
			where.label = loc['name']
			locations[locid] = where
		obj.has_current_location = where

	culture = Type("culture")
	culture.label = rec['culture']
	obj.culture = culture
	# XXX Map to AAT

	if rec['markings']:
		markings = Mark()
		markings.description = rec['markings']
		obj.shows_visual_item = markings
	if rec['signature']:
		sig = Signature()
		sig.description = rec['signature']
		obj.shows_visual_item = sig
	if rec['inscription']:
		insc = Inscription()
		insc.description = rec['inscription']
		obj.shows_visual_item = insc

	if rec.has_key('creditline'):
		credit = CreditLine()
		credit.value = rec['creditline']
		obj.is_subject_to = credit
	if rec['source_creditline']:
		srcCredit = SourceCreditLine()
		srcCredit.value = rec['source_creditline']
		obj.is_subject_to = srcCredit

	if rec['bibliography']:
		bx = 0
		for bib in rec['bibliography']:
			bt = bib['display_source_type']
			bv = bib['display_value']
			doc = Document("%s/%s" % (ident, str(bx)))
			bx += 1
			doc.label = bv
			doc.has_type = Type(bt)
			# XXX extract actual bib data and map to something sensible
			obj.is_documented_in = doc

	if rec['provenance']:
		for prov in rec['provenance']:
			date = prov['display_date']
			pid = str(prov['id'])
			who = prov['display_constituent']
			# XXX Parse constituent and map to provenance patterns


	if rec['related_exhibitions']:
		for exh in rec['related_exhibitions']:
			exhid = str(exh['record_identifier'])
			ttl = exh['display_title']
			dates = exh['display_dates']

			exhibition = Exhibition(exhid)
			exhibition.label = ttl
			if dates:
				ts = TimeSpan(exhid)
				ts.description = dates
				exhibition.has_timespan = ts
				# XXX parse for begin, end dates

			vens  = exh['display_venues']
			for v in vens:
				name = v['display_name']
				loc = v['display_location']
				vid = str(v['record_identifier'])
				vdates = v['display_dates']

				venue = Activity(vid)
				venue.label = name
				if vdates:
					vts = TimeSpan(vid)
					vts.description = vdates
					venue.has_timespan = vts
					# XXX Parse for begin, end dates
				if loc:
					place = Place(vid)
					place.description = loc
					# XXX Parse location
					venue.took_place_at = place
				exhibition.consists_of = venue

				# XXX Catalog Number is a Document that documents the Venue or Exhibition

			obj.was_present_at = exhibition

	ldrecs.append(obj)
	# print factory.toString(obj, compact=False)
	#break


