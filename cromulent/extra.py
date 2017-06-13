
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

import inspect
from .model import Destruction, EndOfExistence, Activity, Purchase, MonetaryAmount, Actor, Place, \
	Type, Dimension, SymbolicObject, Person, ManMadeObject, PhysicalObject, CRMEntity, \
	InformationObject, ManMadeThing, BaseResource

# DestuctionActivity class as CRM has a Destruction Event and recommends multi-classing
# WARNING:  instantiating this class in the default profile will raise an error

class DestructionActivity(Destruction, Activity):
	_uri_segment = "Activity"
	_type = ["crm:Destruction", "crm:Activity"]
	_niceType = ["Destruction", "Activity"]
DestructionActivity._classhier = inspect.getmro(DestructionActivity)[:-1]

# And hence we make an EndOfExistence+Activity class
# for all activities that end existences
class EoEActivity(EndOfExistence, Activity):
	_uri_segment = "Activity"
	_type = ["crm:End_of_Existence", "crm:Activity"]
	_niceType = ["EndOfExistence", "Activity"]	
EoEActivity._classhier = inspect.getmro(EoEActivity)[:-1]

# New Payment Activity
Purchase._properties['offering_price'] = {"rdf":"pi:had_offering_price", "range": MonetaryAmount, "okayToUse": 1}
class Payment(Activity):
	_properties = {
		"paid_amount": {"rdf": "pi:paid_amount", "range": MonetaryAmount, "okayToUse": 1},
		"paid_to": {"rdf": "pi:paid_to", "range": Actor, "okayToUse": 1},
		"paid_from": {"rdf": "pi:paid_from", "range": Actor, "okayToUse": 1}
	}
	_uri_segment = "Payment"
	_type = "pi:Payment"
Payment._classhier = inspect.getmro(Payment)[:-1]

# Require explict addition of the schema.org shortcut properties
def add_schema_properties():
	Person._properties['family_name'] = {"rdf": "schema:familyName", "range": str, "okayToUse": 1}
	Person._properties['given_name'] = {"rdf": "schema:givenName", "range": str, "okayToUse": 1}
	Person._properties['nationality'] = {"rdf": "schema:nationality", "range": Place, "okayToUse": 1}
	ManMadeObject._properties['style'] = {"rdf": "schema:genre", "range": Type, "okayToUse": 1}
	ManMadeObject._properties['height'] = {"rdf": "schema:height", "range": Dimension, "okayToUse": 1}
	ManMadeObject._properties['width'] = {"rdf": "schema:width", "range": Dimension, "okayToUse": 1}
	ManMadeObject._properties['subject'] = {"rdf": "dct:subject", "range": Type, "okayToUse": 1}
	BaseResource._properties['homepage'] = {"rdf": "foaf:homepage", "range": InformationObject, "okayToUse": 1}
	BaseResource._properties['webpage'] = {"rdf": "foaf:page", "range": InformationObject, "okayToUse": 1}
	BaseResource._properties['exact_match'] = {"rdf": "skos:exactMatch", "range": BaseResource, "okayToUse": 1}
	BaseResource._properties['close_match'] = {"rdf": "skos:closeMatch", "range": BaseResource, "okayToUse": 1}	
	ManMadeThing._properties['conforms_to'] = {"rdf": "dcterms:conformsTo", "range": BaseResource, "okayToUse": 1}
	InformationObject._properties['format'] = {"rdf": "dc:format", "range": str, "okayToUse": 1}
	BaseResource._properties['related'] = {"rdf": "dcterms:relation", "range": BaseResource, "okayToUse": 1}

# Require explicit addition of rdf:value 
def add_rdf_value():
	SymbolicObject._properties['value'] = {"rdf": "rdf:value", "range": str, "okayToUse": 1}
	Dimension._properties['value'] = {"rdf": "rdf:value", "range": str, "okayToUse": 1}
