Bibpy
===

About
---
Bibpy is a (yet another) BibTex file parser in python. 

What's the difference with other parsers ? 
---
It doesn't depend on libraries like pyparser etc. It's small and fast ( O(n) ).

What language does it parse ?
---
The BNF it parse is based on http://tex.stackexchange.com/questions/16490/the-gold-standard-in-bibtex-databases/16492#16492

```
A rough grammar (case-insensitive):

 Database  ::= (Junk '@' Entry)*
 Junk      ::= .*?
 Entry ::= Record
       |   Comment
       |   String
       |   Preamble
 Comment   ::= "comment" [^\n]* \n     -- ignored
 String    ::= "string" '{' Field* '}'
 Preamble  ::= "preamble" '{' .* '}'   -- (balanced)
 Record    ::= Type '{' Key ',' Field* '}'
       |   Type '(' Key ',' Field* ')' -- not handled
 Type  ::= Name
 Key   ::= Name
 Field ::= Name '=' Value
 Name      ::= [^\s\"#%'(){}]*
 Value ::= [0-9]+
       |   '"' ([^'"']|\\'"')* '"'
       |   '{' .* '}'          -- (balanced)
```
