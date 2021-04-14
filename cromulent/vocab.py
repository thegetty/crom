
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

from .model import Identifier, Mark, HumanMadeObject, Type, \
	Person, Material, MeasurementUnit, Place, Dimension, Currency, \
	ConceptualObject, TimeSpan, Actor, PhysicalThing, Language, \
	LinguisticObject, InformationObject, Formation, Dissolution, \
	Activity, Group, Name, MonetaryAmount, Right, Encounter, \
	Destruction, AttributeAssignment, BaseResource, PhysicalObject, \
	Acquisition, HumanMadeFeature, VisualItem, Set, Birth, Death, \
	PropositionalObject, Payment, Creation, Phase, Period, \
	Production, Event, DigitalObject, TransferOfCustody, \
	Move, DigitalService, CRMEntity, \
	STR_TYPES, factory, ExternalResource

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
	"CodenIdentifier": {"parent": Identifier, "id": "300417431", "label": "CODEN Identifer"},
	"DoiIdentifier": {"parent": Identifier, "id": "300417432", "label": "DOI Identifer"},
	"VolumeNumber": {"parent": Identifier, "id": "300265632", "label": "Volume"},
	"IssueNumber": {"parent": Identifier, "id": "300312349", "label": "Issue"},
	"CallNumber": {"parent": Identifier, "id": "300311706", "label": "Call Number"},
	"StockNumber": {"parent": Identifier, "id": "300412177", "label": "Stock Number"},
	
	"EmailAddress": {"parent": Identifier, "id":"300435686", "label": "Email Address"},
	"StreetAddress": {"parent": Identifier, "id":"300435687", "label": "Street Address"},
	"TelephoneNumber": {"parent": Identifier, "id": "300435688", "label": "Telephone Number"},
	"FaxNumber": {"parent": Identifier, "id": "300435689", "label": "Fax Number"},
	"StreetNumber": {"parent": Identifier, "id":"300419272", "label": "Street Number"},
	"StreetName": {"parent": Identifier, "id": "300419273", "label": "Street Name"},
	"PostalCode": {"parent": Identifier, "id": "300419274", "label": "Postal Code"},

	"DigitalImage": {"parent": DigitalObject, "id": "300215302", "label": "Digital Image"},
	"WebPage": {"parent": DigitalObject, "id":"300264578", "label": "Web Page"},

	"OwnershipRight": {"parent": Right, "id":"300055603", "label": "Ownership Right"},
	"CustodyRight": {"parent": Right, "id":"300411616", "label": "Custody Right"},
	"CopyrightRight": {"parent": Right, "id":"300055598", "label": "Copyright"},

	"OwnershipPhase": {"parent": Phase, "id": "300055603", "label": "Ownership Phase"},

	"_BriefText": {"parent": LinguisticObject, "id": "300418049", "label":"Brief Text"},
	"Note": {"parent": LinguisticObject, "id":"300027200", "label": "Note", "metatype": "brief text"},
	"Description": {"parent": LinguisticObject, "id":"300435416", "label": "Description", "metatype": "brief text"},
	"Abstract": {"parent": LinguisticObject, "id":"300026032", "label": "Abstract", "metatype": "brief text"},
	"Citation": {"parent": LinguisticObject, "id":"300311705", "label": "Citation", "metatype": "brief text"},

	"CreditStatement": {"parent": LinguisticObject, "id": "300026687", "label": "Credit Statement", "metatype": "brief text"},
	"RightsStatement": {"parent": LinguisticObject, "id": "300435434", "label": "Copyright/License Statement", "metatype": "brief text"},
	"ValuationStatement": {"parent": LinguisticObject, "id": "300435426", "label": "Appraisal Statement", "metatype": "brief text"},
	"ConditionStatement": {"parent": LinguisticObject, "id": "300435425", "label": "Condition Statement", "metatype": "brief text"},
	"SignificanceStatement": {"parent": LinguisticObject, "id": "300435427", "label": "Significance Statement", "metatype": "brief text"},
	"ContextStatement": {"parent": LinguisticObject, "id": "300435428", "label": "Historical/Cultural Context", "metatype": "brief text"},
	"SourceStatement": {"parent": LinguisticObject, "id": "300404764", "label": "Source Statement", "metatype": "brief text"},
	"PropertyStatusStatement": {"parent": LinguisticObject, "id": "300438433", "label": "Property Status Statement", "metatype": "brief text"},
	"AccessStatement": {"parent": LinguisticObject, "id": "300133046", "label": "Access Statement", "metatype": "brief text"},

	"MarkingsStatement": {"parent": LinguisticObject, "id": "300435420", "label": "Markings", "metatype": "brief text"},
	"InscriptionStatement": {"parent": LinguisticObject, "id": "300435414", "label": "Inscription", "metatype": "brief text"},
	"SignatureStatement": {"parent": LinguisticObject, "id": "300028705", "label": "Signature", "metatype": "brief text"},
	"WatermarksStatement": {"parent": LinguisticObject, "id": "300435421", "label": "Watermarks", "metatype": "brief text"},
	"MaterialStatement": {"parent": LinguisticObject, "id": "300435429", "label": "Material Statement", "metatype": "brief text"},
	"PhysicalStatement": {"parent": LinguisticObject, "id": "300435452", "label": "Physical Statement", "metatype": "brief text"},
	"DimensionStatement": {"parent": LinguisticObject, "id": "300435430", "label": "Dimension Statement", "metatype": "brief text"},
	"CultureStatement": {"parent": LinguisticObject, "id": "300435431", "label": "Culture Statement", "metatype": "brief text"},
	"PeriodStatement": {"parent": LinguisticObject, "id": "300435432", "label": "Period Statement", "metatype": "brief text"},
	"EnvironmentStatement": {"parent": LinguisticObject, "id": "300229535", "label": "Environmental Conditions Statement", "metatype": "brief text"},

	"ProductionStatement": {"parent": LinguisticObject, "id": "300435436", "label": "Production Statement", "metatype": "brief text" },
	"AcquisitionStatement": {"parent": LinguisticObject, "id": "300435439", "label": "Acquisition Statement", "metatype": "brief text"},
	"ProvenanceStatement": {"parent": LinguisticObject, "id":"300435438", "label": "Provenance Statement", "metatype": "brief text"},
	"BibliographyStatement": {"parent": LinguisticObject, "id": "300026497", "label": "Bibliography Statement", "metatype": "brief text"},
	"ExhibitionStatement": {"parent": LinguisticObject, "id":"300435424", "label":"Exhibition Statement", "metatype": "brief text"},
	"PriceStatement": {"parent": LinguisticObject, "id":"300055694", "label":"Price Statement", "metatype": "brief text"},
	"ConditionReport": {"parent": LinguisticObject, "id":"300379544", "label":"Condition Statement", "metatype": "brief text"},	

	"BiographyStatement": {"parent": LinguisticObject, "id":"300435422", "label": "Biography Statement", "metatype": "brief text"},
	"EditionStatement": {"parent": LinguisticObject, "id":"300435435", "label": "Edition Statement", "metatype": "brief text"},
	"PaginationStatement": {"parent": LinguisticObject, "id":"300435440", "label": "Pagination Statement", "metatype": "brief text"},
	"FoliationStatement": {"parent": LinguisticObject, "id":"300435441", "label": "Foliation Statement", "metatype": "brief text"},
	"LanguageStatement": {"parent": LinguisticObject, "id": "300435433", "label": "Language Statement", "metatype": "brief text"},

	"TranscribedInscription": {"parent": LinguisticObject, "id": "300028702", "label": "Transcribed Inscription", "metatype": "brief text"},
	"TranscribedSignature": {"parent": LinguisticObject, "id": "300028705", "label": "Transcribed Signature", "metatype": "brief text"},

	"CatalogueRaisonneText": {"parent": LinguisticObject, "id":"300026061", "label": "Catalogue Raisonne", "metatype": "work type"},
	"AuctionCatalogText": {"parent": LinguisticObject, "id":"300026068", "label": "Auction Catalog", "metatype": "work type"},
	"SalesCatalogText": {"parent": LinguisticObject, "id": "300026074", "label": "Sales Catalog", "metatype": "work type"},
	"LotteryCatalogText": {"parent": LinguisticObject, "id":"300438603", "label": "Lottery Catalog", "metatype": "work type"},
	"ExhibitionCatalogText": {"parent": LinguisticObject, "id": "300026096", "label": "Exhibition Catalog", "metatype": "work type"},
	"AccessionCatalogText": {"parent": LinguisticObject, "id": "300026617", "label": "Accession Catalog", "metatype": "work type"},
	"AccountBookText": {"parent": LinguisticObject, "id": "300027483", "label": "Account Book", "metatype": "work type"},
	"RegisterText": {"parent": LinguisticObject, "id":"300027168", "label": "Register", "metatype": "work type"},
	"PageText": {"parent": LinguisticObject, "id":"300194222", "label": "Page", "metatype": "work type"},
	"FolioText": {"parent": LinguisticObject, "id":"300189604", "label": "Folio", "metatype": "work type"},
	"ParagraphText": {"parent": LinguisticObject, "id":"300417223", "label": "Paragraph"},
	"Annotation": {"parent": LinguisticObject, "id":"300026100", "label":"Annotation"},

	"DataRecord": {"parent": LinguisticObject, "id":"300438434", "label": "Entry or Record"},
	"Heading": {"parent": LinguisticObject, "id": "300200862", "label": "Heading"},
	"SubHeading": {"parent": LinguisticObject, "id": "300419992", "label": "SubHeading"},

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
	"Color":      {"parent": Dimension, "id":"300080438", "label": "Color"}, # individual colors as dimensions, 56130 is concept of color
	"Length":     {"parent": Dimension, "id":"300055645", "label": "Length"},
	"Thickness":  {"parent": Dimension, "id":"300055646", "label": "Thickness"},
	"SequencePosition": {"parent": Dimension, "id":"300010269", "label":"Sequence Position"},
	"PhysicalDimension": {"parent": Dimension, "id":"300055642", "label":"Unknown physical dimension"},

	"Gallery":      {"parent": Place, "id":"300240057", "label": "Gallery (place)"},
	"AuctionHouse": {"parent": Place, "id":"300005234", "label": "Auction House (place)"},
	"MuseumPlace":  {"parent": Place, "id":"300005768", "label": "Museum (place)"},
	"ExhibitionPlace": {"parent": Place, "id":"300005748", "label": "Exhibition (place)"},
	"CityBlock":    {"parent": Place, "id":"300008077", "label": "City Block"},
	"City":         {"parent": Place, "id":"300008389", "label": "City"},
	"Province":     {"parent": Place, "id":"300000774", "label": "Province"},
	"Nation":       {"parent": Place, "id":"300128207", "label": "Nation"},
	"Sovereign":	{"parent": Place, "id":"300232420", "label": "Sovereign State"},
	"StoragePlace": {"parent": Place, "id":"300150151", "label": "Storage (place)"},

	"Building":     {"parent": HumanMadeObject, "id": "300004792", "label":"Building"},

	"AuctionHouseOrg": {"parent": Group, "id": "300417515", "label": "Auction House (organization)"},
	"MuseumOrg":   {"parent": Group, "id":"300312281", "label": "Museum"},
	"Institution": {"parent": Group, "id":"300026004", "label": "Institution"},
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
	"Shape":       {"parent": Type, "id":"300056273", "label": "Shape"},
	"Style": 	   {"parent": Type, "id":"300015646", "label": "Style"},

	"Auctioneer":  {"parent": Person, "id":"300025208", "label": "Auctioneer"}, # is this useful?
	"Artist":  {"parent": Person, "id":"300025103", "label": "Artist"},
	"Collector":  {"parent": Person, "id":"300025234", "label": "Collector"},
	"Dealer":  {"parent": Person, "id":"300025236", "label": "Dealer"},

	"AuctionEvent": {"parent": Activity, "id":"300054751", "label": "Auction Event"},
	"Auction":     {"parent": Activity, "id":"300420001", "label": "Auction of Lot"}, # Individual auction-of-lot
	"LotteryDrawing": {"parent": Activity, "id":"300438601", "label": "Lottery Drawing"},
	"Lottery":     {"parent": Activity, "id":"300184191", "label": "Lottery"},

	"Negotiating": {"parent": Activity, "id":"300438558", "label": "Negotiating"},
	"Bidding":     {"parent": Creation, "id":"300054602", "label": "Bidding"}, # individual bid
	"Curating":    {"parent": Activity, "id":"300054277", "label": "Curating"},
	"Inventorying": {"parent": Encounter, "id":"300077506", "label": "Inventorying"},
	"Exhibition":  {"parent": Activity, "id":"300054766", "label": "Exhibiting"},
	"MultiExhibition": {"parent": Activity, "id":"300054773", "label": "Exhibiting in multiple locations"},
	"Publishing":  {"parent": Activity, "id":"300054686", "label": "Publishing"},
	"Distributing":  {"parent": Activity, "id": "300137595", "label": "Distributing"},
	"Hiring":      {"parent": Activity, "id":"300109703", "label": "Hiring"},
	"Expert":      {"parent": Activity, "id":"300417631", "label": "Expert"},
	"CommissairePriseur":  {"parent": Activity, "id":"300412173", "label": "Commissaire-priseur"},

	"Active":      {"parent": Activity, "id":"300393177", "label": "Professional Activities"},
	"Collecting": {"parent": Activity, "id": "300077121", "label": "Collecting"},
	"Creating": {"parent": Activity, "id": "300404387", "label": "Creating Artwork"},
	"Dealing": {"parent": Activity, "id": "300055675", "label": "Commercial Dealing in Artwork"},
	"Owning": {"parent": Activity, "id": "300055603", "label": "Owning"},
	"Promise": {"parent": Activity, "id": "300435599", "label": "Promise"},

	"Purchase":  {"parent":Acquisition, "id":"300077989", "label": "Purchasing"},
	"Assembling": {"parent": Activity, "id":"300077121", "label":"Assembling"},
	"Managing": {"parent": Activity, "id":"300054277", "label": "Managing"},
	"Storing": {"parent": Activity, "id":"300056390", "label": "Storing"},
	"Producing": {"parent": Activity, "id":"300054713", "label": "Producing"},
	"Conserving": {"parent": Activity, "id":"300404519", "label": "Conservation Activity"},

	"ProvenanceEntry": {"parent": Activity, "id":"300055863", "label": "Provenance Activity"},
	"ProvenanceActivity": {"parent": Activity, "id":"300055863", "label": "Provenance Activity"},
	"ReturnOfLoan": {"parent": TransferOfCustody, "id":"300438467", "label": "Return of Loan"},
	"Theft": {"parent": TransferOfCustody, "id": "300055292", "label": "Theft"},
	"Looting": {"parent": TransferOfCustody, "id":"300379554", "label": "Looting"},
	"Loss": {"parent": TransferOfCustody, "id":"300417655", "label": "Loss"},
	"Loan": {"parent": TransferOfCustody, "id":"300417645", "label": "Loan"},
	"LongtermLoan": {"parent": TransferOfCustody, "id":"300417646", "label": "Long-term Loan"},
	"SaleOfStolenGoods": {"parent": TransferOfCustody, "id":"xxx", "label":"Sale of Stolen Goods"},

	"PossibleAssignment": {"parent": AttributeAssignment, "id":"300435722", "label": "Possibly"}, 
	"ProbableAssignment": {"parent": AttributeAssignment, "id":"300435721", "label": "Probably"},
	"ObsoleteAssignment": {"parent": AttributeAssignment, "id":"300404908", "label": "Obsolete"},

	"Measuring": {"parent": AttributeAssignment, "id":"300053578", "label":"Measuring"},
	"Identifying": {"parent": AttributeAssignment, "id":"300137570","label":"Identifying"},
	"Naming": {"parent": AttributeAssignment, "id":"300411672", "label":"Naming"},

	"ExhibitionIdea": {"parent": PropositionalObject, "id":"300417531", "label": "Exhibition"},

	"AuctionLotSet": {"parent": Set, "id":"300411307", "label": "Auction Lot"},
	"CollectionSet": {"parent": Set, "id":"300025976", "label": "Collection"},
	"ArchiveSet": {"parent": Set, "id":"300375748", "label": "Archive"}, # Maybe 300189759?
	"ArchiveGroupSet": {"parent": Set, "id":"300404022", "label": "Archival Grouping"},
	"ArchiveSubGroupSet": {"parent": Set, "id":"300404023", "label": "Archival SubGrouping"},
	
	"PrimaryName": {"parent": Name, "id":"300404670", "label": "Primary Name"},
	"SortName": {"parent": Name, "id":"300404672", "label": "Sorting Name"},

	"Title": {"parent": Name, "id":"300195168", "label": "Title"},
	"Subtitle": {"parent": Name, "id":"300312006", "label":"Subtitle"},
	"DisplayName": {"parent": Name, "id": "300404669", "label": "Display Title"},
	"TranslatedTitle": {"parent": Name, "id":"300417194", "label": "Translated Title"},

	"PersonalName": {"parent": Name, "id":"300266386", "label": "Personal Name"},
	"AliasName": {"parent": Name, "id": "300404664", "label": "Alias"},
	"MaidenName": {"parent": Name, "id": "300404682", "label": "Maiden Name"},
	"FormerName": {"parent": Name, "id": "300435719", "label": "Former Name"},
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
	"Sample": {"parent": HumanMadeObject, "id":"300028875", "label": "Sample", "metatype": "work type"},

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
	"Folio": {"parent": HumanMadeObject, "id":"300189604", "label": "Folio", "metatype": "work type"},

	"Folder": {"parent": HumanMadeObject, 'id':"300197602", "label": "Folder", "metatype": "work type"},
	"Box": {"parent": HumanMadeObject, "id":"300045643", "label": "Box", "metatype": "work type"},
	"Envelope": {"parent": HumanMadeObject, "id":"300197601", "label": "Envelope", "metatype": "work type"},
	"Binder": {"parent": HumanMadeObject,"id":"300252990", "label": "Binder", "metatype": "work type"},
	"Case": {"parent": HumanMadeObject,"id":"300045659", "label": "Case", "metatype": "work type"},
	"FlatfileCabinet": {"parent": HumanMadeObject,"id":"300417284", "label": "Flat File Cabinet", "metatype": "work type"},

	"AuctionCatalog": {"parent": HumanMadeObject,"id":"300026068", "label": "Auction Catalog", "metatype": "work type"},
	"ExhibitionCatalog": {"parent": HumanMadeObject,"id":"300026096", "label": "Exhibition Catalog", "metatype": "work type"},
	"AccessionCatalog": {"parent": HumanMadeObject, "id": "300026617", "label": "Accession Catalog", "metatype": "work type"},
	"SalesCatalog": {"parent": HumanMadeObject,"id":"300026074", "label": "Sales Catalog", "metatype": "work type"},
	"LotteryCatalog": {"parent": HumanMadeObject, "id":"300438603", "label": "Lottery Catalog", "metatype": "work type"},

	"Sample": {"parent": HumanMadeObject, "id": "300028875", "label": "Sample"},

	"FrontPart": {"parent": HumanMadeObject, "id":"300190703", "label": "Front Part", "metatype": "part type"},
	"BackPart": {"parent": HumanMadeObject, "id":"300190692", "label": "Back Part", "metatype": "part type"},
	"TopPart": {"parent": HumanMadeObject, "id":"300190710", "label": "Top Part", "metatype": "part type"},
	"BottomPart": {"parent": HumanMadeObject, "id":"300190695", "label": "Bottom Part", "metatype": "part type"},
	"SidePart": {"parent": HumanMadeObject, "id":"300190706", "label": "Side Part", "metatype": "part type"},
	"SupportPart": {"parent": HumanMadeObject, "id":"300014844", "label": "Support", "metatype": "part type"},
	"FramePart": {"parent": HumanMadeObject, "id":"300404391", "label": "Frame", "metatype": "part type"},
	"MountPart": {"parent": HumanMadeObject, "id":"300131087", "label": "Mount", "metatype": "part type"},
	"PanelPart": {"parent": HumanMadeObject, "id":"300014657", "label": "Panel", "metatype": "part type"},
	"BasePart": {"parent": HumanMadeObject, "id":"300001656", "label": "Base", "metatype": "part type"},

	"StartingPrice": {"parent": MonetaryAmount, "id": "300417242", "label": "Starting Price"},
	"ReservePrice": {"parent": MonetaryAmount, "id": "300417243", "label": "Reserve Price"},
	"EstimatedPrice": {"parent": MonetaryAmount, "id": "300417244", "label": "Estimated Price"},
	"AskingPrice": {"parent": MonetaryAmount, "id": "300417241", "label": "Asking Price"},
	"HammerPrice": {"parent": MonetaryAmount, "id": "300417245", "label": "Hammer Price"},

	"CommissionPayment": {"parent": Payment, "id": "300393199", "label": "Commission"}

}
 
identity_instances = {

	# Common Materials
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
	"hazardous": {"parent": Material, "id": "300138222", "label": "Hazardous Material"},
	"thread": {"parent": Material, "id": "300014250", "label": "Thread"},

	# Measurement Units - lengths, weights, durations
	"lignes": {"parent": MeasurementUnit, "id": "300435501", "label": "Paris lines"},
	"fr_inches": {"parent": MeasurementUnit, "id": "300435502", "label": "Paris inches"},
	"fr_feet": {"parent": MeasurementUnit, "id":"300435503", "label": "Paris feet"},
	"inches": {"parent": MeasurementUnit, "id": "300379100", "label": "inches"},
	"feet": {"parent": MeasurementUnit, "id":"300379101", "label": "feet"},
	"mm": {"parent": MeasurementUnit, "id": "300379097", "label": "millimeters"},
	"cm": {"parent": MeasurementUnit, "id": "300379098", "label": "centimeters"},
	"meters": {"parent": MeasurementUnit, "id": "300379099", "label": "meters"},
	"braccia": {"parent": MeasurementUnit, "id": "300404161", "label": "braccia"},
	"ells": {"parent": MeasurementUnit, "id": "300412070", "label": "ells"},
	"grams": {"parent": MeasurementUnit, "id": "300379225", "label": "grams"},
	"kilograms": {"parent": MeasurementUnit, "id": "300379226", "label": "kilograms"},
	"ounces":{"parent": MeasurementUnit, "id": "300379229", "label": "ounces"},
	"pounds": {"parent": MeasurementUnit, "id": "300379254", "label": "pounds"},
	"seconds": {"parent": MeasurementUnit, "id": "300379239", "label": "seconds"},
	"minutes": {"parent": MeasurementUnit, "id": "300379240", "label": "minutes"},
	"hours": {"parent": MeasurementUnit, "id": "300379241", "label": "hours"},
	"days": {"parent": MeasurementUnit, "id": "300379242", "label": "days"},
	"months": {"parent": MeasurementUnit, "id": "300379245", "label": "months"},
	"years": {"parent": MeasurementUnit, "id": "300379244", "label": "years"},

	"percent": {"parent": MeasurementUnit, "id": "300417377", "label": "percent"},
	"numbers": {"parent": MeasurementUnit, "id": "300055665", "label": "numbers"},
	"bytes": {"parent": MeasurementUnit, "id": "300265869", "label": "bytes"},
	"kilobytes": {"parent": MeasurementUnit, "id": "300265870", "label": "kilobytes"},
	"megabytes": {"parent": MeasurementUnit, "id": "300265873", "label": "megabytes"},
	"gigabytes": {"parent": MeasurementUnit, "id": "300265874", "label": "gigabytes"},
	"terabytes": {"parent": MeasurementUnit, "id": "300266477", "label": "terabytes"},
	"pageCount": {"parent": MeasurementUnit, "id": "300194222", "label": "pages"},
	"pixels": {"parent": MeasurementUnit, "id": "300266190", "label": "pixels"},
	"rgb_colorspace": {"parent": MeasurementUnit, "id": "300266239", "label": "rgb"},
	"partsUnit": {"parent": MeasurementUnit, "id": "300404159", "label": "parts"},

	# Languages
	"english": {"parent": Language, "id": "300388277", "label": "English"},
	"french": {"parent": Language, "id":"300388306","label": "French"},
	"german": {"parent": Language, "id":"300388344","label": "German"},
	"spanish": {"parent": Language, "id":"300389311","label": "Spanish"},
	"chinese": {"parent": Language, "id":"300388113", "label":"Chinese"},
	"hindi": {"parent": Language, "id":"300388412", "label":"Hindi"},
	"afrikaans": {"parent": Language, "id":"300387782", "label":"Afrikaans"},
	"albanian": {"parent": Language, "id":"300387803", "label":"Albanian"},
	"arabic": {"parent": Language, "id":"300387843", "label":"Arabic"},
	"bulgarian": {"parent": Language, "id":"300388034", "label":"Bulgarian"},
	"bosnian": {"parent": Language, "id":"300388023", "label":"Bosnian"},
	"catalan": {"parent": Language, "id":"300388072", "label":"Catalan"},
	"portuguese":{"parent": Language, "id":"300389115", "label":"Portuguese"},
	"bengali": {"parent": Language, "id":"300387971", "label":"Bengali"},
	"russian": {"parent": Language, "id":"300389168", "label":"Russian"},
	"dutch": {"parent": Language, "id":"300388256", "label":"Dutch"},
	"finnish": {"parent": Language, "id":"300388299", "label":"Finnish"},
	"icelandic": {"parent": Language, "id":"300388449", "label":"Icelandic"},
	"irish": {"parent": Language, "id":"300388467", "label":"Irish"},
	"italian": {"parent": Language, "id":"300388474", "label":"Italian"},
	"farsi": {"parent": Language, "id":"300388296", "label":"Farsi"},
	"greek": {"parent": Language, "id":"300389734", "label":"Greek"},
	"gujarati": {"parent": Language, "id":"300388371", "label":"Gujarati"},
	"ancient greek": {"parent": Language, "id": "300387827", "label": "Ancient Greek"},
	"korean": {"parent": Language, "id":"300388633", "label":"Korean"},
	"latin": {"parent": Language, "id":"300388693", "label":"Latin"},
	"lithuanian": {"parent": Language, "id":"300388723", "label":"Lithuanian"},
	"macedonian": {"parent": Language, "id":"300388760", "label":"Macedonian"},
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
	"serbian": {"parent": Language, "id": "300389247", "label": "Serbian"},
	"swedish": {"parent": Language, "id": "300389336", "label": "Swedish"},
	"turkish": {"parent": Language, "id": "300389470", "label": "Turkish"},
	"welsh": {"parent": Language, "id": "300389555", "label": "Welsh"},

	# Currencies
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
	"at kronen": {"parent": Currency, "id":"300435706", "label": "Austrian Kronen"},
	"austro-hungarian kronen": {"parent": Currency, "id":"300435707", "label": "Austro-Hungarian Kronen"},

	# Color Dimensions -- additional Type on the Color Dimension instance
	# See: https://linked.art/model/object/physical/
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

	# Techniques -- use technique property, no need to metatype
	"glassblowing": {"parent": Type, "id":"300053932", "label":"Glassblowing"},
	"sculpting": {"parent": Type, "id":"300264383", "label": "Sculpting"},
	"painting": {"parent": Type, "id":"300054216", "label": "Painting"},
	"spraypainting": {"parent": Type, "id":"300053816", "label": "Spraypainting"},

  # Conditions
	"crizzling": {"parent": Type, "id": "300218594", "label": "Crizzling"},

	# Geographic
	"city": {"parent": Type, "id": "300008389", "label": "City"},
	"province": {"parent": Type, "id":"300000774", "label": "Province"},
	"county": {"parent": Type, "id":"300000771", "label": "County"},
	"nation": {"parent": Type, "id": "300128207", "label": "Nation"},
	"sovereign": {"parent": Type, "id": "300232420", "label": "Sovereign State"},
	"building": {"parent": Type, "id": "300004792", "label": "Building"},
	"city block": {"parent": Type, "id": "300008077", "label": "City Block"},

	# dot one qualifiers
	"style of": {"parent": Type, "id": "300404285", "label": "Style Of"},

	# General
	"primary": {"parent": Type, "id": "300404670", "label": "Primary"},
	"artwork": {"parent": Type, "id": "300133025", "label": "Artwork"},
	"work type": {"parent": Type, "id": "300435443", "label": "Type of Work"},
	"part type": {"parent": Type, "id":"300241583", "label": "Part Type"},
	"brief text": {"parent": Type, "id": "300418049", "label":"Brief Text"},
	"first": {"parent": Type, "id":"300404050", "label": "First"},
	"last": {"parent": Type, "id": "XXX", "label": "Last"},

	# Random?
	"public collection": {"parent": Type, "id": "300411912", "label": "Public Collection"},
	"computer generated": {"parent": Type, "id": "300202389", "label": "Computer Generated"},
	"vandalism": {"parent": Type, "id":"300055299", "label": "Vandalism"},
	"contribution": {"parent": Type, "id":"300403975", "label":"Contribution"},  # As opposed to primarily responsible

	# Subjects -- use is_about / subject project, no need to metatype
	"gender issues": {"parent": Type, "id": "300233686", "label": "Gender Issues"},
	"war": {"parent": Type, "id": "300055314", "label": "War"},
	"crime": {"parent": Type, "id": "300055289", "label": "Crime"},

	# Additional classifications for objects
	"door piece": {"parent": Type, "id":"300002911", "label": "Door piece"}, # on Painting
	"bust": {"parent": Type, "id":"300047457", "label": "Bust"}, # on Sculpture
	"altarpiece": {"parent": Type, "id":"300075940", "label": "Altarpiece"}, # on Painting
	"double-sided paintings": {"parent": Type, "id":"300265620", "label": "Double-sided Paintings"}, # on Painting
	"bas-relief": {"parent": Type, "id":"300184633", "label": "Bas-relief"},

	# Additional classifications for visual content
	"allusion": {"parent": Type, "id":"300055815", "label":"Allusion"},
	"allegory": {"parent": Type, "id":"300055866", "label":"Allegory"}

}

for (name,v) in identity_instances.items():
	register_instance(name, v)
for (name,v) in ext_classes.items():
	register_vocab_class(name, v)


local_instances = {

	# Nationalities
	"american nationality": {"parent": Nationality, "id": "300107956", "label": "American"},
	"austrian nationality": {"parent": Nationality, "id": "300111153", "label": "Austrian"},
	"australian nationality": {"parent": Nationality, "id": "300021861", "label": "Australian"},
	"belgian nationality": {"parent": Nationality, "id": "300111156", "label": "Belgian"},
	"british nationality": {"parent": Nationality, "id": "300111159", "label": "British"},	
	"canadian nationality": {"parent": Nationality, "id": "300107962", "label": "Canadian"},
	"chinese nationality": {"parent": Nationality, "id": "300018322", "label": "Chinese"},
	"czech nationality": {"parent": Nationality, "id": "300111166", "label": "Czech"},
	"danish nationality": {"parent": Nationality, "id": "300111172", "label": "Danish"},
	"dutch nationality": {"parent": Nationality, "id": "300111175", "label": "Dutch"},
	"egyptian nationality": {"parent": Nationality, "id": "300020251", "label": "Egyptian"},
	"flemish nationality": {"parent": Nationality, "id": "300111184", "label": "Flemish"},
	"french nationality": {"parent": Nationality, "id": "300111188", "label": "French"},
	"german nationality": {"parent": Nationality, "id": "300111192", "label": "German"},
	"greek nationality": {"parent": Nationality, "id": "300264816", "label": "Greek"},
	"hungarian nationality": {"parent": Nationality, "id": "300111195", "label": "Hungarian"},
	"indian nationality": {"parent": Nationality, "id": "300018863", "label": "Indian"},
	"irish nationality": {"parent": Nationality, "id": "300111259", "label": "Irish"},
	"italian nationality": {"parent": Nationality, "id": "300111198", "label": "Italian"},
	"japanese nationality": {"parent": Nationality, "id": "300018519", "label": "Japanese"},
	"mexican nationality": {"parent": Nationality, "id": "300107963", "label": "Mexican"},
	"new zealand nationality": {"parent": Nationality, "id": "300021959", "label": "New Zealander"},
	"norwegian nationality": {"parent": Nationality, "id": "300111201", "label": "Norwegian"},
	"polish nationality": {"parent": Nationality, "id": "300111204", "label": "Polish"},
	"portuguese nationality": {"parent": Nationality, "id": "300111207", "label": "Portuguese"},
	"russian nationality": {"parent": Nationality, "id": "300111276", "label": "Russian"},
	"spanish nationality": {"parent": Nationality, "id": "300111215", "label": "Spanish"},
	"swedish nationality": {"parent": Nationality, "id": "300111218", "label": "Swedish"},
	"swiss nationality": {"parent": Nationality, "id": "300111221", "label": "Swiss"},
	"venetian nationality": {"parent": Nationality, "id": "300379657", "label": "Venetian"}, # republic until 1797

	# Occupations
	"artist occupation":  {"parent": Occupation, "id":"300025103", "label": "Artist"},
 	"collector occupation":  {"parent": Occupation, "id":"300025234", "label": "Collector"},
 	"dealer occupation":  {"parent": Occupation, "id":"300025236", "label": "Dealer"},

	# Nations
	"belgium": {"parent": Nation, "id": "1000063", "vocab": "tgn", "label": "Belgium"},
	"france": {"parent": Nation, "id": "1000070", "vocab": "tgn", "label": "France"},
	"germany": {"parent": Nation, "id": "7000084", "vocab": "tgn", "label": "Germany"},
	"switzerland": {"parent": Nation, "id": "7011731", "vocab": "tgn", "label": "Switzerland"},
	"united kingdom": {"parent": Nation, "id": "7008591", "vocab": "tgn", "label": "United Kingdom"},
	"england": {"parent": Nation, "id": "7002445", "vocab": "tgn", "label": "England"},
	"scotland": {"parent": Nation, "id": "7002444", "vocab": "tgn", "label": "Scotland"},
	"wales": {"parent": Nation, "id": "7002443", "vocab": "tgn", "label": "Wales"},

	# Shapes
	"oval": {"parent": Shape, "id":"300263817", "label": "Oval"},
	"octagonal": {"parent": Shape, "id":"300263824", "label": "Octagonal"},
	"circle": {"parent": Shape, "id":"300263827", "label": "Circle"},
	"square": {"parent": Shape, "id":"300263832", "label": "Square"},
	"oblong": {"parent": Shape, "id":"300311843", "label": "Oblong"},
	"upright": {"parent": Shape, "id":"300343370", "label": "Upright"},
	"arched": {"parent": Shape, "id":"300126995", "label": "Arched"},

	# Styles
	"style genre": {"parent": Style, "id":"300139140", "label": "Genre"},
	"style landscape": {"parent": Style, "id":"300015636", "label": "Landscape"},
	"style portrait": {"parent": Style, "id":"300015637", "label": "Portrait"},
	"style still life": {"parent": Style, "id":"300015638", "label": "Still Life"},
	"style impressionism": {"parent": Style, "id":"300021503", "label": "Impressionism"},

	# Genders / Biological Sexes
	"male": {"parent": Gender, "id":"300189559", "label": "Male"},
	"female": {"parent": Gender, "id":"300189557", "label": "Female"},	
	"intersex": {"parent": Gender, "id":"300417544", "label": "Intersex"},
	"hermaphrodite": {"parent": Gender, "id":"300389935", "label": "Hermaphrodite"},
	"non-binary gender": {"parent": Gender, "id":"300417543", "label": "Non-Binary Gender Identity"},
	"transgender": {"parent": Gender, "id":"300400504", "label": "Transgender"}

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

def add_classification(obj, cl_type):
	c = cl_type()
	for cn in c._classification:
		if hasattr(obj, 'classified_as') and not cn in obj.classified_as:
			obj.classified_as = cn
		elif not hasattr(obj, 'classified_as'):
			obj.classified_as = cn
	return obj

def make_multitype_obj(*args, **kw):
	# (class1, class2, class3, name=foo, other=bar)
	inst = args[0](**kw)
	for c in args[1:]:
		for cn in c._classification:
			if hasattr(inst, 'classified_as') and not cn in inst.classified_as:
				inst.classified_as = cn
			elif not hasattr(inst, 'classified_as'):
				inst.classified_as = cn
	return inst


def conceptual_only_parts():
	# Make .part work as expected for Right
	# which is only propositional and not symbolic, so P148 not P106

	def set_c_part(self, value):
		self.c_part = value
	def set_c_part_of(self, value):
		self.c_part_of = value

	def rights_getter(self, what):
		if what == "part":
			return self.c_part
		elif what == "part_of":
			return self.c_part_of
		else:
			object.__getattr__(self, what)

	Right.set_part = set_c_part
	Right.set_part_of = set_c_part_of
	Right._property_name_map['c_part'] = 'part'
	Right._property_name_map['c_part_of'] = 'part_of'
	Right._all_properties['part'] = PropositionalObject._all_properties['c_part']
	Right._all_properties['part_of'] = PropositionalObject._all_properties['c_part_of']
	Right.__getattr__ = rights_getter


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
		if ass_res and assto_res:
			assto_res._check_prop(value, ass_res)
		object.__setattr__(self, p177, value)
	setattr(AttributeAssignment, "set_%s" % p177, aa_set_assigned_property_type)


	def phase_set_relationship(self, value):
		# XXX do same checking as above
		object.__setattr__(self, phase_rel, value)
	setattr(Phase, "set_%s" % phase_rel, phase_set_relationship)		

def add_linked_art_boundary_check():

	boundary_classes = [x.__name__ for x in [Actor, HumanMadeObject, Person, Group, VisualItem, \
		Place, Period, LinguisticObject, Phase, Set, Event, DigitalObject, DigitalService]]
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

	ExternalResource._embed_override = None

	def my_linked_art_boundary_check(self, top, rel, value):
		# True = Embed ; False = Split
		if value._embed_override is not None:
			return value._embed_override
		elif isinstance(value, LinguisticObject) and hasattr(value, 'classified_as'):
			for ca in value.classified_as:
				if instances['brief text'] in getattr(ca, 'classified_as', []):
					return True
		# Non Statement Linguistic objects might still be internal or external
		# so apply logic from relating properties, not return False
		elif isinstance(value, ProvenanceEntry):
			return False

		if rel in ["part", "member"]:
			# Downwards, internal simple partitioning 
			# This catches an internal part to a LinguisticObject
			return True
		elif rel in ["part_of", 'member_of']:
			# upwards partition refs are inclusion, and always boundary crossing
			return False
		elif value.type in boundary_classes:
			# This catches the external text LinguisticObject
			return False
		elif value.type in embed_classes:
			return True
		else:
			# Default to embedding to avoid data loss
			return True

	setattr(BaseResource, "_linked_art_boundary_okay", my_linked_art_boundary_check)
	factory.linked_art_boundaries = True	

def set_linked_art_uri_segments():
	HumanMadeObject._uri_segment = "object"
	Activity._uri_segment = "event"
	Event._uri_segment = "event"
	Period._uri_segment = "event"
	Place._uri_segment = "place"
	InformationObject._uri_segment = "info"
	Group._uri_segment = "group"
	# Actor._uri_segment = "actor"
	Person._uri_segment = "person"
	PhysicalObject._uri_segment = "object"
	LinguisticObject._uri_segment = "text"
	PropositionalObject._uri_segment = "concept"
	DigitalObject._uri_segment = "digital"
	DigitalService._uri_segment = "digital"
	Type._uri_segment = "concept"	
	Language._uri_segment = "concept"
	MeasurementUnit._uri_segment = "concept"
	Currency._uri_segment = "concept"
	Material._uri_segment = "concept"
	VisualItem._uri_segment = "visual"
	ProvenanceEntry._uri_segment = "provenance"
	Exhibition._uri_segment = "activity"
	Set._uri_segment = "set"


def add_helper_functions():
	# Add filter functions to the right bits of the model

	def get_names(self, filter=None):
		return [x for x in self.identified_by if isinstance(x, Name) and (not filter or filter in x.classified_as)]

	def get_identifiers(self, filter=None):
		return [x for x in self.identified_by if isinstance(x, Identifier) and (not filter or filter in x.classified_as)]

	def get_statements(self, filter=None):
		return [x for x in self.referred_to_by if isinstance(x, LinguisticObject) and x.content and (not filter or filter in x.classified_as)]

	CRMEntity.get_names = get_names
	CRMEntity.get_identifiers = get_identifiers
	CRMEntity.get_statements = get_statements




