import os, sys

from cromulent import model, vocab, reader
r = reader.Reader()

vocab.conceptual_only_parts()
vocab.add_attribute_assignment_check()


base = '/Users/rsanderson/Development/linked-art/linked.art/content/example'

stuff = []

dirs = os.listdir(base)
for d in dirs:
	if not '.' in d:
		files = os.listdir(os.path.join(base, d))
		files.sort()
		for f in files:
			if f.endswith('.json'):
				fn = os.path.join(base, d, f)
				print(fn)
				fh = open(fn)
				data = fh.read()
				fh.close()
				w = r.read(data)
				stuff.append(w)
