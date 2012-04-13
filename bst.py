"""
Copyright (C) 2011 by Panagiotis Tigkas <ptigas@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import fileinput
import re
import json


def clear_comments(data):
    """Return the bibtex content without comments"""
    res = re.sub(r"(%.*\n)", '', data)
    res = re.sub(r"(comment [^\n]*\n)", '', res)
    res = re.sub(r"(\n)", ' ', res)
    res = re.sub(r"(\t)", " ", res)
    res = re.sub(r"(  )", " ", res)
    return res

class Bstparser :
	def tokenize(self) :
		"""Returns a token iterator"""        
		for item in self.token_re.finditer(self.data):
			i = item.group(0)
			if self.white.match(i) :
				if self.nl.match(i) :
					self.line += 1
				continue
			else :
				yield i            

	def __init__(self, data) :
		self.data = data
		self.token = None
		self.token_type = None
		self._next_token = self.tokenize().next
		self.hashtable = {}
		self.mode = None
		self.records = {}        
		self.line = 1
		self.last_called_function = None

		# compile some regexes
		self.white = re.compile(r"[\n|\s]+")
		self.nl = re.compile(r"[\n]")
		self.token_re = re.compile(r"([^\s\"%(){}@,]+|#\d+|:=|\n|@|\"|{|}|=|,)")

	def next_token(self):
		"""Returns next token"""        
		self.token = self._next_token()

	def parse(self) :
		"""Parses self.data and stores the parsed bibtex to self.rec"""
		while True :
			try :
				self.next_token()

				# print self.token

				if self.token == 'ENTRY' :
					self.entry()
				elif self.token == 'INTEGERS' :	
					self.integers()
				elif self.token == 'FUNCTION' :	
					self.function()
				elif self.token == 'ITERATE' :	
					self.iterate()
				elif self.token == 'MACRO' :
					self.macro()
				elif self.token == 'EXECUTE' :
					self.execute()
				elif self.token == 'READ' :
					self.read()
				elif self.token == 'REVERSE' :
					self.reverse()
				elif self.token == 'SORT' :
					self.sort()
				elif self.token == 'STRINGS' :
					self.strings()
				else :					
					raise NameError("Expecting a command. I got %s" % self.token)
				
			except StopIteration :
				break

	def eat_except( self, s ):
		while True:
			if self.token == s :
				break;
			#print self.token
			self.next_token()

	def entry(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()

			self.eat_except('}') ###
			
			if self.token == '}' :
				self.next_token()
				if self.token == '{' :
					self.next_token()

					self.eat_except('}') ###
					
					if self.token == '}' :
						self.next_token()
						if self.token == '{' :
							self.next_token()

							self.eat_except('}') ###

							if self.token == '}' :
								return
							else :
								raise NameError("} expected 6")	
						else:
							raise NameError("{ expected 5")
					else:
						raise NameError("} expected 4")							
				else :
					raise NameError("{ expected 3")
			else :
				raise NameError("} expected 2")
		else :
			raise NameError("{ expected 1")		

	def integers(self):
		integer_list = []
		self.next_token()
		if self.token == '{' :
			self.next_token()

			while True :
				if self.token == '}' :
					break
				integer_list.append(self.token)
				self.next_token()
			print "INTEGERS", integer_list
		else :
			raise NameError("{ expected 2")

	def function(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()

			# Get name
			print "FUNCTION", self.token
			self.next_token()			
			
			if self.token == '}' :
				self.next_token()
				bracket = 0
				if self.token == '{' :
					bracket += 1
					self.next_token()

					while True:
						if self.token == '}' :
							bracket -= 1
							if bracket == 0 :
								break
						if self.token == '{' :
							bracket += 1
						self.next_token()


					if self.token == '}' and bracket == 0:
						return
					else:
						raise NameError("} expected 4")							
				else :
					raise NameError("{ expected 3")
			else :
				raise NameError("} expected 2")
		else :
			raise NameError("{ expected 1")	

	def macro(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()

			# Get name
			print "MACRO", self.token
			self.next_token()			
			
			if self.token == '}' :
				self.next_token()
				bracket = 0
				if self.token == '{' :
					bracket += 1
					self.next_token()

					while True:
						if self.token == '}' :
							bracket -= 1
							if bracket == 0 :
								break
						if self.token == '{' :
							bracket += 1
						self.next_token()


					if self.token == '}' and bracket == 0:
						return
					else:
						raise NameError("} expected 4")							
				else :
					raise NameError("{ expected 3")
			else :
				raise NameError("} expected 2")
		else :
			raise NameError("{ expected 1")	

	def execute(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()

			# Get name
			print "EXECUTE", self.token			

			self.eat_except('}') ###
		else :
			raise NameError("{ expected 2")

	def read(self):
		pass		

	def reverse(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()			
			self.eat_except('}') ###
		else :
			raise NameError("{ expected 2")

	def sort(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()			
			self.eat_except('}') ###
		else :
			raise NameError("{ expected 2")

	def iterate(self):
		self.next_token()
		if self.token == '{' :
			self.next_token()			
			self.eat_except('}') ###
		else :
			raise NameError("{ expected 2")

	def strings(self):
		integer_list = []
		self.next_token()
		if self.token == '{' :
			self.next_token()

			while True :
				if self.token == '}' :
					break
				integer_list.append(self.token)
				self.next_token()
			print "STRINGS", integer_list
		else :
			raise NameError("{ expected 2")

def main() :
    """Main function"""

    # TODO: Probably a solution with iterations will be better
    data = ""
    for line in fileinput.input():
        line = line.rstrip()        
        data += line + "\n"

	data = clear_comments(data)	
	bst = Bstparser(data)
    bst.parse()    
    
if __name__ == "__main__" :
    main()