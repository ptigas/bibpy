Bibpy
===

About
---
Bibpy is a (yet another) BibTex file parser in python. 

What's  different ? 
---
It does not depend on libraries like pyparser etc. It's small and fast. Also, *sometimes* it recovers from common errors.

What grammar is parsing ?
---
The BNF it parse is based on http://tex.stackexchange.com/questions/16490/the-gold-standard-in-bibtex-databases/16492#16492

```
A rough grammar (case-insensitive):

 Database  ::= (Junk '@' Entry)*
 Junk      ::= .*?
 Entry 	   ::= Record | Comment | String | Preamble
 Comment   ::= "comment" [^\n]* \n     -- ignored
 String    ::= "string" '{' Field* '}'
 Preamble  ::= "preamble" '{' .* '}'   -- (balanced)
 Record    ::= Type '{' Key ',' Field* '}'
       	   |   Type '(' Key ',' Field* ')' -- not handled
 Type  	   ::= Name
 Key   	   ::= Name
 Field     ::= Name '=' Value
 Name      ::= [^\s\"#%'(){}]*
 Value ::= [0-9]+
       |   '"' ([^'"']|\\'"')* '"'
       |   '{' .* '}'          -- (balanced)
```

TODO
---
This libraries is part of a citation sharing service, stay tunned.


License
---
(The MIT License)

Copyright (c) 2011 Panagiotis Tigkas

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.