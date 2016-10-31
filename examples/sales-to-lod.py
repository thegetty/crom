
from lxml import etree
import json
import csv
import codecs
import re
import os
import sys
from dateutil.parser import parse as dateparse

# for cidoc_orm, see: https://github.com/azaroth42/Python-CIDOC-ORM
from cidoc_orm import factory, TimeSpan, Identifier, LegalBody, \
	Production, Actor, Place, Group, Material, Mark, \
	Activity, InformationObject, Purchase, Acquisition, MonetaryAmount, \
	Currency, MeasurementUnit, Dimension, PhysicalObject, VisualItem, Title

from aat_mapping import ManMadeObject, Type, Person, materialTypes, register_aat_class, \
	Painting, Sculpture, Drawing, Miniature, Graphic, Enamel, Tapestry, Mosaic, \
	Embroidery, Furniture, LocalNumber, dimensionUnits


PhysicalObject._properties['had_starting_price'] = {"rdf": "gri:had_starting_price", "range": MonetaryAmount}

cmUnit = dimensionUnits['cm']

# Cache of repeated Objects
catalogO = {}
placeO = {}
nationalityO = {}
personO = {}

materialO = {}

bad_price = {}
bad_dates = {}
bad_types = {}
bad_materials = {}

# XXX -- Distinguish Local from Lugt
register_aat_class("LugtNumber", Identifier, "300404621")

factory.base_url = "http://data.getty.edu/provenance/"
factory.default_lang = "en"

objTypeMap = {
	u'gem\xe4lde': Painting,
	'skulptur': Sculpture,
	'zeichnung': Drawing,
	'miniatur': Miniature,
	'graphik': Graphic,
	'painting': Painting,
	'enamel': Enamel,
	'miniature': Miniature,
	'sculpture': Sculpture,
	'drawing': Drawing,
	'tapestry': Tapestry,
	'embroidery': Embroidery,
	'furniture': Furniture,
	'mosaic': Mosaic,
	'watercolor': Painting 
}


r = "(je|l|h|d|b|durchm|durchmesser|dm[.]?)?[ ]*(ca.|h)?[ ]*([0-9,.]+)([ ]*(cm)?[ ]*x[ ]*([0-9,.]+)[ ]*(cm)?)?"
dimre = re.compile(r)
# dim1 = groups()[2], dim2 = groups()[5]


def process_record(rec):
	recData = {}
	for elm in rec.getchildren():
		tag = elm.tag
		curr = recData.get(tag, None)

		if elm.getchildren():
			value = elm
		else:
			value = elm.text

		if curr is None:
			recData[tag] = value
		elif type(recData[tag]) == list:
			recData[tag].append(value)
		else:
			recData[tag] = [curr, value]

	cno = recData['Catalogue_No']
	try:
		catalog = catalogO[cno]
		auction = catalog.refers_to

		# Try and update end of timespan
		if not hasattr(auction.has_timespan, 'end_of_the_end'):
			sed = recData.get('Sale_End_Date', '')			
			if sed:
				try:
					dt = dateparse(sed)
					span.end_of_the_end = "%s-%s-%sT00:00:00 CET" % (dt.year, dt.month, dt.day)
				except:
					try:
						bad_dates[sed] += 1
					except:
						bad_dates[sed] = 1

	except:
		catalog = InformationObject(cno)
		catalogO[cno] = catalog
		auction = Activity(cno)
		catalog.refers_to = auction
		catalog.has_representation = VisualItem(recData['GSC_link_to_pdf'])
		catalog.is_identified_by = LocalNumber(cno)

		# Auction date
		span = TimeSpan(cno)
		sbd = recData['Sale_Begin_Date']
		sed = recData.get('Sale_End_Date', '')
		try:
			dt = dateparse(sbd)
			span.begin_of_the_begin = "%s-%s-%sT00:00:00 CET" % (dt.year, dt.month, dt.day)
		except:
			try:
				bad_dates[sbd] += 1
			except:
				bad_dates[sbd] = 1
		if sed:
			try:
				dt = dateparse(sed)
				span.end_of_the_end = "%s-%s-%sT00:00:00 CET" % (dt.year, dt.month, dt.day)
			except:
				try:
					bad_dates[sed] += 1
				except:
					bad_dates[sed] = 1
		auction.has_timespan = span

		# Auction location
		city = recData['City_of_Sale']
		try:
			cityPlace = placeO[city]
		except:
			cityPlace = Place(city)
			cityPlace.label = city
			placeO[city] = cityPlace
		auction.took_place_at = cityPlace

		try:
			country = cityPlace.falls_within
		except:
			try:
				country = recData['Country_Auth']
				countryPlace = Place(country)
				countryPlace.label = country
				cityPlace.falls_within = countryPlace
			except:
				# No country
				pass

		try:
			# Auction House
			house = recData['Auction_House']
			try:
				ahouse = houseO[house]
			except:
				ahouse = LegalBody(house)
				ahouse.label = house
			auction.carried_out_by = ahouse
		except:
			# No auction house? :(
			pass

	try:
		lno = recData["Lot_Number"]
	except:
		print "No lot number for %s" % recData['recno']
		return

	cnolot = cno +'/'+ lno

	# Build an aggregation of objects for the lot
	lotset = PhysicalObject(cnolot + "-set")
	# InfoObj for the entry
	entry = InformationObject(cnolot)
	entry.refers_to = lotset
	catalog.is_composed_of = entry

	if recData.has_key('Price'):
		pr = recData['Price']
		# Process prinfo

		if type(pr) == list:
			pr = pr[0]
		if not type(pr) in [str, unicode]:
			try:	
				pr = pr.text
			except:
				pr = ""

		pr = pr.replace("[?]", "")
		pr = pr.replace('?', '')
		pr = pr.strip()

		if pr:
			pr = pr.replace('1/2', '.5')
			pr = pr.replace('1/4', '.25')
			pr = pr.replace('3/4', '.75')
			pr = pr.replace(' .', '.')

			# Unknown:  x-y-z  x.y.z
			# x"y' x=y  x:y x=y-z
			# 

			if pr.find(" frs") > -1:
				curr = Currency("francs")
				curr.label = "francs"
				pr = pr.replace(' frs', '')
			elif pr.find(" fl") > -1:
				curr = Currency("fl.s")
				curr.label = "fl.s"
				pr = pr.replace(' fl', '')
			elif pr.find(" livres") > -1:
				curr = Currency("pounds")
				curr.label = "pounds"
				pr = pr.replace(' livres', '')
			else:
				curr = None

			pr = pr.replace('[or]', 'or')
			oidx = pr.find(' or ') 
			if oidx > -1:
				pr = pr[:oidx]
				pr = pr.strip()

			fidx = pr.find(' for ')
			if fidx > -1:
				pr = pr[:fidx]
				pr = pr.strip()

			try:
				p = float(pr)				
			except:
				p = -1
				try:
					bad_price[pr] += 1
				except:
					bad_price[pr] = 1
			if p >= 0:
				amnt = MonetaryAmount(cnolot + "-start")
				amnt.has_value = p
				if curr:
					amnt.has_currency = curr
		 		lotset.had_starting_price = amnt


	# Build the object

	try:
		typs = recData['Object_Types'].xpath('./Object_Type/text()')
		ot = typs[0]
		cls = objTypeMap[ot]
	except:
		cls = ManMadeObject
		try:
			bad_types[ot] += 1
		except:
			bad_types[ot] = 1

	obj = cls(cnolot)
	lotset.is_composed_of = obj

	title = Title(cnolot)
	obj.has_title = title
	try:
		title.value = recData['Title']
	except:
		title.value = "[No Title Known]"
	if recData.has_key('Title_Modifier'):
		title.has_note = unicode(recData['Title_Modifier'])

	if recData.has_key('Materials'):
		for mat in recData['Materials'].xpath('./Material/text()'):
			ot = mat.lower()
			ot = ot.replace(',', '')
			ot = ot.replace('#', '')
			ot = ot.replace('.', '')
			ot = ot.replace('?', '')
			ot = ot.replace('auf', '')
			ot = ot.replace('und', '')
			ot = ot.replace("on", " ")
			ot = ot.replace("and", " ")			
			ot = ot.replace("  ", ' ')

			words = ot.split(' ')
			obj.consists_of = []
			for w in words:
				if w:
					try:
						material = materialO[w]
					except:
						material = Material(w)
						materialO[w] = material
						material.value = w
					obj.consists_of = material

	if recData.has_key("Dimensions"):
		for dimtext in recData['Dimensions'].xpath('./Dimension_Text/text()'):
			m = dimre.match(dimtext)
			if m:
				d1 = m.groups()[2]
				d2 = m.groups()[5]

				dim1 = Dimension(cnolot + "_d1")
				dim1.has_value = d1
				dim1.has_unit = cmUnit
				obj.has_dimension = dim1

				if d2:
					dim2 = Dimension(cnolot + "_d2")
					dim2.has_value = d2				
					dim2.has_unit = cmUnit
					obj.has_dimension = dim2

			else:
				#print "Can't handle dimension data:"
				#print dimtext			
				try:
					bad_materials[dimtext] += 1
				except:
					bad_materials[dimtext] = 1

	# Artist could be modified by Attrib_Mod
	# e.g. zugeschrieben --> attributed (2200)
	# Kopie von  --> copy from (1)
	# stil --> style [of] (24)

	# Artist
	if recData.has_key('Artist'):
		arts = recData['Artist']
		if type(arts) != list:
			arts = [arts]
		for artist in arts:
			va = artist.xpath('./Verb_Artist/text()')
			aa = artist.xpath('./Artist_Auth/text()')
			natl = artist.xpath('./Nationality/text()')
			mod = artist.xpath('./Attrib_Mod/text()')

			# first try to detect non names
			if aa:
				aa = unicode(aa[0])
				if aa == "NEW":
					# treat as if not present
					pass
				elif aa.startswith('['):
					# anonymous artist with some known features
					pass
				aname = aa.lower()
				aname = aname.replace(" ", "_")
				try:
					who = personO[aname]
				except:
					who = Person(aname)
					personO[aname] = who
					# put verbatim name somewhere
					# and authority name in p131 is identified by
					who.label = aa

					if natl: 
						natl = unicode(natl[0])
						try:
							nat = nationalityO[natl]
						except:
							nat = Group(natl)
							nat.label = natl
						who.is_current_or_former_member_of = nat

				# one production event per artist?
				prod = Production(cnolot + aname)
				prod.carried_out_by = who
				obj.was_produced_by = prod 

	# seller if we know
	seller = None
	if recData.has_key("Seller"):
		sells = recData['Seller']
		if type(sells) != list:
			sells = [sells]
		sx = 0
		for s in sells:
			try:
				lbl = unicode(s.xpath("./Seller_Auth/text()")[0])
			except:	
				try:
					lbl = unicode(s.xpath("./Verb_Seller/text()")[0])				
				except:
					# ???!!!
					continue
			end = "-seller"
			if sx:
				end += "-%s" % sx
			seller = Actor(cnolot + end)
			seller.label = lbl
			obj.has_former_or_current_owner = seller
			sx += 1

	try:
		txn = recData['Transaction']
		txn = txn.lower()
	except:
		txn = "unknown"
	txn = txn.replace('[?]', '')
	txn = txn.replace("unknown or ", "")
	txn = txn.replace(" or unknown", "")
	txn = txn.strip()

	if txn.find(" or ") > -1:
		# Don't know what to do with X or Y
		print "Not processing or for txn"
		return

	if txn in ["sold", "bought in", "passed"]:
		lot = Activity(cnolot)
		auction.consists_of = lot
		lot.used_specific_object = lotset
		
		span = TimeSpan(cnolot)
		try:
			date = recData['Lot_Sale_Date']
			# NB: this is going to end up strange due to UK vs EU timezones
			try:
				dt = dateparse(date)
				begin = "%s-%s-%sT00:00:00 CET" % (dt.year, dt.month, dt.day)
				end = "%s-%s-%sT23:59:59 CET" % (dt.year, dt.month, dt.day)
				span.begin_of_the_begin = begin
				span.end_of_the_end = end
				lot.has_timespan = span
			except:
				try:
					bad_dates[date] += 1
				except:
					bad_dates[date] = 1
		except:
			print "No Sale Date: %s" % recData['recno']

		ln = recData.get('Lot_Notes', None)
		if ln is not None:
			lot.has_note = unicode(ln)

		entry.refers_to = lot

	if txn in ['sold', 'bought in']:
		# Bidding activity exists
		bidding = Activity(cnolot + "-bidding")
		lot.consists_of = bidding

	if txn == "sold":
		txn = Purchase(cnolot+"-transaction")
		lot.consists_of = txn
		bidding.occurs_before = txn

		acq = Purchase(cnolot + "-acquisition")
		txn.consists_of = acq
		acq.transferred_title_of = obj

		if seller:
			sellers = obj.has_former_or_current_owner
			if type(sellers) == list:
				for s in sellers:
					acq.transferred_title_from = s
			else:	
				acq.transferred_title_from = sellers			

		bx = 0
		if recData.has_key("Buyer"):
			buys = recData['Buyer']
			if type(buys) != list:
				buys = [buys]
			for b in buys:
				try:
					lbl = unicode(b.xpath("./Buyer_Auth/text()")[0])
				except:
					try:
						lbl = unicode(b.xpath("./Verb_Buyer/text()")[0])					
					except:
						# ???!!!
						continue

				end = "-buyer"
				if bx:
					end += "-%s" % bx
				buyer = Actor(cnolot + end)
				buyer.label = lbl
				acq.transferred_title_to = buyer
				bx += 1


	return catalog



recdir = '/Users/rsanderson/Box Sync/PI_Sales/'
files = ['salesdb1.xml', 'salesdb2.xml', 'salesdb3.xml', 'salesdb4.xml']
files = ['salesdb1.xml']

for fn in files:
	rec = []
	fh = file(os.path.join(recdir, fn))
	#fh = codecs.open(os.path.join(recdir, fn), 'r', 'iso-8859-1')

	# chomp first three lines
	fh.readline() ; fh.readline() ; fh.readline()

	header = '<?xml version="1.0" encoding="UTF-8"?>\n'

	line = fh.readline()
	while line != "</root>\n":
		while (line.find('</record>') == -1):
			rec.append(line)
			line = fh.readline()
			if not line:
				break
		rec.append(line)	

		data = ''.join(rec)
		data = header + data
		data = data.replace("Catalogue_No.", "Catalogue_No")
		data = data.replace("Country_Auth.", "Country_Auth")
		data = data.replace('\x04', '')
		data = data.replace('\x1f', '')

		try:
			dom = etree.XML(data)
		except:
			print "Invalid record data: %s" % data[:200]

		top = process_record(dom)
		# break

		line = fh.readline()
		rec = []

	fh.close()

