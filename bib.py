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
    return res


last_called_function = None
def log( f ):
    global last_called_function
    last_called_function = f.__name__
    print f.__name__
    return f

class Bibparser() :
    """Main class for Bibtex parsing"""

    def tokenize(self) :
        """Returns a token iterator"""
        white = re.compile(r"[\n|\s]+")
        token_re = re.compile(r"([^\"#%'(){}@,=]+|@|\"|{|}|=|,)")
        for item in token_re.finditer(self.data):
            i = item.group(0)
            if white.match(i) :
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
        self.line = 0
        self.last_called_function = None    
    
    def parse(self) :
        """Parses self.data and stores the parsed bibtex to self.rec"""
        while True :
            try :
                self.next_token()               
                while self.database() :
                    pass            
            except StopIteration :
                break
    
    def next_token(self):
        """Returns next token"""
        global last_called_function
        self.token = self._next_token()
        print self.line, last_called_function, self.token
    
    @log
    def database(self) :
        """Database"""
        if self.token == '@' :
            self.next_token()
            self.entry()
    
    @log
    def entry(self) :  
        """Entry"""     
        if self.token == 'string' :
            self.mode = 'string'
            self.string()
            self.mode = None
        else :
            self.mode = 'record'            
            self.record()
            self.mode = None

    @log
    def string(self) :   
        """String"""   
        if self.token == "string" :
            self.next_token()
            if self.token == "{" :
                self.next_token()
                self.field()
                if self.token == "}" :
                    pass
                else :                      
                    raise NameError("} missing")
    
    @log
    def field(self) :
        """Field"""
        name = self.name()
        if self.token == '=' :
            self.next_token()
            value = self.value()            
            if self.mode == 'string' :
                self.hashtable[name] = value
            return (name, value)            
    
    @log
    def value(self) :
        """Value"""
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
            brac_counter = 0
            while True:
                self.next_token()
                if self.token == '{' :
                    brac_counter += 1
                if self.token == '}' :              
                    brac_counter -= 1
                if brac_counter < 0 :
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
            if self.token in self.hashtable :
                value = self.hashtable[ self.token ]
            else :
                value = self.token          
            self.next_token()

        return value
    
    @log
    def name(self) :
        """Returns parsed Name"""
        name = self.token       
        self.next_token()
        return name

    @log
    def key(self) : 
        """Returns parsed Key"""    
        key = self.token
        self.next_token()
        return key

    @log
    def record(self) : 
        """Record""" 
        if self.token not in ['comment', 'string', 'preample'] :          
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
                            val = field[1]
                            self.records[ key ][k] = val
                        if self.token != ',' :                      
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
        """Returns json formated records"""
        return json.dumps(self.records)

def main() :
    """Main function"""
    data = ""
    for line in fileinput.input():
        line = line.rstrip()
        #print line
        data += line + "\n"

    data = clear_comments(data)
    
    bib = Bibparser(data)
    bib.parse()
    #print bib.json()
    
if __name__ == "__main__" :
    main()