
from cidoc_orm import factory, Document, Activity, Event, TimeSpan, ManMadeObject, Acquisition, Type

# Locally "subclass" to create consistent patterns with E55 and AAT
class Painting(ManMadeObject):
	def __init__(self, *args, **kw):
		super(Painting, self).__init__(*args, **kw)
		self.has_type = Type("http://vocab.getty.edu/aat/300033618")

# Or actually subclass in an extension vocab
class Mosaic(ManMadeObject):
	_type = "extension:Mosaic"

catalog = Document("catalog")
page = Document("catalog-entry")
catalog.has_component = page
auction = Activity("auction")
catalog.documents = auction
lot = Activity("lot")
auction.consists_of = lot
page.documents = lot
txn = Acquisition("sale")
lot.consists_of = txn
what = Painting('my-painting')
txn.transferred_title_of = what

print factory.toString(catalog, compact=False)
