
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

from .model import Identifier, Mark, HumanMadeObject, Type, \
	Person, Material, MeasurementUnit, Place, Dimension, Currency, \
	ConceptualObject, TimeSpan, Actor, PhysicalThing, Language, \
	LinguisticObject, InformationObject, Formation, Dissolution, \
	Activity, Group, Name, MonetaryAmount, Right, \
	Destruction, AttributeAssignment, BaseResource, PhysicalObject, \
	Acquisition, HumanMadeFeature, VisualItem, Set, Birth, Death, \
	PropositionalObject, Payment, Creation, Phase, Period, \
	Production, Event, DigitalObject, \
	STR_TYPES, factory

# Add classified_as initialization hack for all resources
def post_init(self, **kw):
	if self.__class__._classification:
		for t in self._classification:
			self.classified_as = t
BaseResource._post_init = post_init

instances = {}
instance_types = {}

def register_vocab_class(name, data):
	parent = data['parent']
	id = data['id']
	label = data['label']
	vocab = data.get('vocab', 'aat')

	c = type(name, (parent,), {})
	if id.startswith('http'):
		t = Type(id)
	else:
		t = Type("http://vocab.getty.edu/%s/%s" % (vocab, id))
	t._label = label
	instance_types[name] = t
	if parent == LinguisticObject and "brief" in data:
		c._classification = [t, instances["brief text"]]
	else:	
		c._classification = [t]		
	if "metatype" in data:
		t.classified_as = instances[data['metatype']]
	c._type = None # To avoid conflicting with parent class
	globals()[name] = c	
	return c

def register_aat_class(name, data):
	data['vocab'] = 'aat'
	register_vocab_class(name, data)

def register_instance(name, data):
	parent = data['parent']
	id = data['id']
	vocab = data.get('vocab', 'aat')
	label = data['label']

	if id.startswith('http'):
		t = parent(id)
	else:
		t = parent("http://vocab.getty.edu/%s/%s" % (vocab, id))
	t._label = label
	instances[name] = t
	return t

# Meta meta
ext_classes = {

	"LocalNumber": {"parent":Identifier, "id":"300404621", "label": "Owner-Assigned Number"},	
	"SystemNumber": {"parent":Identifier, "id":"300435704", "label": "System-Assigned Number"},
	"AccessionNumber": {"parent":Identifier, "id":"300312355", "label": "Accession Number"},
	"LotNumber": {"parent": Identifier, "id": "300404628", "label": "Lot Number"},
	"IsbnIdentifier": {"parent": Identifier, "id": "300417443", "label": "ISBN Identifier"},
	"IssnIdentifier": {"parent": Identifier, "id": "300417430", "label": "ISSN Identifier"},
	"DoiIdentifier": {"parent": Identifier, "id": "300417432", "label": "DOI Identifer"},

	"EmailAddress": {"parent": Identifier, "id":"300435686", "label": "Email Address"},
	"StreetAddress": {"parent": Identifier, "id":"300435687", "label": "Street Address"},
	"TelephoneNumber": {"parent": Identifier, "id": "300435688", "label": "Telephone Number"},
	"FaxNumber": {"parent": Identifier, "id": "300435689", "label": "Fax Number"},
	"StreetNumber": {"parent": Identifier, "id":"300419272", "label": "Street Number"},
	"StreetName": {"parent": Identifier, "id": "300419273", "label": "Street Name"},
	"PostalCode": {"parent": Identifier, "id": "300419274", "label": "Postal Code"},

	"DigitalImage": {"parent": DigitalObject, "id": "300215302", "label": "Digital Image"},

	"OwnershipRight": {"parent": Right, "id":"300055603", "label": "Ownership Right"},
	"CustodyRight": {"parent": Right, "id":"300411616", "label": "Custody Right"},
	"CopyrightRight": {"parent": Right, "id":"300055598", "label": "Copyright"},

	"OwnershipPhase": {"parent": Phase, "id": "300055603", "label": "Ownership Phase"},

	"Note": {"parent": LinguisticObject, "id":"300027200", "label": "Note", "brief": True},
	"Description": {"parent": LinguisticObject, "id":"300411780", "label": "Description", "brief": True},
	"_BriefText": {"parent": LinguisticObject, "id": "300418049", "label":"Brief Text"},
	"Abstract": {"parent": LinguisticObject, "id":"300026032", "label": "Abstract", "brief": True},
	"Annotation": {"parent": LinguisticObject, "id":"300026100", "label":"Annotation"},
	"Citation": {"parent": LinguisticObject, "id":"300311705", "label": "Citation", "brief": True},

	"CreditStatement": {"parent": LinguisticObject, "id": "300026687", "label": "Credit Statement", "brief": True},
	"RightsStatement": {"parent": LinguisticObject, "id": "300435434", "label": "Copyright/License Statement", "brief": True},
	"ValuationStatement": {"parent": LinguisticObject, "id": "300435426", "label": "Appraisal Statement", "brief": True},
	"ConditionStatement": {"parent": LinguisticObject, "id": "300435425", "label": "Condition Statement", "brief": True},
	"SignificanceStatement": {"parent": LinguisticObject, "id": "300435427", "label": "Significance Statement", "brief": True},
	"ContextStatement": {"parent": LinguisticObject, "id": "300435428", "label": "Historical/Cultural Context", "brief": True},
	"SourceStatement": {"parent": LinguisticObject, "id": "300404764", "label": "Source Statement", "brief": True},
  
	"MarkingsStatement": {"parent": LinguisticObject, "id": "300435420", "label": "Markings", "brief": True},
	"InscriptionStatement": {"parent": LinguisticObject, "id": "300435414", "label": "Inscription", "brief": True},
	"SignatureStatement": {"parent": LinguisticObject, "id": "300435415", "label": "Signature", "brief": True},
	"WatermarksStatement": {"parent": LinguisticObject, "id": "300435421", "label": "Watermarks", "brief": True},
	"MaterialStatement": {"parent": LinguisticObject, "id": "300435429", "label": "Material Statement", "brief": True},
	"PhysicalStatement": {"parent": LinguisticObject, "id": "300435452", "label": "Physical Statement", "brief": True},
	"DimensionStatement": {"parent": LinguisticObject, "id": "300435430", "label": "Dimension Statement", "brief": True},
	"CultureStatement": {"parent": LinguisticObject, "id": "300435431", "label": "Culture Statement", "brief": True},
	"PeriodStatement": {"parent": LinguisticObject, "id": "300435432", "label": "Period Statement", "brief": True},

	"ProductionStatement": {"parent": LinguisticObject, "id": "300435436", "label": "Production Statement", "brief": True },
	"AcquisitionStatement": {"parent": LinguisticObject, "id": "300435439", "label": "Acquisition Statement", "brief": True},
	"ProvenanceStatement": {"parent": LinguisticObject, "id":"300435438", "label": "Provenance Statement", "brief": True},
	"BibliographyStatement": {"parent": LinguisticObject, "id": "300026497", "label": "Bibliography Statement", "brief": True},
	"ExhibitionStatement": {"parent": LinguisticObject, "id":"300435424", "label":"Exhibition Statement", "brief": True},

	"BiographyStatement": {"parent": LinguisticObject, "id":"300435422", "label": "Biography Statement", "brief": True},
	"EditionStatement": {"parent": LinguisticObject, "id":"300435435", "label": "Edition Statement", "brief": True},
	"PaginationStatement": {"parent": LinguisticObject, "id":"300435440", "label": "Pagination Statement", "brief": True},
	"FoliationStatement": {"parent": LinguisticObject, "id":"300435441", "label": "Foliation Statement", "brief": True},
	"LanguageStatement": {"parent": LinguisticObject, "id": "300435433", "label": "Language Statement", "brief": True},

	"TranscribedInscription": {"parent": LinguisticObject, "id": "300028702", "label": "Transcribed Inscription", "brief": True},

	"CatalogueRaisonneText": {"parent": LinguisticObject, "id":"300026061", "label": "Catalogue Raisonne"},
	"AuctionCatalogText": {"parent": LinguisticObject, "id":"300026068", "label": "Auction Catalog"},
	"SalesCatalogText": {"parent": LinguisticObject, "id": "300026074", "label": "Sales Catalog"},
	"ExhibitionCatalogText": {"parent": LinguisticObject, "id": "300026096", "label": "Exhibition Catalog"},
	"AccountBookText": {"parent": LinguisticObject, "id": "300027483", "label": "Account Book"},
	"RegisterText": {"parent": LinguisticObject, "id":"300027168", "label": "Register"},
	"PageText": {"parent": LinguisticObject, "id":"300194222", "label": "Page"},
	"FolioText": {"parent": LinguisticObject, "id":"300189604", "label": "Folio"},

	"WebPage": {"parent": LinguisticObject, "id":"300264578", "label": "Web Page"},
	"DataRecord": {"parent": LinguisticObject, "id":"300026685", "label": "Data Record"}, # Not sure about this one
	"Heading": {"parent": LinguisticObject, "id": "300200862", "label": "Heading"},
	"SubHeading": {"parent": LinguisticObject, "id": "300419992", "label": "Heading"},

	"JournalText": {"parent": LinguisticObject, "id":"300215390", "label": "Journal"},
	"IssueText": {"parent": LinguisticObject, "id":"300312349", "label": "Issue"},
	"VolumeText": {"parent": LinguisticObject, "id":"300265632", "label": "Volume"},
	"ArticleText": {"parent": LinguisticObject, "id":"300048715", "label": "Article"},
	"ChapterText": {"parent": LinguisticObject, "id":"300311699", "label": "Chapter"},
	"SeriesText": {"parent": LinguisticObject, "id":"300027349", "label": "Series"},
	"ProceedingsText": {"parent": LinguisticObject, "id":"300027316", "label": "Proceedings"},
	"MonographText": {"parent": LinguisticObject, "id":"300060417", "label": "Monograph"},
	"PatentText": {"parent": LinguisticObject, "id":"300027832", "label": "Patent"},
	"ThesisText": {"parent": LinguisticObject, "id":"300028028", "label": "Thesis"},
	"TechnicalReportText": {"parent": LinguisticObject, "id":"300027323", "label": "Technical Report"},
	"DocManuscriptText": {"parent": LinguisticObject, "id":"300028579", "label": "Document Manuscript"},
	"AudioVisualContent": {"parent": LinguisticObject, "id":"300028045", "label": "A/V Content"},

	"Height":     {"parent": Dimension, "id":"300055644", "label": "Height"},
	"Width":      {"parent": Dimension, "id":"300055647", "label": "Width"},
	"Depth":      {"parent": Dimension, "id":"300072633", "label": "Depth"},
	"Diameter":   {"parent": Dimension, "id":"300055624", "label": "Diameter"},
	"Weight":     {"parent": Dimension, "id":"300056240", "label": "Weight"},
	"Color":      {"parent": Dimension, "id":"300056130", "label": "Color"},
	"SequencePosition": {"parent": Dimension, "id":"300010269", "label":"Sequence Position"},
	"PhysicalDimension": {"parent": Dimension, "id":"300055642", "label":"Unknown physical dimension"},

	"Gallery":      {"parent": Place, "id":"300240057", "label": "Gallery (place)"},
	"AuctionHouse": {"parent": Place, "id":"300005234", "label": "Auction House (place)"},
	"MuseumPlace":  {"parent": Place, "id":"300005768", "label": "Museum (place)"},
	"ExhibitionPlace": {"parent": Place, "id":"300005748", "label": "Exhibition (place)"},
	"City":         {"parent": Place, "id":"300008389", "label": "City"},
	"Province":     {"parent": Place, "id":"300000774", "label": "Province"},
	"Nation":       {"parent": Place, "id":"300128207", "label": "Nation"},

	"AuctionHouseOrg": {"parent": Group, "id": "300417515", "label": "Auction House (organization)"},
	"MuseumOrg":   {"parent": Group, "id":"300312281", "label": "Museum"},
	"Department":  {"parent": Group, "id":"300263534", "label": "Department"},
	"School":      {"parent": Group, "id":"300404284", "label": "School"},
	"Studio":      {"parent": Group, "id":"300404275", "label": "Studio"},
	"Circle":      {"parent": Group, "id":"300404283", "label": "Circle"},
	"Workshop":    {"parent": Group, "id":"300404274", "label": "Workshop"},
	"Atelier":     {"parent": Group, "id":"300404277", "label": "Atelier"},
	"FollowerGroup": {"parent": Group, "id":"300404282", "label": "Follower"},
	"PupilGroup":  {"parent": Group, "id":"300404279", "label": "Pupil"},

	"Nationality": {"parent": Type, "id":"300379842", "label": "Nationality"},
	"Gender":      {"parent": Type, "id":"300055147", "label": "Gender"},
	"Occupation":  {"parent": Type, "id":"300263369", "label": "Occupation"},

	"Auctioneer":  {"parent": Person, "id":"300025208", "label": "Auctioneer"}, # is this useful?

	"AuctionEvent": {"parent": Activity, "id":"300054751", "label": "Auction Event"},
	"Auction":     {"parent": Activity, "id":"300420001", "label": "Auction of Lot"}, # Individual auction-of-lot
	"Bidding":     {"parent": Creation, "id":"300054602", "label": "Bidding"}, # individual bid
	"Curating":    {"parent": Activity, "id":"300054277", "label": "Curating"},
	"Inventorying": {"parent": Activity, "id":"300077506", "label": "Inventorying"},
	"Exhibition":  {"parent": Activity, "id":"300054766", "label": "Exhibiting"},
	"MultiExhibition": {"parent": Activity, "id":"300054773", "label": "Exhibiting in multiple locations"},
	"Active":      {"parent": Activity, "id":"300393177", "label": "Professional Activities"},
	"Publishing":  {"parent": Activity, "id":"300054686", "label": "Publishing"},

	"Purchase":  {"parent":Acquisition, "id":"300077989", "label": "Purchasing"},
	"Procurement": {"parent": Activity, "id":"300137616", "label": "Procurement"},
	"Assembling": {"parent": Activity, "id":"300077121", "label":"Assembling"},
	"Managing": {"parent": Activity, "id":"300054277", "label": "Managing"},
	"Storing": {"parent": Activity, "id":"300056390", "label": "Storing"},
	"Producing": {"parent": Activity, "id":"300054713", "label": "Producing"},

	"ExhibitionIdea": {"parent": PropositionalObject, "id":"300417531", "label": "Exhibition"},

	"Theft": {"parent": Acquisition, "id": "300055292", "label": "Theft"},
	"Looting": {"parent": Acquisition, "id":"300379554", "label": "Looting"},

	"AuctionLotSet": {"parent": Set, "id":"300411307", "label": "Auction Lot"},
	"CollectionSet": {"parent": Set, "id":"300025976", "label": "Collection"},
	"ArchiveSet": {"parent": Set, "id":"300375748", "label": "Archive"}, # Maybe 300189759?
	"ArchiveGroupSet": {"parent": Set, "id":"300404022", "label": "Archival Grouping"},
	"ArchiveSubGroupSet": {"parent": Set, "id":"300404023", "label": "Archival SubGrouping"},
	
	"PrimaryName": {"parent": Name, "id":"300404670", "label": "Primary Name"},
	"SortName": {"parent": Name, "id":"300404672", "label": "Sorting Name"},
	"PersonalName": {"parent": Name, "id":"300266386", "label": "Personal Name"},
	"Title": {"parent": Name, "id":"300195168", "label": "Title"},
	"DisplayName": {"parent": Name, "id": "300404669", "label": "Display Title"},
	"AliasName": {"parent": Name, "id": "300404664", "label": "Alias"},
	"MaidenName": {"parent": Name, "id": "300404682", "label": "Maiden Name"},

	"GivenName": {"parent": Name, "id":"300404651", "label": "Given Name"},
	"FamilyName": {"parent": Name, "id":"300404652", "label": "Family Name"},
	"MiddleName": {"parent": Name, "id":"300404654", "label": "Middle Name"},
	"NameSuffix": {"parent": Name, "id":"300404662", "label": "Name Suffix"},
	"NamePrefix": {"parent": Name, "id":"300404845", "label": "Name Prefix"},


	"CityName": {"parent": Name, "id": "300008389", "label": "City"},
	"CountryName": {"parent": Name, "id": "300128207", "label": "Country"},

	"Painting": {"parent": HumanMadeObject, "id": "300033618", "label": "Painting", "metatype": "work type"},
	"Sculpture": {"parent": HumanMadeObject, "id": "300047090", "label": "Sculpture", "metatype": "work type"},
	"Drawing": {"parent": HumanMadeObject, "id": "300033973", "label": "Drawing", "metatype": "work type"},
	"Miniature": {"parent": HumanMadeObject, "id": "300033936", "label": "Miniature", "metatype": "work type"},
	"Tapestry": {"parent": HumanMadeObject, "id": "300205002", "label": "Tapestry", "metatype": "work type"},
	"Furniture": {"parent": HumanMadeObject, "id": "300037680", "label": "Furniture", "metatype": "work type"},
	"Mosaic": {"parent": HumanMadeObject, "id": "300015342", "label": "Mosaic", "metatype": "work type"},
	"Photograph": {"parent": HumanMadeObject, "id": "300046300", "label": "Photograph", "metatype": "work type"},
	"Coin": {"parent": HumanMadeObject, "id": "300037222", "label": "Coin", "metatype": "work type"},
	"Vessel": {"parent": HumanMadeObject, "id": "300193015", "label": "Vessel", "metatype": "work type"},
	"Graphic": {"parent": HumanMadeObject, "id": "300015387", "label": "Graphic Art", "metatype": "work type"},
	"Enamel": {"parent": HumanMadeObject, "id": "300178264", "label": "Enamel", "metatype": "work type"},
	"Embroidery": {"parent": HumanMadeObject, "id": "300264024", "label": "Embroidery", "metatype": "work type"},
	"PhotographPrint": {"parent": HumanMadeObject, "id": "300127104", "label": "Photograph Print", "metatype": "work type"},
	"PhotographAlbum": {"parent": HumanMadeObject, "id": "300026695", "label": "Photograph Album", "metatype": "work type"},
	"PhotographBook": {"parent": HumanMadeObject, "id": "300265728", "label": "Photograph Book", "metatype": "work type"},
	"PhotographColor": {"parent": HumanMadeObject, "id": "300128347", "label": "Color Photograph", "metatype": "work type"},
	"PhotographBW": {"parent": HumanMadeObject, "id": "300128359", "label": "Black and White Photograph", "metatype": "work type"},
	"Negative": {"parent": HumanMadeObject, "id": "300127173", "label": "Photographic Negative", "metatype": "work type"},
	"Map": {"parent": HumanMadeObject, "id": "300028094", "label": "Map", "metatype": "work type"},
	"Clothing": {"parent": HumanMadeObject, "id": "300266639", 'label': "Clothing", "metatype": "work type"},
	"Furniture": {"parent": HumanMadeObject, "id":"300037680", "label": "Furniture", "metatype": "work type"},

	"Architecture": {"parent": HumanMadeObject, "id":"300263552", "label": "Architecture", "metatype": "work type"},
	"Armor": {"parent": HumanMadeObject, "id":"300036745", "label": "Armor", "metatype": "work type"},
	"Book": {"parent": HumanMadeObject, "id":"300028051", "label": "Book", "metatype": "work type"},
	"DecArts": {"parent": HumanMadeObject, "id":"300054168", "label": "Decorative Arts", "metatype": "work type"},
	"Implement": {"parent": HumanMadeObject, "id":"300024841", "label": "Implement", "metatype": "work type"},
	"Jewelry": {"parent": HumanMadeObject, "id":"300209286", "label": "Jewelry", "metatype": "work type"},
	"Manuscript": {"parent": HumanMadeObject, "id":"300265483", "label": "Manuscript", "metatype": "work type"},
	"SiteInstallation": {"parent": HumanMadeObject, "id":"300047896", "label": "Site Installation", "metatype": "work type"},
	"Text": {"parent": HumanMadeObject, "id":"300263751", "label": "Text", "metatype": "work type"},
	"Print":  {"parent": HumanMadeObject, "id":"300041273", "label": "Print", "metatype": "work type"},
	"TimeBasedMedia": {"parent": HumanMadeObject, "id":"300185191", "label": "Time-based Media", "metatype": "work type"},
	"Page": {"parent": HumanMadeObject, "id":"300194222", "label": "Page", "metatype": "work type"},

	"FrontPart": {"parent": HumanMadeObject, "id":"300190703", "label": "Front Part"},
	"BackPart": {"parent": HumanMadeObject, "id":"300190692", "label": "Back Part"},
	"TopPart": {"parent": HumanMadeObject, "id":"300190710", "label": "Top Part"},
	"BottomPart": {"parent": HumanMadeObject, "id":"300190695", "label": "Bottom Part"},
	"SidePart": {"parent": HumanMadeObject, "id":"300190706", "label": "Side Part"},
	"SupportPart": {"parent": HumanMadeObject, "id":"300014844", "label": "Support"},
	"FramePart": {"parent": HumanMadeObject, "id":"300404391", "label": "Frame"},
	"MountPart": {"parent": HumanMadeObject, "id":"300131087", "label": "Mount"},
	"PanelPart": {"parent": HumanMadeObject, "id":"300014657", "label": "Panel"},
	"BasePart": {"parent": HumanMadeObject, "id":"300001656", "label": "Base"},

	"Folder": {"parent": HumanMadeObject, 'id':"300197602", "label": "Folder", "metatype": "work type"},
	"Box": {"parent": HumanMadeObject, "id":"300045643", "label": "Box", "metatype": "work type"},
	"Envelope": {"parent": HumanMadeObject, "id":"300197601", "label": "Envelope", "metatype": "work type"},
	"Binder": {"parent": HumanMadeObject,"id":"300252990", "label": "Binder", "metatype": "work type"},
	"Case": {"parent": HumanMadeObject,"id":"300045659", "label": "Case", "metatype": "work type"},
	"FlatfileCabinet": {"parent": HumanMadeObject,"id":"300417284", "label": "Flat File Cabinet", "metatype": "work type"},

	"StartingPrice": {"parent": MonetaryAmount, "id": "300417242", "label": "Starting Price"},
	"ReservePrice": {"parent": MonetaryAmount, "id": "300417243", "label": "Reserve Price"},
	"EstimatedPrice": {"parent": MonetaryAmount, "id": "300417244", "label": "Estimated Price"},

	"CommissionPayment": {"parent": Payment, "id": "300393199", "label": "Commission"}

}
 
identity_instances = {
	"watercolor": {"parent": Material, "id": "300015045", "label": "watercolors"},	
	"oil": {"parent": Material, "id": "300015050", "label": "oil"},
	"tempera": {"parent": Material, "id": "300015062", "label": "tempera"},
	"canvas": {"parent": Material, "id": "300014078", "label": "canvas"},
	"oak": {"parent": Material, "id": "300012264", "label": "oak"},
	"gold leaf": {"parent": Material, "id": "300264831", "label": "gold leaf"},
	"paper": {"parent": Material, "id": "300014109", "label": "paper"},
	"copper": {"parent": Material, "id": "300011020", "label": "copper"},
	"terracotta": {"parent": Material, "id": "300010669", "label": "terracotta"},
	"glass": {"parent": Material, "id": "300010797", "label": "glass"},
	"chalk": {"parent": Material, "id": "300011727", "label": "chalk"},
	"bronze": {"parent": Material, "id": "300010957", "label": "bronze"},
	"marble": {"parent": Material, "id": "300011443", "label": "marble"},
	"albumen silver print": {"parent": Material, "id": "300127121", "label": "albumen silver print"},
	"gelatin silver print": {"parent": Material, "id": "300128695", "label": "gelatin silver print"},
	"silver": {"parent": Material, "id": "300011029", "label": "silver"},

	"synthetic": {"parent": Type, "id": "xxx", "label": "Synthetic Material"},

	"lignes": {"parent": MeasurementUnit, "id": "300435501", "label": "Paris lines"},
	"fr_inches": {"parent": MeasurementUnit, "id": "300435502", "label": "Paris inches"},
	"fr_feet": {"parent": MeasurementUnit, "id":"300435503", "label": "Paris feet"},
	"inches": {"parent": MeasurementUnit, "id": "300379100", "label": "inches"},
	"feet": {"parent": MeasurementUnit, "id":"300379101", "label": "feet"},
	"cm": {"parent": MeasurementUnit, "id": "300379098", "label": "centimeters"},
	"meters": {"parent": MeasurementUnit, "id": "300379099", "label": "meters"},
	"braccia": {"parent": MeasurementUnit, "id": "300404161", "label": "braccia"},
	"ells": {"parent": MeasurementUnit, "id": "300412070", "label": "ells"},
	"percent": {"parent": MeasurementUnit, "id": "300417377", "label": "percent"},
	"numbers": {"parent": MeasurementUnit, "id": "300055665", "label": "numbers"},
	"bytes": {"parent": MeasurementUnit, "id": "300265869", "label": "bytes"},
	"kilobytes": {"parent": MeasurementUnit, "id": "300265870", "label": "kilobytes"},
	"megabytes": {"parent": MeasurementUnit, "id": "300265873", "label": "megabytes"},
	"gigabytes": {"parent": MeasurementUnit, "id": "300265874", "label": "gigabytes"},
	"terabytes": {"parent": MeasurementUnit, "id": "300266477", "label": "terabytes"},
	"partsUnit": {"parent": MeasurementUnit, "id": "300404159", "label": "parts"},
	"pageCount": {"parent": MeasurementUnit, "id": "300194222", "label": "pages"},
	"pixels": {"parent": MeasurementUnit, "id": "300266190", "label": "pixels"},
	"rgb_colorspace": {"parent": MeasurementUnit, "id": "300266239", "label": "rgb"},

	"english": {"parent": Language, "id": "300388277", "label": "English"},
	"french": {"parent": Language, "id":"300388306","label": "French"},
	"german": {"parent": Language, "id":"300388344","label": "German"},
	"spanish": {"parent": Language, "id":"300389311","label": "Spanish"},
	"chinese": {"parent": Language, "id":"300388113", "label":"Chinese"},
	"hindi": {"parent": Language, "id":"300388412", "label":"Hindi"},
	"arabic": {"parent": Language, "id":"300387843", "label":"Arabic"},
	"portuguese":{"parent": Language, "id":"300389115", "label":"Portuguese"},
	"bengali": {"parent": Language, "id":"300387971", "label":"Bengali"},
	"russian": {"parent": Language, "id":"300389168", "label":"Russian"},
	"dutch": {"parent": Language, "id":"300388256", "label":"Dutch"},
	"italian": {"parent": Language, "id":"300388474", "label":"Italian"},
	"greek": {"parent": Language, "id":"300389734", "label":"Greek"},
	"ancient greek": {"parent": Language, "id": "300387827", "label": "Ancient Greek"},
	"latin": {"parent": Language, "id":"300388693", "label":"Latin"},
	"japanese": {"parent": Language, "id":"300388486", "label":"Japanese"},
	"croatian": {"parent": Language, "id": "300388185", "label": "Croatian"},
	"czech": {"parent": Language, "id": "300388191", "label": "Czech"},
	"danish": {"parent": Language, "id": "300388204", "label": "Danish"},
	"greek": {"parent": Language, "id": "300388361", "label": "Greek"},
	"georgian": {"parent": Language, "id": "300388343", "label": "Georgian"},
	"hebrew": {"parent": Language, "id": "300388401", "label": "Hebrew"},
	"hungarian": {"parent": Language, "id": "300388770", "label": "Magyar (Hungarian)"},
	"norwegian": {"parent": Language, "id": "300388992", "label": "Norwegian"},
	"polish": {"parent": Language, "id": "300389109", "label": "Polish"},
	"romanian": {"parent": Language, "id": "300389157", "label": "Romanian"},
	"serbo-croatian": {"parent": Language, "id": "300389248", "label": "Serbo-Croatian"},
	"slovak": {"parent": Language, "id": "300389290", "label": "Slovak"},
	"slovenian": {"parent": Language, "id": "300389291", "label": "Slovenian"},
	"swedish": {"parent": Language, "id": "300389336", "label": "Swedish"},
	"turkish": {"parent": Language, "id": "300389470", "label": "Turkish"},

	"primary": {"parent": Type, "id": "300404670", "label": "Primary"},
	"artwork": {"parent": Type, "id": "300133025", "label": "Artwork"},
	"work type": {"parent": Type, "id": "300435443", "label": "Type of Work"},

	"public collection": {"parent": Type, "id": "300411912", "label": "Public Collection"},
	"style of": {"parent": Type, "id": "300404285", "label": "Style Of"},
	"computer generated": {"parent": Type, "id": "300202389", "label": "Computer Generated"},
	"gender issues": {"parent": Type, "id": "300233686", "label": "Gender Issues"},
	"war": {"parent": Type, "id": "300055314", "label": "War"},
	"impressionism": {"parent": Type, "id":"300021503", "label": "Impressionism"},
	"landscapes": {"parent": Type, "id":"300015636", "label": "Landscapes"},
	"door piece": {"parent": Type, "id":"300002911", "label": "Door piece"},
	"bust": {"parent": Type, "id":"300047457", "label": "Bust"},
	"altarpiece": {"parent": Type, "id":"300075940", "label": "Altarpiece"},
	"arched": {"parent": Type, "id":"300126995", "label": "Arched"},
	"bas-relief": {"parent": Type, "id":"300184633", "label": "Bas-relief"},
	"oval": {"parent": Type, "id":"300263817", "label": "Oval"},
	"octagonal": {"parent": Type, "id":"300263824", "label": "Octagonal"},
	"circle": {"parent": Type, "id":"300263827", "label": "Circle"},
	"square": {"parent": Type, "id":"300263832", "label": "Square"},
	"double-sided paintings": {"parent": Type, "id":"300265620", "label": "Double-sided Paintings"},
	"oblong": {"parent": Type, "id":"300311843", "label": "Oblong"},
	"upright": {"parent": Type, "id":"300343370", "label": "Upright"},
	"city": {"parent": Type, "id": "300008389", "label": "City"},
	"province": {"parent": Type, "id":"300000774", "label": "Province"},
	"nation": {"parent": Type, "id": "300128207", "label": "Nation"},
	"building": {"parent": Type, "id": "300004792", "label": "Building"},
	"city block": {"parent": Type, "id": "300008077", "label": "City Block"},
	"crime": {"parent": Type, "id": "300055289", "label": "Crime"},
	"glassblowing": {"parent": Type, "id":"300053932", "label":"Glassblowing"},
	"sculpting": {"parent": Type, "id":"300264383", "label": "Sculpting"},
	"painting": {"parent": Type, "id":"300054216", "label": "Painting"},
	"first": {"parent": Type, "id":"300404050", "label": "First"},
	"last": {"parent": Type, "id": "XXX", "label": "Last"},

	"style genre": {"parent": Type, "id":"300139140", "label": "Genre"},
	"style landscape": {"parent": Type, "id":"300015636", "label": "Landscape"},
	"style portrait": {"parent": Type, "id":"300015637", "label": "Portrait"},
	"style still life": {"parent": Type, "id":"300015638", "label": "Still Life"},

	"color red": {"parent": Type, "id": "300126225", "label": "Red"},
	"color green": {"parent": Type, "id": "300128438", "label": "Green"},
	"color blue": {"parent": Type, "id": "300129361", "label": "Blue"},
	"color yellow": {"parent": Type, "id": "300127794", "label": "Yellow"},
	"color orange": {"parent": Type, "id": "300126734", "label": "Orange"},
	"color purple": {"parent": Type, "id": "300130257", "label": "Purple"},
	"color brown": {"parent": Type, "id": "300127490", "label": "Brown"},
	"color black": {"parent": Type, "id": "300130920", "label": "Black"},
	"color white": {"parent": Type, "id": "300129784", "label": "White"},
	"color gray": {"parent": Type, "id": "300130811", "label": "Gray"},

	"brief text": {"parent": Type, "id": "300418049", "label":"Brief Text"},

	"us dollars": {"parent": Currency, "id":"300411994", "label": "US Dollars"},
	"gb pounds": {"parent": Currency, "id":"300411998", "label": "British Pounds"},
	"gb shillings": {"parent": Currency, "id":"300412167", "label": "British Shillings"},
	"dutch guilder": {"parent": Currency, "id":"300412019", "label": "Dutch Guilder"},
	"fr assignats": {"parent": Currency, "id":"300412157", "label": "French Assignats"},
	"at shillings": {"parent": Currency, "id":"300412158", "label": "Austrian Shillings"},
	"fr ecus": {"parent": Currency, "id":"300412159", "label": "French Ecus"},
	"de florins": {"parent": Currency, "id":"300412160", "label": "German Florins"},
	"gb guineas": {"parent": Currency, "id":"300412163", "label": "British Guineas"},
	"dk kroner": {"parent": Currency, "id":"300412164", "label": "Danish Kroner"},
	"dk rigsdaler": {"parent": Currency, "id":"300412190", "label": "Danish Rigsdaler"},
	"fr livres": {"parent": Currency, "id":"300412165", "label": "French Livres"},
	"fr louis": {"parent": Currency, "id":"300412166", "label": "French Louis coins"},
	"thalers": {"parent": Currency, "id":"300412168", "label": "Thalers"},
	"de reichsmarks": {"parent": Currency, "id":"300412169", "label": "German Reichsmarks"},
	"de marks": {"parent": Currency, "id":"300412017", "label": "German Marks"},
	"reichsthalers": {"parent": Currency, "id":"300412170", "label": "Reichsthalers"},
	"ch francs": {"parent": Currency, "id":"300412001", "label": "Swiss Francs"},
	"fr francs": {"parent": Currency, "id":"300412016", "label": "French Francs"},
	"it lira": {"parent": Currency, "id":"300412015", "label": "Italian Lira"},
	"ducats": {"parent": Currency, "id":"300193382", "label": "Ducats"},
	"groschen": {"parent": Currency, "id":"300191473", "label": "Groschen"},
	"silbergroshen": {"parent": Currency, "id":"300412171", "label": "Silbergroshen"},
	"stuiver": {"parent": Currency, "id":"300412172", "label": "Stuiver"},
}

for (name,v) in identity_instances.items():
	register_instance(name, v)
for (name,v) in ext_classes.items():
	register_vocab_class(name, v)


local_instances = {
	"french nationality": {"parent": Nationality, "id": "300111188", "label": "French"},
	"american nationality": {"parent": Nationality, "id": "300107956", "label": "American"},
	"italian nationality": {"parent": Nationality, "id": "300111198", "label": "Italian"},
	"dutch nationality": {"parent": Nationality, "id": "300111175", "label": "Dutch"},
	"belgian nationality": {"parent": Nationality, "id": "300111156", "label": "Belgian"},
	"british nationality": {"parent": Nationality, "id": "300111159", "label": "British"},	
	"flemish nationality": {"parent": Nationality, "id": "300111184", "label": "Flemish"},
	"german nationality": {"parent": Nationality, "id": "300111192", "label": "German"},
	"austrian nationality": {"parent": Nationality, "id": "300111153", "label": "Austrian"},
	"spanish nationality": {"parent": Nationality, "id": "300111215", "label": "Spanish"},
	"swiss nationality": {"parent": Nationality, "id": "300111221", "label": "Swiss"},
	"irish nationality": {"parent": Nationality, "id": "300111259", "label": "Irish"},
	"hungarian nationality": {"parent": Nationality, "id": "300111195", "label": "Hungarian"},
	"swedish nationality": {"parent": Nationality, "id": "300111218", "label": "Swedish"},
	"czech nationality": {"parent": Nationality, "id": "300111166", "label": "Czech"},
	"russian nationality": {"parent": Nationality, "id": "300111276", "label": "Russian"},
	"polish nationality": {"parent": Nationality, "id": "300111204", "label": "Polish"},
	"norwegian nationality": {"parent": Nationality, "id": "300111201", "label": "Norwegian"},
	"danish nationality": {"parent": Nationality, "id": "300111172", "label": "Danish"},
	"chinese nationality": {"parent": Nationality, "id": "300018322", "label": "Chinese"},
	"egyptian nationality": {"parent": Nationality, "id": "300020251", "label": "Egyptian"},
	"greek nationality": {"parent": Nationality, "id": "300264816", "label": "Greek"},
	"canadian nationality": {"parent": Nationality, "id": "300107962", "label": "Canadian"},
	"mexican nationality": {"parent": Nationality, "id": "300107963", "label": "Mexican"},
	"portuguese nationality": {"parent": Nationality, "id": "300111207", "label": "Portuguese"},
	"japanese nationality": {"parent": Nationality, "id": "300018519", "label": "Japanese"},

	"belgium": {"parent": Nation, "id": "1000063", "vocab": "tgn", "label": "Belgium"},
	"france": {"parent": Nation, "id": "1000070", "vocab": "tgn", "label": "France"},
	"germany": {"parent": Nation, "id": "7000084", "vocab": "tgn", "label": "Germany"},
	"switzerland": {"parent": Nation, "id": "7011731", "vocab": "tgn", "label": "Switzerland"},
	"united kingdom": {"parent": Nation, "id": "7008591", "vocab": "tgn", "label": "United Kingdom"},
	"england": {"parent": Nation, "id": "7002445", "vocab": "tgn", "label": "England"},
	"scotland": {"parent": Nation, "id": "7002444", "vocab": "tgn", "label": "Scotland"},
	"wales": {"parent": Nation, "id": "7002443", "vocab": "tgn", "label": "Wales"},
}

for (name,v) in local_instances.items():
	register_instance(name, v)

# pen, pencil, card, cardboard, porcelain, wax, ceramic, plaster
# crayon, millboard, gouache, brass, stone, lead, iron, clay,
# alabaster, limestone

aat_culture_mapping = {
	"italian": "300111198",
	"german": "300111192",
	"dutch": "300020929"
}

def make_multitype_obj(*args, **kw):
	# (class1, class2, class3, name=foo, other=bar)
	inst = args[0](**kw)
	for c in args[1:]:
		for cn in c._classification:
			if not cn in inst.classified_as:
				inst.classified_as = cn
	return inst


def add_art_setter():
	# Linked.Art profile requires aat:300133025 on all artworks
	# Art can be a HumanMadeObject or an InformationObject
	# set it by adding art=1 to the constructor

	def art_post_init(self, **kw):
		super(HumanMadeObject, self)._post_init(**kw)
		if "art" in kw:
			self.classified_as = instances['artwork']
	HumanMadeObject._post_init = art_post_init

	def art2_post_init(self, **kw):
		if "art" in kw:
			self.classified_as = instances['artwork']
		super(InformationObject, self)._post_init(**kw)
	InformationObject._post_init = art2_post_init

def add_attribute_assignment_check():
	# Allow references to properties in p177 on AttrAssign
	# Validate that the property is allowed in assigned
	# either on set, or when assigned is set
		
	p177 = factory.context_rev.get('crm:P177_assigned_property', 'assigned_property')
	ass = factory.context_rev.get('crm:P141_assigned', 'assigned')
	assto = factory.context_rev.get('crm:P140:assigned_attribute_to', 'assigned_to')

	phase_rel = factory.context_rev.get('la:relationship', 'relationship')
	phase_of = factory.context_rev.get('la:phase_of', 'phase_of')
	phase_entity = factory.context_rev.get('la:related_entity', 'related_entity')

	def aa_set_assigned(self, value):
		assto_res = getattr(self, assto, None)
		if assto_res:
			p177_res = getattr(self, p177, None)
			assto_res._check_prop(p177_res, value)
		object.__setattr__(self, ass, value)
	setattr(AttributeAssignment, "set_%s" % ass, aa_set_assigned)

	def aa_set_assigned_to(self, value):
		ass_res = getattr(self, ass, None)
		p177_res = getattr(self, p177, None)		
		if ass_res and p177_res:
			# unmap the URI to property name
			value._check_prop(p177_res, ass_res)
		object.__setattr__(self, assto, value)
	setattr(AttributeAssignment, "set_%s" % assto, aa_set_assigned_to)

	def aa_set_assigned_property_type(self, value):
		ass_res = getattr(self, ass, None)
		assto_res = getattr(self, assto, None)
		if not assto_res:
			# override
			assto_res = BaseResource()
		if ass_res:
			assto_res._check_prop(value, ass_res)
		object.__setattr__(self, p177, value)
	setattr(AttributeAssignment, "set_%s" % p177, aa_set_assigned_property_type)


	def phase_set_relationship(self, value):
		# XXX do same checking as above
		object.__setattr__(self, phase_rel, value)
	setattr(Phase, "set_%s" % phase_rel, phase_set_relationship)		

def add_linked_art_boundary_check():

	boundary_classes = [x.__name__ for x in [Actor, HumanMadeObject, Person, Group, VisualItem, \
		Place, Period, LinguisticObject, Phase, Set, Event]]
	data_embed_classes = [Name, Identifier, Dimension, TimeSpan, MonetaryAmount]
	type_embed_classes = [Type, Currency, Language, Material, MeasurementUnit]
	event_embed_classes = [Birth, Creation, Production, Formation, Payment, \
							Death, Destruction, Dissolution ]
	all_embed_classes = []
	all_embed_classes.extend(data_embed_classes)
	all_embed_classes.extend(type_embed_classes)
	all_embed_classes.extend(event_embed_classes)
	embed_classes = [x.__name__ for x in all_embed_classes]

	# Activity, AttributeAssignment, InformationObject, TransferOfCustody, Move
	# Propositional Object

	def my_linked_art_boundary_check(self, top, rel, value):
		# True = Embed ; False = Split
		if isinstance(value, LinguisticObject) and hasattr(value, 'classified_as') and instances['brief text'] in value.classified_as:
			# linguistic objects and * can be described by embedded linguistic objects
			return True
		elif isinstance(value, Procurement):
			return False
		elif rel in ["part", "member"]:
			# Downwards, internal simple partitioning 
			return True
		elif rel in ["part_of", 'member_of']:
			# upwards partition refs are inclusion, and always boundary crossing
			return False
		elif value.type in boundary_classes:
			return False
		elif value.type in embed_classes:
			return True
		else:
			# Default to embedding to avoid data loss
			return True

	setattr(BaseResource, "_linked_art_boundary_okay", my_linked_art_boundary_check)
	factory.linked_art_boundaries = True	

