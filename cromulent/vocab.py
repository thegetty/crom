
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

from .model import Identifier, Mark, ManMadeObject, Type, \
	Person, Material, MeasurementUnit, Place, Dimension, \
	ConceptualObject, TimeSpan, Actor, PhysicalThing, \
	LinguisticObject, InformationObject, SpatialCoordinates, \
	Activity, Group, Appellation, MonetaryAmount, Purchase, \
	Destruction, AttributeAssignment, BaseResource, PhysicalObject, \
	Acquisition, TransferOfCustody, Title 

# Add classified_as initialization hack for all resources
def post_init(self, **kw):
	if self.__class__._classification:
		self.classified_as = Type(self._classification)
BaseResource._post_init = post_init

def register_aat_class(name, parent, id):
	c = type(name, (parent,), {})
	# Decision 2017-04 to always use prefixed version for id and references
	c._classification = "aat:%s" % id
	c._type = None # To avoid conflicting with parent class
	globals()[name] = c	

materialTypes = {}
def register_aat_material(name, id):
	# This will auto-prefix in `id`
	m = Material("http://vocab.getty.edu/aat/%s" % id)
	m.label = name
	materialTypes[name] = m	

dimensionUnits = {}
def register_aat_dimensionUnit(name, id):
	d = MeasurementUnit("http://vocab.getty.edu/aat/%s" % id)
	d.label = name
	dimensionUnits[name] = d

# Meta meta
ext_classes = {
	"LocalNumber": {"parent": Identifier, "vocab": "aat", "id": "300404621"},	
	"AccessionNumber": {"parent": Identifier, "vocab": "aat", "id": "300312355"},
	"LotNumber": {"parent": Identifier, "vocab": "aat", "id": "300404628"},

	"PrimaryAppellation": {"parent": Appellation, "vocab": "aat", "id": "300404670"},

	"Inscription": {"parent": LinguisticObject, "vocab": "aat", "id": "300028702"},
	"Signature": {"parent": LinguisticObject, "vocab": "aat", "id": "300028705"},
	"MaterialStatement": {"parent": LinguisticObject, "vocab": "aat", "id": "300010358"},
	"DimensionStatement": {"parent": LinguisticObject, "vocab": "aat", "id": "300266036"},
	"CreditStatement": {"parent": LinguisticObject, "vocab":"aat", "id": "300026687"},
	"RightsStatement": {"parent": LinguisticObject, "vocab":"aat", "id": "300055547"},
	"EditionStatement": {"parent": LinguisticObject, "vocab":"aat", "id":"300121294"},
	"BiographyStatement": {"parent": LinguisticObject, "vocab":"aat", "id":"300080102"},
	"ProvenanceStatement": {"parent": LinguisticObject, "vocab":"aat", "id":"300055863"},
	"Description": {"parent": LinguisticObject, "vocab": "aat", "id":"300080091"},

	"CatalogueRaisonne": {"parent": InformationObject, "vocab":"aat", "id":"300026061"},
	"AuctionCatalog": {"parent": InformationObject, "vocab":"aat", "id":"300026068"},
	"SalesCatalog": {"parent": InformationObject, "vocab":"aat", "id": "300026074"},
	"ExhibitionCatalog": {"parent": InformationObject, "vocab":"aat", "id": "300026096"},
	"AccountBook": {"parent": InformationObject, "vocab":"aat", "id": "300027483"},
	"WebPage": {"parent": InformationObject, "vocab":"aat", "id":"300264578"},
	"Register": {"parent": InformationObject, "vocab":"aat", "id":"300027168"},

	"Latitude":  {"parent": SpatialCoordinates, "vocab":"aat", "id":"300387565"},
	"Longitude": {"parent": SpatialCoordinates, "vocab":"aat", "id":"300387567"},

	"Height":     {"parent": Dimension, "vocab":"aat", "id":"300055644"},
	"Width":      {"parent": Dimension, "vocab":"aat", "id":"300055647"},
	"Depth":      {"parent": Dimension, "vocab":"aat", "id":"300072633"},
	"Diameter":   {"parent": Dimension, "vocab":"aat", "id":"300055624"},
	"Weight":     {"parent": Dimension, "vocab":"aat", "id":"300056240"},

	"Gallery":      {"parent": Place, "vocab":"aat", "id":"300240057"},
	"AuctionHouse": {"parent": Place, "vocab":"aat", "id":"300005234"},
	"MuseumPlace":  {"parent": Place, "vocab":"aat", "id":"300005768"},
	"ExhibitionPlace": {"parent": Place, "vocab":"aat", "id":"300005748"},

	"MuseumOrg":   {"parent": Group, "vocab":"aat", "id":"300312281"},
	"Department":  {"parent": Group, "vocab":"aat", "id":"300263534"},
	"Nationality": {"parent": Group, "vocab":"aat", "id":"300379842"},
	"Gender":      {"parent": Group, "vocab":"aat", "id":"300055147"},

	"Auctioneer":  {"parent": Person, "vocab":"aat", "id":"300025208"},

	"Auction":     {"parent": Activity, "vocab":"aat", "id":"300054751"},
	"Bidding":     {"parent": Activity, "vocab":"aat", "id":"300054602"}, # individual bid
	"Curating":    {"parent": Activity, "vocab":"aat", "id":"300054277"},
	"Inventorying": {"parent": Activity, "vocab":"aat", "id":"300077506"},
	"Provenance":  {"parent": Activity, "vocab":"aat", "id":"300055863"},
	"Exhibition":  {"parent": Activity, "vocab":"aat", "id":"300054766"},
	"MultiExhibition": {"parent": Activity, "vocab":"aat", "id":"300054773"},
	"Active":      {"parent": Activity, "vocab":"aat", "id":"300393177"},

	"Theft": {"parent": TransferOfCustody, "vocab":"aat", "id": "300055292"},

	"Attribution": {"parent": AttributeAssignment, "vocab":"aat", "id": "300056109"},
	"Appraising": {"parent": AttributeAssignment, "vocab":"aat", "id": "300054622"},
	"Dating": {"parent": AttributeAssignment, "vocab":"aat", "id":"300054714"},
	"Naming": {"parent": AttributeAssignment, "vocab":"aat", "id":"300411672"},

	"SupportPart": {"parent": PhysicalObject, "vocab":"aat", "id":"300014844"},
	"FramePart": {"parent": PhysicalObject, "vocab":"aat", "id":"300404391"},
	"MountPart": {"parent": PhysicalObject, "vocab":"aat", "id":"300131087"},
	"PanelPart": {"parent": PhysicalObject, "vocab":"aat", "id":"300014657"},
	"AuctionLotSet": {"parent": PhysicalObject, "vocab":"aat", "id":"300411307"},
	"CollectionSet": {"parent": PhysicalObject, "vocab":"aat", "id":"300025976"},

	"SortName": {"parent": Appellation, "vocab":"aat", "id":"300404672"},
	"PrimaryName": {"parent": Appellation, "vocab":"aat", "id":"300404670"},
	"GivenName": {"parent": Appellation, "vocab":"aat", "id":"300404651"},
	"FamilyName": {"parent": Appellation, "vocab":"aat", "id":"300404652"},
	"MiddleName": {"parent": Appellation, "vocab":"aat", "id":"300404654"},
	"NamePrefix": {"parent": Appellation, "vocab":"aat", "id":"300404845"},
	"NameSuffix": {"parent": Appellation, "vocab":"aat", "id":"300404662"},

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
	"Graphic": {"parent": ManMadeObject, "vocab": "aat", "id": "300015387"},
	"Enamel": {"parent": ManMadeObject, "vocab": "aat", "id": "300178264"},
	"Embroidery": {"parent": ManMadeObject, "vocab": "aat", "id": "300264024"},
	"PhotographPrint": {"parent": ManMadeObject, "vocab": "aat", "id": "300127104"},
	"PhotographAlbum": {"parent": ManMadeObject, "vocab": "aat", "id": "300026695"},
	"PhotographBook": {"parent": ManMadeObject, "vocab": "aat", "id": "300265728"},
	"PhotographColor": {"parent": ManMadeObject, "vocab": "aat", "id": "300128347"},
	"PhotographBW": {"parent": ManMadeObject, "vocab": "aat", "id": "300128359"},

	"Architecture": {"parent": ManMadeObject, "vocab": "aat", "id":"300263552"},
	"Armor": {"parent": ManMadeObject, "vocab": "aat", "id":"300036745"},
	"Book": {"parent": ManMadeObject, "vocab": "aat", "id":"300028051"},
	"DecArts": {"parent": ManMadeObject, "vocab": "aat", "id":"300054168"},
	"Implement": {"parent": ManMadeObject, "vocab": "aat", "id":"300024841"},
	"Jewelry": {"parent": ManMadeObject, "vocab": "aat", "id":"300209286"},
	"Manuscript": {"parent": ManMadeObject, "vocab": "aat", "id":"300265483"},
	"SiteInstallation": {"parent": ManMadeObject, "vocab": "aat", "id":"300047896"},
	"Text": {"parent": ManMadeObject, "vocab": "aat", "id":"300263751"},
	"Print":  {"parent": ManMadeObject, "vocab": "aat", "id":"300041273"},
	"TimeBasedMedia": {"parent": ManMadeObject, "vocab": "aat", "id":"300185191"}

}
 
for (name,v) in ext_classes.items():
	register_aat_class(name, v['parent'], v['id'])

aat_material_mapping = {
	"panel": "300014657",  # Is really a support
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

# pen, pencil, card, cardboard, porcelain, wax, ceramic, plaster
# crayon, millboard, gouache, brass, stone, lead, iron, clay,
# alabaster, limestone

for (k,v) in aat_material_mapping.items():
	register_aat_material(k,v)

aat_culture_mapping = {
	"french": "300111188",
	"italian": "300111198",
	"german": "300111192",
	"dutch": "300020929"
}

dim_unit_mapping = {
	"inches": "300379100",	
	"feet": "300379101",
	"cm": "300379098"
}
for (k,v) in dim_unit_mapping.items():
	register_aat_dimensionUnit(k,v)

# Monkey patch Type's _toJSON to only emit full data if not just URI+type
def typeToJSON(self, top=False):
	props = self.__dict__.keys()
	if len(props) > 4:
		return super(Type, self)._toJSON()
	elif self._factory.elasticsearch_compatible:
		return {"id": self.id}
	else:
		return self.id
Type._toJSON = typeToJSON


def add_art_setter():
	# Linked.Art profile requires aat:300133025 on all artworks
	# Art can be a ManMadeObject or an InformationObject
	# set it by adding art=1 to the constructor

	def art_post_init(self, **kw):
		if "art" in kw:
			self.classified_as = Type("aat:300133025")
		super(ManMadeObject, self)._post_init(**kw)
	ManMadeObject._post_init = art_post_init

	def art2_post_init(self, **kw):
		if "art" in kw:
			self.classified_as = Type("aat:300133025")
		super(InformationObject, self)._post_init(**kw)
	InformationObject._post_init = art2_post_init
	
