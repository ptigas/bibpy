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
import sys
import re
import json

def clear_comments(data):
	res = re.sub(r"(%.*\n)",'',data)
	res = re.sub(r"(comment [^\n]*\n)",'',res)
	return res

def tokenize(data):
    for item in token_re.finditer(data):
        i = item.group(0)
        yield re.sub(r"[\n|\s]*",'',i) # eat new line chars

def ERROR(s) :
	print "ERROR: %s" % s 
	sys.exit(-1)

class Bibparser() :
	def tokenize(self) :
		white = re.compile(r"[\n|\s]+")
		token_re = re.compile(r"([^\s\n\"#%'(){}@,=]+|@|\"|{|}|=|,)")
		for item in token_re.finditer(self.data):
			i = item.group(0)			
			yield white.sub('',i)			

	def __init__(self, data) :
		self.data = data	
		self.token = None
		self.token_type = None
		self._next_token = self.tokenize().next
		self.db = {}
		self.mode = None
		self.records = {}
		self.line = 1

	def parse(self) :
		while True :
			try :
				self.next_token()				
				while self.database() :
					pass			
			except StopIteration :
				break

	def next_token(self):
		self.token = self._next_token()		
	
	def database(self) :
		if self.token == '@' :
			self.next_token()
			self.entry()
	
	def entry(self) :		
		if self.token == 'string' :
			self.mode = 'string'
			self.string()
			self.mode = None
		else :
			self.mode = 'record'
			self.record()
			self.mode = None

	def string(self) :		
		if self.token == "string" :
			self.next_token()
			if self.token == "{" :
				self.next_token()
				self.field()
				if self.token == "}" :
					pass
				else :						
					raise NameError("} missing")
	
	def field(self) :
		name = self.name()
		if self.token == '=' :
			self.next_token()
			value = self.value()			
			if self.mode == 'string' :
				self.db[name] = value
			return (name, value)			
	
	def value(self) :
		value = ""
		if self.token == '"' :		
			val = []
			while True:
				self.next_token()
				if self.token == '"' :
					break
				else :
					val.append(self.token)
			value = ' '.join(val)
			if self.token == '"' :			
				self.next_token()
			else :
				raise NameError("\" missing")
		elif self.token == '{' :
			val = []
			c = 0
			while True:
				self.next_token()
				if self.token == '{' :
					c +=1
				if self.token == '}' :				
					c -= 1
				if c < 0 :
					break
				else :
					val.append(self.token)
			value = ' '.join(val)
			if self.token == '}' :
				self.next_token()
			else :
				raise NameError("} missing")
		elif self.token.isdigit() :
			value = self.token
			self.next_token()
		else :
			if self.token in self.db :
				value = self.db[ self.token ]
			else :
				value = self.token			
			self.next_token()

		return value
	
	def name(self) :
		name = self.token		
		self.next_token()
		return name

	def key(self) :		
		key = self.token
		self.next_token()
		return key

	def record(self) :	
		if self.token not in ['comment','string','preample'] :			
			self.next_token()
			if self.token == '{' :
				self.next_token()
				key = self.key()
				self.records[ key ] = {}
				if self.token == ',' :				
					while True:
						self.next_token()
						field = self.field()
						if field :
							k = field[0]
							v = field[1]
							self.records[ key ][k] = v
						if self.token <> ',' :						
							break				
					if self.token == '}' :
						pass
					else :
						# assume entity ended
						if self.token == '@' :
							pass
						else :
							print self.token
							raise NameError("@ missing")
	
	def json(self) :
		return json.dumps(self.records)

def main() :
	data = ""
	for line in fileinput.input():
		line = line.rstrip()
		#print line
		data += line + "\n"

	data = clear_comments(data)
	
	bib = Bibparser(data)
	bib.parse()

	print bib.json()
	sys.exit(-1)
	for key in parser.records :
		print key	
		for attr in parser.records[key] :		
			if attr :
				print "\t %s : %s" % (attr, parser.records[key][attr])

if __name__ == "__main__" :
	main()