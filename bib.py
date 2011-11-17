import fileinput
import sys
import re

#token_re = re.compile("\s*([\w|\d|'|.]+|@|\"|{|}|=)")
token_re = re.compile(r"\s*([^\s\"#%'(){}@,=]+|@|\"|{|}|=|,)")

def clear_comments(data):
	res = re.sub(r"(%.*\n)",'',data)
	res = re.sub(r"(comment [^\n]*\n)",'',res)
	return res

def tokenize(data):
    for item in token_re.finditer(data):
        i = item.group(0)
        yield re.sub(r"[\n|\s]*",'',i) # eat new line chars

data = ""
for line in fileinput.input():
	line = line.rstrip()
	#print line
	data += line + "\n"

data = clear_comments(data)
next_token = tokenize(data).next

t = None

def ERROR( s ) :
	print "ERROR: %s" % s
	sys.exit(-1)

def key() :
	global t
	print "KEY: %s"%t
	t = next_token()

def record() :
	global t	
	if t not in ['comment','string','preample'] :
		print "RECORD NAME: %s" % t
		t = next_token()
		if t == '{' :
			t = next_token()
			key()
			if t == ',' :				
				while True:
					t = next_token()
					field()					
					if t <> ',' :						
						break				
				if t == '}' :
					pass
				else :
					if t == '@' : # assume closed
						pass
					else :
						print t
						ERROR("1")

def name() :
	global t
	#print t
	print "NAME: %s" % t
	t = next_token()


def value() :
	global t
	if t == '"' :		
		val = []
		while True:
			t = next_token()
			if t == '"' :
				break
			else :
				val.append(t)
		print "VAL: %s"%' '.join(val)
		if t == '"' :			
			t = next_token()
		else :
			ERROR("2")
	elif t == '{' :
		val = []
		c = 0
		while True:
			t = next_token()
			if t == '{' :
				c +=1
			if t == '}' :				
				c -= 1
			if c < 0 :
				break
			else :
				val.append(t)
		print "VAL: %s"%' '.join(val)
		if t == '}' :
			t = next_token()
		else :
			ERROR("3")
	elif t.isdigit() :
		t = next_token()
	else :
		t = next_token()

def field() :
	global t
	name()	
	if t == '=' :
		t = next_token()		
		value()		

def string() :
	global t
	if t == "string" :
		t = next_token()
		if t == "{" :
			t = next_token()
			field()
			if t == "}" :
				pass
			else :
				ERROR("5")

def entry() :
	global t	
	if t == 'string' :
		string()
	else :
		record()

def database() :
	global t
	if t == '@' :
		t = next_token()
		entry()

def parse():
	global t
	while True :
		try :
			t = next_token()
			while database() :
				pass			
		except StopIteration :
			break
	#print next_token()

parse()