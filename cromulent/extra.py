
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

import inspect
from .model import Destruction, Activity, Purchase, MonetaryAmount, Actor, Place, \
	Type, Dimension, SymbolicObject, Person, ManMadeObject, PhysicalObject, CRMEntity, \
	InformationObject, ManMadeThing, BaseResource

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
	Person._properties['family_name'] = {"rdf": "schema:familyName", "range": str}
	Person._properties['given_name'] = {"rdf": "schema:givenName", "range": str}
	Person._properties['nationality'] = {"rdf": "schema:nationality", "range": Place}
	ManMadeObject._properties['genre'] = {"rdf": "schema:genre", "range": Type}
	ManMadeObject._properties['height'] = {"rdf": "schema:height", "range": Dimension}
	ManMadeObject._properties['width'] = {"rdf": "schema:width", "range": Dimension}
	ManMadeObject._properties['subject'] = {"rdf": "dct:subject", "range": Type}
	BaseResource._properties['homepage'] = {"rdf": "foaf:homepage", "range": InformationObject}
	BaseResource._properties['webpage'] = {"rdf": "foaf:page", "range": InformationObject}
	BaseResource._properties['exact_match'] = {"rdf": "skos:exactMatch", "range": BaseResource}
	ManMadeThing._properties['conforms_to'] = {"rdf": "dcterms:conformsTo", "range": BaseResource}
	InformationObject._properties['format'] = {"rdf": "dc:format", "range": str}
	BaseResource._properties['related'] = {"rdf": "dcterms:relation", "range": BaseResource}

# Require explicit addition of rdf:value 
def add_rdf_value():
	SymbolicObject._properties['value'] = {"rdf": "rdf:value", "range": str}
	Dimension._properties['value'] = {"rdf": "rdf:value", "range": str}

