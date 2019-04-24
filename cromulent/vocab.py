 
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

from .model import Identifier, Mark, ManMadeObject, Type, \
	Person, Material, MeasurementUnit, Place, Dimension, Currency, \
	ConceptualObject, TimeSpan, Actor, PhysicalThing, Language, \
	LinguisticObject, InformationObject, \
	Activity, Group, Name, MonetaryAmount, PropertyInterest, \
	Destruction, AttributeAssignment, BaseResource, PhysicalObject, \
	Acquisition, ManMadeFeature, VisualItem, Set, \
	PropositionalObject, Payment, Creation, Phase, \
	STR_TYPES, factory

# Add classified_as initialization hack for all resources
def post_init(self, **kw):
	if self.__class__._classification:
		for t in self._classification:
			self.classified_as = t
BaseResource._post_init = post_init

def register_aat_class(name, data):
	parent = data['parent']
	id = data['id']
	label = data['label']

	c = type(name, (parent,), {})
	if id.startswith('http'):
		t = Type(id)
	else:
		t = Type("http://vocab.getty.edu/aat/%s" % id)
	t._label = label
	if parent == LinguisticObject and "brief" in data:
		c._classification = [t, instances["brief text"]]
	else:	
		c._classification = [t]		
	c._type = None # To avoid conflicting with parent class
	globals()[name] = c	

instances = {}

def register_instance(name, data):
	parent = data['parent']
	id = data['id']
	label = data['label']

	if id.startswith('http'):
		t = parent(id)
	else:
		t = parent("http://vocab.getty.edu/aat/%s" % id)
	t._label = label
	instances[name] = t

# Meta meta
ext_classes = {
	"LocalNumber": {"parent":Identifier, "id":"300404621", "label": "Local Number"},	
	"AccessionNumber": {"parent":Identifier, "id":"300312355", "label": "Accession Number"},
	"LotNumber": {"parent": Identifier, "id": "300404628", "label": "Lot Number"},

	"DigitalImage": {"parent": VisualItem, "id": "300215302", "label": "Digital Image"},

	"OwnershipRight": {"parent": PropertyInterest, "id":"300055603", "label": "Ownership Right"},
	"CustodyRight": {"parent": PropertyInterest, "id":"300411616", "label": "Custody Right"},
	"CopyrightRight": {"parent": PropertyInterest, "id":"300055598", "label": "Copyright"},

	"OwnershipPhase": {"parent": Phase, "id": "300055603", "label": "Ownership Phase"},

	"Inscription": {"parent": LinguisticObject, "id": "300028702", "label": "Inscription", "brief": True},
	"Signature": {"parent": LinguisticObject, "id": "300028705", "label": "Signature", "brief": True},
	"MaterialStatement": {"parent": LinguisticObject, "id": "300010358", "label": "Material Statement", "brief": True},
	"DimensionStatement": {"parent": LinguisticObject, "id": "300266036", "label": "Dimension Statement", "brief": True},
	"CreditStatement": {"parent": LinguisticObject, "id": "300026687", "label": "Credit Statement", "brief": True},
	"RightsStatement": {"parent": LinguisticObject, "id": "300055547", "label": "Rights Statement", "brief": True},
	"EditionStatement": {"parent": LinguisticObject, "id":"300121294", "label": "Edition Statement", "brief": True},
	"BiographyStatement": {"parent": LinguisticObject, "id":"300080102", "label": "Biography Statement", "brief": True},
	"ProvenanceStatement": {"parent": LinguisticObject, "id":"300055863", "label": "Provenance Statement", "brief": True},
	"Description": {"parent": LinguisticObject, "id":"300080091", "label": "Description", "brief": True},
	"PaginationStatement": {"parent": LinguisticObject, "id":"300200294", "label": "Pagination Statement", "brief": True},
	"FoliationStatement": {"parent": LinguisticObject, "id":"300200662", "label": "Foliation Statement", "brief": True},
	"Abstract": {"parent": LinguisticObject, "id":"300026032", "label": "Abstract", "brief": True},
	"Note": {"parent": LinguisticObject, "id":"300027200", "label": "Note", "brief": True},
	"Annotation": {"parent": LinguisticObject, "id":"300026100", "label":"Annotation"},

	"CatalogueRaisonne": {"parent": LinguisticObject, "id":"300026061", "label": "Catalogue Raisonne"},
	"AuctionCatalog": {"parent": LinguisticObject, "id":"300026068", "label": "Auction Catalog"},
	"SalesCatalog": {"parent": LinguisticObject, "id": "300026074", "label": "Sales Catalog"},
	"ExhibitionCatalog": {"parent": LinguisticObject, "id": "300026096", "label": "Exhibition Catalog"},
	"AccountBook": {"parent": LinguisticObject, "id": "300027483", "label": "Account Book"},
	"WebPage": {"parent": LinguisticObject, "id":"300264578", "label": "Web Page"},
	"Register": {"parent": LinguisticObject, "id":"300027168", "label": "Register"},
	"Page": {"parent": LinguisticObject, "id":"300194222", "label": "Page"},
	"Folio": {"parent": LinguisticObject, "id":"300189604", "label": "Folio"},
	"DataRecord": {"parent": LinguisticObject, "id":"300026685", "label": "Data Record"}, # Not sure about this one
	"Heading": {"parent": LinguisticObject, "id": "300200862", "label": "Heading"},
	"SubHeading": {"parent": LinguisticObject, "id": "300419992", "label": "Heading"},

	"Journal": {"parent": LinguisticObject, "id":"300215390", "label": "Journal"},
	"Issue": {"parent": LinguisticObject, "id":"300312349", "label": "Issue"},
	"Volume": {"parent": LinguisticObject, "id":"300265632", "label": "Volume"},
	"Article": {"parent": LinguisticObject, "id":"300048715", "label": "Article"},
	"Chapter": {"parent": LinguisticObject, "id":"300311699", "label": "Chapter"},
	"Series": {"parent": LinguisticObject, "id":"300027349", "label": "Series"},
	"Proceedings": {"parent": LinguisticObject, "id":"300027316", "label": "Proceedings"},
	"Monograph": {"parent": LinguisticObject, "id":"300060417", "label": "Monograph"},
	"Patent": {"parent": LinguisticObject, "id":"300027832", "label": "Patent"},
	"Thesis": {"parent": LinguisticObject, "id":"300028028", "label": "Thesis"},
	"TechnicalReport": {"parent": LinguisticObject, "id":"300027323", "label": "Technical Report"},
	"DocManuscript": {"parent": LinguisticObject, "id":"300028579", "label": "Document Manuscript"},
	"AudioVisualContent": {"parent": LinguisticObject, "id":"300028045", "label": "A/V Content"},

	"Height":     {"parent": Dimension, "id":"300055644", "label": "Height"},
	"Width":      {"parent": Dimension, "id":"300055647", "label": "Width"},
	"Depth":      {"parent": Dimension, "id":"300072633", "label": "Depth"},
	"Diameter":   {"parent": Dimension, "id":"300055624", "label": "Diameter"},
	"Weight":     {"parent": Dimension, "id":"300056240", "label": "Weight"},
	"Color":      {"parent": Dimension, "id":"300056130", "label": "Color"},

	"Gallery":      {"parent": Place, "id":"300240057", "label": "Gallery (place)"},
	"AuctionHouse": {"parent": Place, "id":"300005234", "label": "Auction House (place)"},
	"MuseumPlace":  {"parent": Place, "id":"300005768", "label": "Museum (place)"},
	"ExhibitionPlace": {"parent": Place, "id":"300005748", "label": "Exhibition (place)"},

	"AuctionHouseOrg": {"parent": Group, "id": "300417515", "label": "Auction House (organization)"},
	"MuseumOrg":   {"parent": Group, "id":"300312281", "label": "Museum"},
	"Department":  {"parent": Group, "id":"300263534", "label": "Department"},

	"Nationality": {"parent": Type, "id":"300379842", "label": "Nationality"},
	"Gender":      {"parent": Type, "id":"300055147", "label": "Gender"},
	"Occupation":  {"parent": Type, "id":"300263369", "label": "Occupation"},

	"Auctioneer":  {"parent": Person, "id":"300025208", "label": "Auctioneer"}, # is this useful?


	"AuctionEvent": {"parent": Activity, "id":"300xxxxxx", "label": "Auction Event"},
	"Auction":     {"parent": Activity, "id":"300054751", "label": "Auction of Lot"}, # Individual auction-of-lot
	"Bidding":     {"parent": Creation, "id":"300054602", "label": "Bidding"}, # individual bid
	"Curating":    {"parent": Activity, "id":"300054277", "label": "Curating"},
	"Inventorying": {"parent": Activity, "id":"300077506", "label": "Inventorying"},
	"Provenance":  {"parent": Activity, "id":"300055863", "label": ""},
	"Exhibition":  {"parent": Activity, "id":"300054766", "label": "Exhibiting"},
	"MultiExhibition": {"parent": Activity, "id":"300054773", "label": "Exhibiting in multiple locations"},
	"Active":      {"parent": Activity, "id":"300393177", "label": "Professional Activities"},
	"Publishing":  {"parent": Activity, "id":"300054686", "label": "Publishing"},
	"Purchase":  {"parent":Acquisition, "id":"300077989", "label": "Puchasing"},

	"ExhibitionIdea": {"parent": PropositionalObject, "id":"300417531", "label": "Exhibition"},

	"Theft": {"parent": Acquisition, "id": "300055292", "label": "Theft"},
	"Looting": {"parent": Acquisition, "id":"300379554", "label": "Looting"},

	"AuctionLotSet": {"parent": Set, "id":"300411307", "label": "Auction Lot"},
	"CollectionSet": {"parent": Set, "id":"300025976", "label": "Collection"},

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

	"EmailAddress": {"parent": Name, "id":"300149026", "label": "Email Address"},
	"StreetAddress": {"parent": Name, "id":"300386983", "label": "Street Address"},
	"StreetNumber": {"parent": Name, "id":"300419272", "label": "Street Number"},
	"StreetName": {"parent": Name, "id": "300419273", "label": "Street Name"},
	"PostalCode": {"parent": Name, "id": "300419274", "label": "Postal Code"},

	"Painting": {"parent": ManMadeObject, "id": "300033618", "label": "Painting"},
	"Sculpture": {"parent": ManMadeObject, "id": "300047090", "label": "Sculpture"},
	"Drawing": {"parent": ManMadeObject, "id": "300033973", "label": "Drawing"},
	"Miniature": {"parent": ManMadeObject, "id": "300033936", "label": "Miniature"},
	"Tapestry": {"parent": ManMadeObject, "id": "300205002", "label": "Tapestry"},
	"Furniture": {"parent": ManMadeObject, "id": "300037680", "label": "Furniture"},
	"Mosaic": {"parent": ManMadeObject, "id": "300015342", "label": "Mosaic"},
	"Photograph": {"parent": ManMadeObject, "id": "300046300", "label": "Photograph"},
	"Coin": {"parent": ManMadeObject, "id": "300037222", "label": "Coin"},
	"Vessel": {"parent": ManMadeObject, "id": "300193015", "label": "Vessel"},
	"Graphic": {"parent": ManMadeObject, "id": "300015387", "label": "Graphic Art"},
	"Enamel": {"parent": ManMadeObject, "id": "300178264", "label": "Enamel"},
	"Embroidery": {"parent": ManMadeObject, "id": "300264024", "label": "Embroidery"},
	"PhotographPrint": {"parent": ManMadeObject, "id": "300127104", "label": "Photograph Print"},
	"PhotographAlbum": {"parent": ManMadeObject, "id": "300026695", "label": "Photograph Album"},
	"PhotographBook": {"parent": ManMadeObject, "id": "300265728", "label": "Photograph Book"},
	"PhotographColor": {"parent": ManMadeObject, "id": "300128347", "label": "Color Photograph"},
	"PhotographBW": {"parent": ManMadeObject, "id": "300128359", "label": "Black and White Photograph"},
	"Negative": {"parent": ManMadeObject, "id": "300127173", "label": "Photographic Negative"},
	"Map": {"parent": ManMadeObject, "id": "300028094", "label": "Map"},
	"Clothing": {"parent": ManMadeObject, "id": "300266639", 'label': "Clothing"},
	"Furniture": {"parent": ManMadeObject, "id":"300037680", "label": "Furniture"},

	"Architecture": {"parent": ManMadeObject, "id":"300263552", "label": "Architecture"},
	"Armor": {"parent": ManMadeObject, "id":"300036745", "label": "Armor"},
	"Book": {"parent": ManMadeObject, "id":"300028051", "label": "Book"},
	"DecArts": {"parent": ManMadeObject, "id":"300054168", "label": "Decorative Arts"},
	"Implement": {"parent": ManMadeObject, "id":"300024841", "label": "Implement"},
	"Jewelry": {"parent": ManMadeObject, "id":"300209286", "label": "Jewelry"},
	"Manuscript": {"parent": ManMadeObject, "id":"300265483", "label": "Manuscript"},
	"SiteInstallation": {"parent": ManMadeObject, "id":"300047896", "label": "Site Installation"},
	"Text": {"parent": ManMadeObject, "id":"300263751", "label": "Text"},
	"Print":  {"parent": ManMadeObject, "id":"300041273", "label": "Print"},
	"TimeBasedMedia": {"parent": ManMadeObject, "id":"300185191", "label": "Time-based Media"},

	"FrontPart": {"parent": ManMadeObject, "id":"300190703", "label": "Front Part"},
	"BackPart": {"parent": ManMadeObject, "id":"300190692", "label": "Back Part"},
	"TopPart": {"parent": ManMadeObject, "id":"300190710", "label": "Top Part"},
	"BottomPart": {"parent": ManMadeObject, "id":"300190695", "label": "Bottom Part"},
	"SidePart": {"parent": ManMadeObject, "id":"300190706", "label": "Side Part"},

	"SupportPart": {"parent": ManMadeObject, "id":"300014844", "label": "Support"},
	"FramePart": {"parent": ManMadeObject, "id":"300404391", "label": "Frame"},
	"MountPart": {"parent": ManMadeObject, "id":"300131087", "label": "Mount"},
	"PanelPart": {"parent": ManMadeObject, "id":"300014657", "label": "Panel"},
	"BasePart": {"parent": ManMadeObject, "id":"300001656", "label": "Base"},

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

	"inches": {"parent": MeasurementUnit, "id": "300379100", "label": "inches"},
	"feet": {"parent": MeasurementUnit, "id":"300379101", "label": "feet"},
	"cm": {"parent": MeasurementUnit, "id": "300379098", "label": "centimeters"},
	"meters": {"parent": MeasurementUnit, "id": "300379099", "label": "meters"},
	"percent": {"parent": MeasurementUnit, "id": "300417377", "label": "percent"},

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

	"primary": {"parent": Type, "id": "300404670", "label": "Primary"},
	"artwork": {"parent": Type, "id": "300133025", "label": "Artwork"},
	"public collection": {"parent": Type, "id": "300411912", "label": "Public Collection"},
	"style of": {"parent": Type, "id": "300404285", "label": "Style Of"},
	"computer generated": {"parent": Type, "id": "300202389", "label": "Computer Generated"},
	"gender issues": {"parent": Type, "id": "300233686", "label": "Gender Issues"},
	"war": {"parent": Type, "id": "300055314", "label": "War"},
	"impressionism": {"parent": Type, "id":"300021503", "label": "Impressionism"},
	"landscapes": {"parent": Type, "id":"300015636", "label": "Landscapes"},
	"oval": {"parent": Type, "id":"300263817", "label": "Oval"},
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

	"french nationality": {"parent": Type, "id": "300111188", "label": "French"},
	"american nationality": {"parent": Type, "id": "300107956", "label": "American"},
	"italian nationality": {"parent": Type, "id": "300111198", "label": "Italian"},
	"dutch nationality": {"parent": Type, "id": "300111175", "label": "Dutch"},
	"belgian nationality": {"parent": Type, "id": "300111156", "label": "Belgian"},
	"british nationality": {"parent": Type, "id": "300111159", "label": "British"},	
	"flemish nationality": {"parent": Type, "id": "300111184", "label": "Flemish"},
	"german nationality": {"parent": Type, "id": "300111192", "label": "German"},
	"austrian nationality": {"parent": Type, "id": "300111153", "label": "Austrian"},
	"spanish nationality": {"parent": Type, "id": "300111215", "label": "Spanish"},
	"swiss nationality": {"parent": Type, "id": "300111221", "label": "Swiss"},
	"irish nationality": {"parent": Type, "id": "300111259", "label": "Irish"},
	"hungarian nationality": {"parent": Type, "id": "300111195", "label": "Hungarian"},
	"swedish nationality": {"parent": Type, "id": "300111218", "label": "Swedish"},
	"czech nationality": {"parent": Type, "id": "300111166", "label": "Czech"},
	"russian nationality": {"parent": Type, "id": "300111276", "label": "Russian"},
	"polish nationality": {"parent": Type, "id": "300111204", "label": "Polish"},
	"norwegian nationality": {"parent": Type, "id": "300111201", "label": "Norwegian"},
	"danish nationality": {"parent": Type, "id": "300111172", "label": "Danish"},
	"chinese nationality": {"parent": Type, "id": "300018322", "label": "Chinese"},
	"egyptian nationality": {"parent": Type, "id": "300020251", "label": "Egyptian"},
	"greek nationality": {"parent": Type, "id": "300264816", "label": "Greek"},
	"canadian nationality": {"parent": Type, "id": "300107962", "label": "Canadian"},
	"mexican nationality": {"parent": Type, "id": "300107963", "label": "Mexican"},
	"portuguese nationality": {"parent": Type, "id": "300111207", "label": "Portuguese"},
	"japanese nationality": {"parent": Type, "id": "300018519", "label": "Japanese"},

	"style genre": {"parent": Type, "id":"300139140", "label": "Genre"},
	"style landscape": {"parent": Type, "id":"300015636", "label": "Landscape"},
	"style portrait": {"parent": Type, "id":"300015637", "label": "Portrait"},
	"style still life": {"parent": Type, "id":"300015638", "label": "Still Life"},

	"brief text": {"parent": Type, "id": "300418049", "label":"Brief Text"},

	"us dollars": {"parent": Currency, "id":"300411994", "label": "US Dollars"},
	"gb pounds": {"parent": Currency, "id":"300411998", "label": "British Pounds"},
	"dutch guilder": {"parent": Currency, "id":"300412019", "label": "Dutch Guilder"},
	"fr assignats": {"parent": Currency, "id":"300412157", "label": "French Assignats"},
	"at shillings": {"parent": Currency, "id":"300412158", "label": "Austrian Shillings"},
	"fr ecus": {"parent": Currency, "id":"300412159", "label": "French Ecus"},
	"de florins": {"parent": Currency, "id":"300412160", "label": "German Florins"},
	"gb guineas": {"parent": Currency, "id":"300412163", "label": "British Guineas"},
	"dk kroner": {"parent": Currency, "id":"300412164", "label": "Danish Kroner"},
	"fr livres": {"parent": Currency, "id":"300412165", "label": "French Livres"},
	"fr louis": {"parent": Currency, "id":"300412166", "label": "French Louis coins"},
	"de reichsmarks": {"parent": Currency, "id":"300412169", "label": "German Reichsmarks"},
	"reichsthalers": {"parent": Currency, "id":"300412170", "label": "Reichsthalers"},
	"ch francs": {"parent": Currency, "id":"300412001", "label": "Swiss Francs"},
	"fr francs": {"parent": Currency, "id":"300412016", "label": "French Francs"},
	"it lira": {"parent": Currency, "id":"300412015", "label": "Italian Lira"}
}

for (name,v) in identity_instances.items():
	register_instance(name, v)

for (name,v) in ext_classes.items():
	register_aat_class(name, v)

# pen, pencil, card, cardboard, porcelain, wax, ceramic, plaster
# crayon, millboard, gouache, brass, stone, lead, iron, clay,
# alabaster, limestone

aat_culture_mapping = {
	"italian": "300111198",
	"german": "300111192",
	"dutch": "300020929"
}

def add_art_setter():
	# Linked.Art profile requires aat:300133025 on all artworks
	# Art can be a ManMadeObject or an InformationObject
	# set it by adding art=1 to the constructor

	def art_post_init(self, **kw):
		super(ManMadeObject, self)._post_init(**kw)
		if "art" in kw:
			self.classified_as = instances['artwork']
	ManMadeObject._post_init = art_post_init

	def art2_post_init(self, **kw):
		if "art" in kw:
			self.classified_as = instances['artwork']
		super(InformationObject, self)._post_init(**kw)
	InformationObject._post_init = art2_post_init

def add_attribute_assignment_check():
	# Allow references to properties in p2 on AttrAssign
	# Validate that the property is allowed in assigned
	# either on set, or when assigned is set
		
	p2 = factory.context_rev.get('crm:P2_has_type', 'classified_as')
	ass = factory.context_rev.get('crm:P141_assigned', 'assigned')
	assto = factory.context_rev.get('crm:P140:assigned_attribute_to', 'assigned_to')
	phase_rel = factory.context_rev.get('la:relationship', 'relationship')
	phase_of = factory.context_rev.get('la:phase_of', 'phase_of')
	phase_entity = factory.context_rev.get('la:related_entity', 'related_entity')

	def aa_set_assigned(self, value):
		assto_res = getattr(self, assto, None)
		if assto_res:
			p2_res = getattr(self, p2, None)
			assto_res._check_prop(p2_res, value)
		object.__setattr__(self, ass, value)
	setattr(AttributeAssignment, "set_%s" % ass, aa_set_assigned)

	def aa_set_assigned_to(self, value):
		ass_res = getattr(self, ass, None)
		p2_res = getattr(self, p2, None)		
		if ass_res and p2_res:
			# unmap the URI to property name
			value._check_prop(p2_res, ass_res)
		object.__setattr__(self, assto, value)
	setattr(AttributeAssignment, "set_%s" % assto, aa_set_assigned_to)

	def aa_set_classified_as(self, value):
		ass_res = getattr(self, ass, None)
		assto_res = getattr(self, assto, None)
		if not assto_res:
			# override
			assto_res = BaseResource()
		if ass_res:
			assto_res._check_prop(value, ass_res)
		object.__setattr__(self, p2, value)
	setattr(AttributeAssignment, "set_%s" % p2, aa_set_classified_as)

	def phase_set_relationship(self, value):
		# XXX do same checking as above
		object.__setattr__(self, phase_rel, value)
	setattr(Phase, "set_%s" % phase_rel, phase_set_relationship)		


