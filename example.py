
from cidoc_orm import factory, Document, Activity, Event, TimeSpan, ManMadeObject, Acquisition

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
what = ManMadeObject('thing')
txn.transferred_title_of = what

print factory.toString(catalog, compact=False)
