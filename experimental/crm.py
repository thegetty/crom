import model
from model import CromulentFactory, build_classes, \
	KEY_ORDER_HASH, KEY_ORDER_DEFAULT

factory = CromulentFactory("http://lod.example.org/museum/", \
	context="http://linked.art/ns/context/1/full.jsonld")
build_classes()
model.factory = factory