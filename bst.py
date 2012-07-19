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
import sys
import bib

def clear_comments(data):
    """Return the bibtex content without comments"""
    res = re.sub(r"(%.*\n)", '', data)
    res = re.sub(r"(comment [^\n]*\n)", '', res)
    res = re.sub(r"(\n)", ' ', res)
    res = re.sub(r"(\t)", " ", res)
    res = re.sub(r"(  )", " ", res)
    return res

MAX_ITER = 100

ENTRY = None

STACK = []

FUNCTIONS = {}

BUFFER = ""

VARIABLES = {}

class Function :
    OPS = {
            ':=' : {
                'arguments' : 2,
                'function'  : 'assign'
            },
            '>' : {
                'arguments' : 2,
                'function'  : 'less'
            },
            '<' : {
                'arguments' : 2,
                'function'  : 'more'
            },
            '=' : {
                'arguments' : 2,
                'function'  : 'eq'
            },
            '+' : {
                'arguments' : 2,
                'function'  : 'iadd'
            },
            '-' : {
                'arguments' : 2,
                'function'  : 'isub'
            },
            '*' : {
                'arguments' : 2,
                'function'  : 'concat'
            },
            'pop$' : {
                'arguments' : 0,
                'function'  : 'pop'
            },
            "'skip$" : {
                'arguments' : 0,
                'function'  : 'skip'
            },
            "global.max$" : {
                'arguments' : 0,
                'function'  : 'global_max'
            },
            'if$' : {
                'arguments' : 1,
                'function'  : 'iff'
            },
            'while$'   : {
                'arguments' : 2,
                'function'  : '_while'
            },            
            'swap$' : {
                'arguments' : 2,
                'function'  : 'swap'
            },
            'write$' : {
                'arguments' : 1,
                'function'  : 'write'
            },
            'newline$' : {
                'arguments' : 0,
                'function'  : 'newline'
            },
            'call.type$': {
                'arguments' : 1,
                'function' : 'call_type'
            },
            'preamble$' : {
                'arguments' : 0,
                'function'  : 'preample'
            },
            'add.period$' : {
                'arguments' : 1,
                'function'  : 'add_period'
            },
            'empty$' : {
                'arguments' : 1,
                'function'  : 'empty'
            },
            'missing$' :{
                'arguments' : 1,
                'function'  : 'missing',
            },
            'duplicate$' : {
                'arguments' : 1,
                'function'  : 'duplicate'
            },
            'substring$' : {
                'arguments' : 3,
                'function'  : 'substring'
            },
            'cite$' : {
                'arguments' : 0,
                'function'  : 'cite'
            },
            'int.to.str$'   : {
                'arguments' : 1,
                'function'  : 'int2str'
            },
            'width$'        : {
                'arguments' : 0,
                'function'  : 'width'
            },
            'num.names$'    : {
                'arguments' : 1,
                'function'  : 'num_names'
            },
            'format.name$'  : {
                'arguments' : 3,
                'function'  : 'format_names'
            }

        }

    def __init__(self, name, commands, external_entries ):
        self.name = name
        self.commands = commands        
        self.external_entries = external_entries

    def int2str( self, n ) :
        global VARIABLES
        n = self._lookup( n )
        print 'int2str', n, VARIABLES
        self.push( str(n) )

    def is_op( self, s ) :
        global FUNCTIONS
        global STACK
        
        if s[0] == "'" and s[1:] in FUNCTIONS :
            s = s[1:]
            Function( s, FUNCTIONS[ s ], self.external_entries ).execute()            
            return {'arguments':1,'function':'push'}

        if type(s) == type(()) :
            return ( self.OPS[s[0]], s[1:] )

        if s in self.OPS :
            print s, 'is op. executing.'
            return self.OPS[s]

        if s in VARIABLES :
            self.push( VARIABLES[s] )
            return {'arguments':0,'function':'skip'}

        if s in FUNCTIONS:
            print s, 'is function. executing.'
            Function( s, FUNCTIONS[ s ], self.external_entries ).execute()
            return {'arguments':0,'function':'skip'}
        print "STACK: ", STACK
        return None

    def format_names( self, s2, i, s1 ) :        
        name = s1.split(' and ')[ self._lookup(i)-1 ]
        self.push( name )

    def cite( self ):
        global ENTRY
        # should add the cite key
        self.push( ENTRY['key'] )

    def duplicate( self, a ) :
        self.push( a )
        self.push( a )

    def global_max( self ) :
        self.push( '#100' )

    def add_period( self, a ):
        i = len(a) - 1        
        while i >= 0 :
            print '-', a[i]
            if a[i] != '}' :
                break
            i -= 1

        if a[i] not in ['.','!','?','}'] :
            self.push( a[:i+1] + '.' + a[i+1:] )
        else :
            self.push( a )

    def missing( self, a ) :
        global ENTRY
        try :
            ENTRY[a]
            self.push('0')
        except KeyError :
            self.push('1')            

    def empty( self, a ):
        print '++++++++++++', a, a == ''
        if a == '' :
            self.push('1')
            print "----- 1"
        else :
            self.push('0')
            print "----- 0"

    def num_names( self, s ) :
        self.push( s.count(' and ') + 1 )

    def width( self ) :
        self.push('#100')

    def preample( self ) :
        self.push('FU')

    def write( self, a ) :
        print "writing", a
        global BUFFER
        BUFFER += str(a)

    def newline( self ) :
        global BUFFER
        BUFFER += "\n"

    def swap( self, a, b ):
        self.push(a)
        self.push(b)

    def substring( self, ln, start, s ) :
        global STACK
        l = len(s)
        ln = self._lookup(ln)
        start = self._lookup(start)
        if start > 0 :
            self.push( s[start-1:min(ln+start-1,l)] )
        else :
            self.push( s[:-start:-1] )
        print "STL:", STACK

    def iff( self, b, y, n ) :            
        if int(b) > 0 :            
            #Function( 'foo', y, self.external_entries ).execute()
            self.execute_f(y)
        else :
            #Function( 'foo', n, self.external_entries ).execute()
            self.execute_f(n)        

    def execute_f( self, f ) :
        if type(f) == type([]) :
            Function( 'unknon', f, self.external_entries ).execute()
        else :
            try :
                Function( f, FUNCTIONS[f], self.external_entries ).execute()
            except KeyError :
                Function( f, [f], self.external_entries ).execute()

    def skip(self):
        pass

    def fix_order( self, commands, cmd ) :

        commands_res = []

        for i, command in enumerate(commands) :            
            commands_res.append( command )
            if command == cmd:
                if type(commands[i-2]) == type([]) :
                    f1 = self.fix_order(commands[i-2], cmd)
                    print 'f1'
                else :
                    f1 = commands[i-2]
                
                if type(commands[i-i]) == type([]) :
                    print 'f2'
                    f2 = self.fix_order(commands[i-1], cmd)
                else :
                    f2 = commands[i-1]                    
                
                commands_res.pop()
                commands_res.pop()
                commands_res.pop()                
                commands_res.append( ( cmd, f1, f2 ) )

        return commands_res

    def execute( self, entry = None ):
        global STACK
        global ENTRY        
        print "Executing commands", self.name

        print "YO: ", self.commands
        commands = self.fix_order( self.commands, "if$" )
        commands = self.fix_order( commands, "while$" )
        print "COMMANDS: ", commands

        #print 'BEFOR > ', self.commands
        print ' > ', commands
        for command in commands :

            print 'Executing command:', command
            
            try :
                res = self.is_op( command )
            except :
                res = None
            
            if res <> None :
                
                # gather all arguments
                # and call function
                args = []
                # print "STACK", STACK                
                if type(res) == type(()) :                    
                    f = getattr(self, res[0]['function'])

                    if ( res[0]['function'] == 'iff' ) :                    
                        args.append( self._lookup(self.pop()) )

                    args.append(res[1][0])
                    args.append(res[1][1])                                    
                else :
                    for i in range(res['arguments']) :
                        args.append(self.pop())
                    f = getattr(self, res['function'])                
                
                if f :
                    print "AAA", args
                    f(*args)


            elif command in [ 
                    'volume', 
                    'title', 
                    'month', 
                    'year', 
                    'pages', 
                    'edition', 
                    'note', 
                    'key', 
                    'author', 
                    'volume', 
                    'number', 
                    'journal' ] :
                try :
                    self.push( ENTRY[ command ] )
                except KeyError :
                    self.push('')

            elif type(command) == type([]) :                
                pass
                #print '...', command
                #Function( 'anon', command ).execute()                
                #self.execute_f( command )

            elif re.match(r".*\$$", command):                
                pass
                #print "TRALALA ", command
            
            else :                
                if command[0] == '"' and command[-1] == '"' :
                    command = command[1:-1]
                #STACK.append(command)
                self.push( command )
        
        print "FINISHED EXECUTING %s" % self.name
        #print STACK

    def assign( self, a, b ):
        global VARIABLES
        print "AAAAA := ", a, b
        if len(b) > 0 and b[0] == '#' :
            print "%s := %s" % ( a[1:], int(b[1:]) )
            VARIABLES[ a[1:] ] = int(b[1:])
        else :
            print "%s := %s" % ( a[1:], b )
            VARIABLES[ a[1:] ] = b

    def less( self, a, b ):
        print "%s < %s" % (a,b)
        self.push( a < b and 1 or 0 )

    def more( self, a, b ):
        print "%s > %s" % (a,b)
        self.push( a > b and 1 or 0 )

    def eq( self, a, b ):
        print "%s == %s" % (a,b)
        self.push( a == b and 1 or 0 )

    def concat( self, a, b ):
        global VARIABLES
        try :
            a = VARIABLES[a[1:]]
        except :
            pass
        try :
            b = VARIABLES[b[1:]]
        except :
            pass
        print "concat(%s,%s)" % (b,a)        
        self.push( str(b)+str(a) )

    def isub( self, a, b ):
        print "%s - %s" % (a,b)
        a = self._lookup( a )
        b = self._lookup( b )
        self.push( b - a )

    def iadd( self, a, b ):    
        a = self._lookup( a )
        b = self._lookup( b )        
        print "%s + %s" % (a,b)
        self.push( a + b )

    def pop( self ):        
        global STACK
        try :
            res = STACK.pop()
        except IndexError :
            res = ""
        print "poping: ", res
        return res

    def push( self, item ):
        global STACK
        if type(item) == type(1) or item.isdigit() :
            STACK.append( "#%s" % item )            
        else :
            STACK.append( item )
        print "pushing: ", STACK[-1]

    def _lookup( self, s ) :
        global VARIABLES

        if type(s) == type("") and s[0] == '#' :            
            return int( s[1:] )
        else :
            try :
                return VARIABLES[ s ]
            except KeyError :
                return s

    def _while( self, a, b ) :
        global STACK
        print "WHILE"
        
        i = 0        
        while True :
            self.execute_f(a)            
            res = self._lookup( self.pop() )
            if res == 0 :
                break
            self.execute_f(b)
            i += 1

            if i > MAX_ITER :
                raise Exception( 'MAX_ITER' )

MACROS = {}

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

    def __init__(self, bst_data, bib_data) :        
        self.data = bst_data
        self.token = None
        self.token_type = None
        self._next_token = self.tokenize().next
        self.hashtable = {}
        self.mode = None
        self.records = {}        
        self.line = 1
        self.last_called_function = None
        self.bib_data = bib_data

        tmp = bib.Bibparser( bib_data )
        tmp.parse()

        # compile some regexes
        self.white = re.compile(r"[\n|\s]+")
        self.nl = re.compile(r"[\n]")
        self.token_re = re.compile(r"([^\s\"%(){}@,]+|#\d+|:=|\n|@|\"[^\"]*\"|{|}|=|,)")

        # integer variables list
        self.integer_list = []

    def next_token(self):
        """Returns next token"""
        self.token = self._next_token()        

    def parse(self) :
        """Parses self.data and stores the parsed bibtex to self.rec"""
        while True :
            try :
                self.next_token()

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

    def push( self, item ):
        global STACK
        if type(item) == type(1) or item.isdigit() :
            STACK.append( "#%s" % item )            
        else :
            STACK.append( item )
        print "pushing: ", STACK[-1]

    def pop( self ):        
        global STACK
        try :
            res = STACK.pop()
        except IndexError :
            res = ""
        print "poping: ", res
        return res

    def entry(self):
        self.next_token()
        if self.token == '{' :

            self.next_token()

            # get external entries
            external_entries = {}
            while True:                
                if self.token == '}' :
                    break;
                external_entries[ self.token ] = True
                self.next_token()            
            
            if self.token == '}' :
                self.next_token()
                if self.token == '{' :
                    self.next_token()

                    # get internal integers
                    internal_ints = {}
                    while True:                
                        if self.token == '}' :
                            break;
                        internal_ints[ self.token ] = True
                        self.next_token()                    
                    
                    if self.token == '}' :
                        self.next_token()
                        if self.token == '{' :
                            self.next_token()

                            # get internal string
                            internal_str = {}
                            while True:                
                                if self.token == '}' :
                                    break;
                                internal_str[ self.token ] = True
                                self.next_token()                            

                            if self.token == '}' :

                                self.external_entries = external_entries
                                self.internal_ints = internal_ints
                                self.internal_str = internal_str     

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
        self.integer_list = []
        self.next_token()
        if self.token == '{' :
            self.next_token()

            while True :
                if self.token == '}' :
                    break
                self.integer_list.append(self.token)
                self.next_token()
            print "INTEGERS", self.integer_list
        else :
            raise NameError("{ expected 2")

    def function(self):
        global FUNCTIONS
        global STACK

        self.next_token()
        if self.token == '{' :
            self.next_token()

            # Get name            
            name = self.token
            self.next_token()           
            
            if self.token == '}' :
                self.next_token()
                bracket = 0
                if self.token == '{' :                    
                    self.next_token()

                    # NEED TO HAVE NESTED COMMANDS
                    commands = []

                    while True :
                        #print '+++++', self.token
                        if self.token == '{' :
                            res = self.command()
                            #print "AAAA", res
                            #for c in res :
                            #    STACK.append(c)
                            #commands.append( res[0:] )
                            commands += res
                        else :
                            commands.append( self.token )
                            self.next_token()
                        if self.token == '}' :                            
                            break                    

                    #print "YO",commands
                    if self.token == '}':                        
                        FUNCTIONS[ name ] = commands
                        return
                    else:
                        raise NameError("} expected 4")                         
                else :
                    raise NameError("{ expected 3")
            else :
                raise NameError("} expected 2")
        else :
            raise NameError("{ expected 1") 

    def command( self, depth = 0 ) :
        cmd = []
        while True :
            #print "----", self.token

            if self.token == '{' :
                self.next_token()
                res = self.command(depth+1)
                cmd.append( res )
            elif self.token == '}' :
                if depth > 0 :
                    self.next_token()                
                return cmd
            else :
                cmd.append( self.token )
                self.next_token()                
                
    def string( self ) :
        s = ''        
        if self.token == '"' :
            s += '"'
            self.next_token()
            while self.token != '"' :
                s += self.token
                self.next_token()

            if self.token == '"' :
                s += self.token
                self.next_token()                
                return s

    def macro(self):
        global MACROS

        self.next_token()
        if self.token == '{' :
            self.next_token()

            # Get name
            #print "MACRO", self.token
            name = self.token
            self.next_token()           
            
            if self.token == '}' :
                self.next_token()
                bracket = 0
                if self.token == '{' :
                    bracket += 1
                    self.next_token()

                    val = []
                    while True:
                        if self.token == '}' :
                            bracket -= 1
                            if bracket == 0 :
                                break
                        if self.token == '{' :
                            bracket += 1
                        val.append(self.token)
                        self.next_token()

                    if self.token == '}' and bracket == 0:
                        MACROS[ name ] = ' '.join(val)                      
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
            f = self.token  
            Function( f, FUNCTIONS[ f ], self.external_entries ).execute()     

            self.eat_except('}') ###
        else :
            raise NameError("{ expected 2")

    def read(self):
        self.bib = bib.Bibparser(self.bib_data)
        self.bib.parse()
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
        global ENTRY
        self.next_token()
        if self.token == '{' :
            self.next_token()

            func = self.token            

            for entry in self.bib.records:
                ENTRY = self.bib.records[entry] 
                # Execute func for 
                # the specific entity
                if func == 'call.type$' :
                    #print "\t call.type$", entry
                    func = self.bib.records[entry]['record_type']                
                Function( func, FUNCTIONS[ func ], self.external_entries ).execute( self.bib.records[entry] )

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
            #print "STRINGS", integer_list
        else :
            raise NameError("{ expected 2")

def main() :    
    """Main function"""

    _bst_filename = sys.argv[1]
    _bib_filename = sys.argv[2]

    with open( _bst_filename, 'r' ) as f :
        bst_file_data = f.read()     

    with open( _bib_filename, 'r' ) as f :
        bib_file_data = f.read()     
    
    bst_file_data = clear_comments(bst_file_data) 
    bib_file_data = clear_comments(bib_file_data) 

    bst = Bstparser(bst_file_data, bib_file_data)
    bst.parse()

    print "------"
    print
    print STACK
    print BUFFER
    
if __name__ == "__main__" :
    main()