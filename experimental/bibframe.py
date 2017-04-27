import model
from model import CromulentFactory, build_classes, \
	KEY_ORDER_HASH, KEY_ORDER_DEFAULT

factory = CromulentFactory("http://lod.example.org/museum/", \
	load_context=False)
build_classes("utils/bibframe_vocab.tsv", top="rdf:Resource")
model.factory = factory