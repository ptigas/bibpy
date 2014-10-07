ENTRY {}{}{}

FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}

FUNCTION {and}
{   'skip$
    { pop$ #0 }
  if$
}

FUNCTION {or}
{   { pop$ #1 }
    'skip$
  if$
}

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

FUNCTION {a}
{
	"this is a" 's :=
	s
}

FUNCTION {test}
{
	'a write$
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

EXECUTE{format.names}