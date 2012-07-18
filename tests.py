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

class TestNumOp(unittest.TestCase):

	def testAddition(self):
		global bib_data
		bst.STACK = ""

		f = """
		FUNCTION {test}
		{
		"asdf"
		}
		"""

		bst_data = prepare( f, 'test' )

		bst.Bstparser( bst_data, bib_data ).parse()

		#self.assertEqual( bst.STACK[-1], 'asdf' )

if __name__ == '__main__':
    unittest.main()