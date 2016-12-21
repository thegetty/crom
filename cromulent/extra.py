
import inspect
from .model import Destruction, Activity, Purchase, MonetaryAmount, Actor, Place, \
	Type, Dimension, SymbolicObject, Person, ManMadeObject

# DestuctionActivity class as CRM has a Destruction Event and recommends multi-classing
class DestructionActivity(Destruction, Activity):
	_uri_segment = "Activity"
	_type = ["crm:Destruction", "crm:Activity"]
	_niceType = ["Destruction", "Activity"]
DestructionActivity._classhier = inspect.getmro(DestructionActivity)[:-1]

# New Payment Activity
Purchase._properties['offering_price'] = {"rdf":"pi:had_offering_price", "range": MonetaryAmount}
class Payment(Activity):
	_properties = {
		"paid_amount": {"rdf": "pi:paid_amount", "range": MonetaryAmount},
		"paid_to": {"rdf": "pi:paid_to", "range": Actor},
		"paid_from": {"rdf": "pi:paid_from", "range": Actor}
	}
	_uri_segment = "Payment"
	_type = "pi:Payment"
Payment._classhier = inspect.getmro(Payment)[:-1]

# Require explict addition of the schema.org shortcut properties
def add_schema_properties():
	Person._properties['familyName'] = {"rdf": "schema:familyName", "range": str}
	Person._properties['givenName'] = {"rdf": "schema:givenName", "range": str}
	Person._properties['nationality'] = {"rdf": "schema:nationality", "range": Place}
	ManMadeObject._properties['culture'] = {"rdf": "schema:genre", "range": Type}
	ManMadeObject._properties['height'] = {"rdf": "schema:height", "range": Dimension}
	ManMadeObject._properties['width'] = {"rdf": "schema:width", "range": Dimension}

def add_rdf_value():
	SymbolicObject._properties['value'] = {"rdf": "rdf:value", "range": str}
	Dimension._properties['value'] = {"rdf": "rdf:value", "range": str}
