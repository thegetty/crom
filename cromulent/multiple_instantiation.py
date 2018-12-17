
# This assumes the default CIDOC-CRM, even though the model code 
# can generate classes for any ontology

import inspect
from cromulent.model import Destruction, EndOfExistence, Activity, Appellation, LinguisticObject	

# DestuctionActivity class as CRM has a Destruction Event and recommends multi-classing
# WARNING:  instantiating this class in the default profile will raise an error

class DestructionActivity(Destruction, Activity):
	_uri_segment = "Activity"
	_type = ["crm:E6_Destruction", "crm:E7_Activity"]
	_niceType = ["Destruction", "Activity"]
DestructionActivity._classhier = inspect.getmro(DestructionActivity)[:-1]

# And hence we make an EndOfExistence+Activity class
# for all activities that end existences
class EoEActivity(EndOfExistence, Activity):
	_uri_segment = "Activity"
	_type = ["crm:64_End_of_Existence", "crm:E7_Activity"]
	_niceType = ["EndOfExistence", "Activity"]	
EoEActivity._classhier = inspect.getmro(EoEActivity)[:-1]

# And a LinguisticAppellation
class LinguisticAppellation(Appellation, LinguisticObject):
	_uri_segment = "Appellation"
	_type = ["crm:E41_Appellation", "crm:E33_Linguistic_Object"]
	_niceType  = ["Appellation", "LinguisticObject"]
LinguisticAppellation._classhier = inspect.getmro(LinguisticAppellation)[:-1]
