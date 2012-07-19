import bst
import unittest

bib_data = """
@article{Alba2004a,
author = {Alba, Enrique and Dorronsoro, B.},
journal = {Evolutionary Computation in Combinatorial Optimization},
pages = {11--20},
publisher = {Springer},
title = {{Solving the vehicle routing problem by using cellular genetic algorithms}},
url = {http://www.springerlink.com/index/YNNJ6QTTMPXCN71H.pdf},
year = {2004}
}

@article{Berger2003,
author = {Berger, Jean and Barkaoui, Mohamed},
issn = {0160-5682},
journal = {Journal of the Operational Research Society},
number = {12},
pages = {1254--1262},
publisher = {Nature Publishing Group},
title = {{A new hybrid genetic algorithm for the capacitated vehicle routing problem}},
url = {http://www.palgrave-journals.com/jors/journal/v54/n12/abs/2601635a.html},
volume = {54},
year = {2003}
}
""";

bst_data = """
ENTRY {}{}{}

FUNCTION {not}{ {#0} {#1} if$ }
FUNCTION {and} { 'skip$ { pop$ #0 } if$ }
FUNCTION {or} { { pop$ #1 } 'skip$ if$ }

FUNCTION {n.dashify}
{ "a b c-d e" 't :=
  ""
    { t empty$ not }
    { t #1 #1 substring$ "-" =
		{ t #1 #2 substring$ "--" = not
		    { "--" *
		      t #2 global.max$ substring$ 't :=
		    }
		    {   
		    	{ t #1 #1 substring$ "-" = }
				{ "-" *
			  		t #2 global.max$ substring$ 't :=
				}
		      	while$
		    }
		  if$
		}
		{ t #1 #1 substring$ *
		  t #2 global.max$ substring$ 't :=
		}
      	if$
    }
  	while$
}

FUNCTION {format.names}
{
	"Berger , Jean and Barkaoui , Mohamed"
	's :=
	#1 'nameptr :=
	s num.names$ 'numnames :=
	numnames 'namesleft :=
	{ namesleft #0 > }
	{ 
		s nameptr "{ff~}{vv~}{ll}{, jj}" format.name$ 't :=
		nameptr #1 >
		{ namesleft #1 >
			{ ", " * t * }
			{ numnames #2 >
				{ "," * }
				'skip$
				if$
	      		t "others" =
			{ " et~al." * }
			{ " and " * t * }
	      	if$
	    }
	    if$
	}
	't
	if$
	nameptr #1 + 'nameptr :=
	namesleft #1 - 'namesleft :=
	}
	while$
}

READ
EXECUTE{n.dashify}
"""

def prepare( func, name ) :
	data =  """
		ENTRY {}{}{}
		%s
		READ
		EXECUTE{ %s }
		""" % (func, name) 
	return data

class TestStack(unittest.TestCase):
	def testEmptyStack(self) :		
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} {}"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )		
		self.assertEqual( b.pop(), '' )

	def testPushPop(self) :		
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} {}"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )	
		b.push('#1')
		b.push('#2')			
		self.assertEqual( b.pop(), '#2' )

		b.push('adsf')
		b.push('a2323')			
		self.assertEqual( b.pop(), 'a2323' )

		b.push('')
		self.assertEqual( b.pop(), '' )

class TestStringOp(unittest.TestCase):
	def testConcat(self) :		
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "abcd" "efg" * }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), 'abcdefg' )

	def testEmptyConcat(self) :		
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "" "" * }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), '' )

		bst.STACK = [] # empty stack
		f = """FUNCTION {test} {  * }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), '' )

	def testAddPeriod(self) :		
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "asdf" add.period$ }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), 'asdf.' )

		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "asd}}" add.period$ }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), 'asd.}}' )

		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "}}}" add.period$ }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), '}}}' )

		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { "asdf!" add.period$ }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), 'asdf!' )

	def testQuote( self ) :
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { quote$ }"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), '"' )

class TestIfWhile(unittest.TestCase) :
	def testWhile( self ) :
		bst.STACK = [] # empty stack
		f = """FUNCTION {test} { 
			#10 't :=
			#0 'i :=
			{ t #1 - 't := t }
			{
			i #1 + 'i :=
			}
			while$
			i
		}"""
		bst_data = prepare( f, 'test' )
		b = bst.Bstparser( bst_data, bib_data )
		b.parse()	
		self.assertEqual( b.pop(), '#9' )

class TestNumOp(unittest.TestCase):
	def testString(self):
		global bib_data		
		f = """FUNCTION {test} { "asdf" }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], 'asdf' )

	def testNumber(self):
		global bib_data		
		f = """FUNCTION {test} { "#1" }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#1' )

	def testAddition(self):
		global bib_data		
		f = """FUNCTION {test} { #10 #123 + }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#133' )

		f = """FUNCTION {test} { #10 #-100 + }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#-90' )

	def testSubstraction(self):
		f = """FUNCTION {test} { #100 #10 - }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#90' )

	def testMore(self):
		f = """FUNCTION {test} { #1 #2 > }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

		f = """FUNCTION {test} { #2 #1 > }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#1' )

		f = """FUNCTION {test} { #1 #1 > }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

	def testLess(self):
		f = """FUNCTION {test} { #1 #2 < }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#1' )

		f = """FUNCTION {test} { #2 #1 < }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

		f = """FUNCTION {test} { #1 #1 < }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

	def testEquals(self):
		f = """FUNCTION {test} { #100 #100 = }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#1' )

		f = """FUNCTION {test} { #100 #90 = }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

		f = """FUNCTION {test} { "asd" #90 = }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#0' )

		f = """FUNCTION {test} { "asd" "asd" = }"""
		bst_data = prepare( f, 'test' )
		bst.Bstparser( bst_data, bib_data ).parse()
		self.assertEqual( bst.STACK[-1], '#1' )

if __name__ == '__main__':
    unittest.main()