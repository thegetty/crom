
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

import inspect
from .model import Activity, MonetaryAmount, Actor, Place, Right, InformationObject, \
	ManMadeThing, BaseResource, Type, Dimension, SymbolicObject, ManMadeObject, \
	LinguisticObject	

# New Payment Activity
class Payment(Activity):
	_properties = {
		"paid_amount": {"rdf": "la:paid_amount", "range": MonetaryAmount, "okayToUse": 1, "multiple": 0},
		"paid_to": {"rdf": "la:paid_to", "range": Actor, "okayToUse": 1, "multiple": 0},
		"paid_from": {"rdf": "la:paid_from", "range": Actor, "okayToUse": 1, "multiple": 0}
	}
	_uri_segment = "Payment"
	_type = "la:Payment"
Payment._classhier = inspect.getmro(Payment)[:-1]

def add_linkedart_properties():
	Activity._properties['brought_into_effect'] = \
		{"rdf": "la:brought_into_effect", "range": Right, "okayToUse": 1, "multiple": 1}
	Activity._properties['took_out_of_effect'] = \
		{"rdf": "la:took_out_of_effect", "range": Right, "okayToUse": 1, "multiple": 1}
	Right._properties['effective_in'] = \
		{"rdf": "la:effective_in", "range": Place, "okayToUse": 1, "multiple": 1}

# Require explict addition of extra shortcut properties
def add_schema_properties():
	ManMadeObject._properties['style'] = {"rdf": "schema:genre", "range": Type, "okayToUse": 1, "multiple": 1}
	ManMadeObject._properties['subject'] = {"rdf": "dct:subject", "range": Type, "okayToUse": 1, "multiple": 1}
	BaseResource._properties['exact_match'] = {"rdf": "skos:exactMatch", "range": BaseResource, "okayToUse": 1, "multiple": 1}
	BaseResource._properties['close_match'] = {"rdf": "skos:closeMatch", "range": BaseResource, "okayToUse": 1, "multiple": 1}	
	ManMadeThing._properties['conforms_to'] = {"rdf": "dcterms:conformsTo", "range": BaseResource, "okayToUse": 1, "multiple": 0}
	InformationObject._properties['format'] = {"rdf": "dc:format", "range": str, "okayToUse": 1, "multiple": 0}
	BaseResource._properties['related'] = {"rdf": "dcterms:relation", "range": BaseResource, "okayToUse": 1, "multiple": 1}

# Require explicit addition of rdf:value 
def add_rdf_value():
	SymbolicObject._properties['value'] = {"rdf": "rdf:value", "range": str, "okayToUse": 1, "multiple": 0}
	Dimension._properties['value'] = {"rdf": "rdf:value", "range": str, "okayToUse": 1, "multiple": 0}
