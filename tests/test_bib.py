from nose.tools import *
from bibpy import *
import glob

def test_parsing():	
	for example in glob.glob('*.bib') :
		yield parse_bib, example

def parse_bib(f):	
	data = clear_comments(open(f, 'r').read())
	bib = Parser(data)
	bib.parse()
	data = bib.json()	