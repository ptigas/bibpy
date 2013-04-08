from bib import *
import glob

for example in glob.glob('tests/*.bib') :
	print 'Testing', example,'...',
	data = clear_comments(open(example, 'r').read())
	bib = Bibparser(data)
	bib.parse()
	data = bib.json()
	print 'done'