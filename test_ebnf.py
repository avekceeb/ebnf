
from EBNF import *
from json import dumps
import EBNF.visual
import random

#import sys
#sys.setrecursionlimit(100000)

def check_match(parser, string):
    parsed, remainder, matched = parser.parse(string)
    print "--> " + string
    print "<-- " + str(parsed)
    assert(matched)
    assert(remainder == '')

def check_not_match(parser, string):
    parsed, remainder, matched = parser.parse(string)
    print "~~> " + string
    assert(not matched)

def check_grammar(grammar, positive = None, negative = None):
    print "-----------------------------------"
    print grammar
    parser = Parser(grammar)
    tree = parser.get_tree()
    assert(tree != None)
    svg = str(random.randint(1000, 9999)) + ".svg"
    EBNF.visual.draw_graph(tree, svg)
    print "tree saved in " + svg
    print "-----------------------------------"
    print

    #### auto-generated random data ####
    for string in [generate_random(tree) for _ in range(100)]:
        check_match(parser, string)
        
    ### provided positive data ###
    if positive:
        if not isinstance(positive, list):
            positive = [positive]
        for string in positive:
            check_match(parser, string)

    ### provided negative data ###
    if negative:
        if not isinstance(negative, list):
            negative = [negative]
        for string in negative:
            check_not_match(parser, string)
    
from EBNF.syntax import *
def test_syntax_trees():
    a = OrTree(left = 'aa', right = 'ba')
    b = RepeatTree(right = a)
    p,r,i = b.parse('aabababacaaaaba')
    assert (i)
    #print b.parse('aabababacaaaaba')

    number = OrTree(left = '0', right = '1')
    letter = OrTree(left = 'a', right = 'b')
    sign = OrTree(left = '@', right = '#')
    var = OrTree(left = letter, right = sign)
    rule = OrTree(left = number, right = var)
    for s in ['@','#','a', 'b','0', '1']:
         p,r,i = rule.parse(s)
         assert(i)

    
def test_smoke():
    check_grammar("""
    rule = number, [sign | letter], number ;
    number = "0" | "1" ;
    letter = "a" | "b" ;
    sign = "@" | "#" ;""",
        positive = ['0#0','0a0','0#1','1b0','00','10'])

    check_grammar("""
    rule = number, [sign | letter], number, [letter] ;
    number = "0" | "1" ;
    letter = "a" | "b" ;
    sign = "@" | "#" ;""",
        positive = ['0#0b','0a0'])

    check_grammar("""
    rule = number, { letter}, number ;
    number = "0" | "1" ;
    letter = "a" | "b" ;""",
                  positive = ['1bbababab0', '1a0', '10'])

    check_grammar("""
    rule = number, number, (letter | sign) , number ;
    number = "0" | "1" ;
    letter = "a" | "b" ;
    sign = "@" | "#" ;""",
                  positive = ['10@0'])

    check_grammar("""
    rule = number | var ;
    var = letter | sign ;
    number = "0" | "1" ;
    letter = "a" | "b" ;
    sign = "@" | "#" ;""",
                  positive = ['0', 'b', '@', '#'])

    check_grammar("""
    rule = number, [sign] ;
    number = "0" | "1" ;
    sign = "@" ;""",
                  positive = ['0@', '0', '1', '1@'])

    check_grammar("""
    rule = number ;
    number = "0" | "1" ;""",
                  positive = ['0', '1'])

    check_grammar("""
    rule = sign, cipher ;
    sign = "-" ;
    cipher = "1" ;""",
                  positive = ['-1'])
    
    check_grammar('rule=XXX; XXX="xxx";', positive = ['xxx'])

    check_grammar('rule="ZZZZ";', positive = ['ZZZZ'])

    check_grammar('rule = ["#"];', positive = '#')

    check_grammar("""rule = "0", ["@"] ;""",
                  positive = ['0', '0@'])
    check_grammar("""
    rule = {line};
    line = test , { maybe condition }, "\n";
    test = "TEST";
    space = " ", {" "};
    maybe condition = space, condition ;
    condition = "COND" ;""",
    positive = ['TEST\n', 'TEST\nTEST\n', 'TEST COND\n', 'TEST     COND COND\nTEST\n'])

    check_grammar('rule = {hello}, "world" ; hello = "hello" ;', negative = ['hello'])

    check_grammar("""
    rule = hello, " ", world ; 
    world = ("W" | "w") , "orld" ;
    hello = "hell", ( "o" | "O" ) ;""",
                  positive = ['hello World', 'hellO world'])

    check_grammar('rule = [hello], "world" ; hello = "hello" ;',
                  positive = ['helloworld', 'world'])

    check_grammar('rule = {hello}, "world" ; hello = "hello" ;',
                  positive = ['world', 'helloworld', 'hellohelloworld', 'hellohellohelloworld'])

    check_grammar('''
    rule A = "=={t|e|r|m|i|n|a|l}==", ( some name X | some other name Y );
    some name X = "X" ; some other name Y = "Y";''',
                  positive = "=={t|e|r|m|i|n|a|l}==X");


def test_regressions():
    g = """
    rule = {line};
    line = prefix , body, suffix, "_" ;
    prefix = "a" | "b" ;
    body = "@" | "#" ;
    suffix = "8" | "3" ;
    """
    check_grammar(g)

    g = """rule = { "@" , [ ( "a" | "A" ), ("b" | "B") ] } ;"""
    check_grammar(g, ['@', '@@', '@ab', '@ab@ab', '@@ab@aB@AB@@@@'])
    check_grammar(g)
    
def test_nested():
    g = """rule = "@" , [ "a", [ "b" ] ] , "#"; """
    check_grammar(g, positive= ['@#', '@a#', '@ab#'])

    g = """rule = "@" , { "a", { "b" } } ; """
    check_grammar(g, positive = ['@', '@aaaaa', '@abababab'])
  
    g = """rule = "@", ( "a" , ( "b" | ("B" | "8") ) ) ; """
    check_grammar(g, positive = ['@ab', '@aB', '@a8'])

    check_grammar("""rule = ((( '@' ))) ; """, positive = '@')

from EBNF.syntax import *
def test_recursion():

    """
    start = expression ;
    expression = term | term, '+', expression ;
    term = "1" ;

in case of (|) ('or' node)
begins parsing from right branch:

    (expression:|) <--.
      /   \           |
     /     \          |
   (1)     (,)        |
           / \        |
          /   \       ^
        (1)   (,)     |
              / \     |
            (+)  \____|

    
    below is an endless loop:
    beacause (,) starts parsing from left branch

    start = expression ;
    expression = term | expression, +, term;
    term = "1" ;

    (expression:|)
      /   \
     /     \
   (1)     (,)
 ^         / \
 |        /   \        
 |_______/    (,)      
              / \      
            (+) (1)    

    """

    expr = OrTree(left = '1')
    subsubexpr = AndTree(left = '+', right = expr)
    subexpr = AndTree(left = '1', right = subsubexpr)
    expr.R = subexpr;
    print expr.parse('1+1')
    print expr.parse('1+1+1')
    print expr.parse('1+1+1+1')


    """
    rhs = name | "[", rhs, "]" ;
    name = "X" ;

     ,--->(rhs:|)
    |      /  \
    |     /    \
    |   (X)    (,)
    |          / \
    ^         /   \
    |       ([)   (,)
    |             / \
    |            /   \
    |__________ /    (]) 



    X
    [X]
    [[X]]

    """

    rhs = OrTree(left = 'X')
    subsubexpr = AndTree(left = rhs, right = ']')
    subexpr = AndTree(left = '[', right = subsubexpr)
    rhs.R = subexpr;
    print rhs.parse('X')
    print rhs.parse('[X]')
    print rhs.parse('[[X]]')
    print rhs.parse('[[[[X]]]]')
    
def open_bugs():
    x_recursive = """
    start = expression ;
    expression = term | term, '+', expression ;
    term = "1" ;
    """
    # VVVVVVVVV
    x_nonrecursive = """
    start = expression ;
    expression = term , { '+', term } ;
    term = "1" ;
    """
    check_grammar(x_nonrecursive, ['1', '1+1', '1+1+1'])
    try:
        check_grammar(x_recursive, '1+1')
    except ParserException:
        pass

    ebnf = """
    start = expression ;
    expression = term | term, '+', expression ;
    term = "1" ;
    """
    check_grammar(ebnf, ['1', '1+1', '1+1+1'])

def test_parserex():
    g = """
    rule = {line};
    line = test , { maybe condition }, "\n";
    test = "TEST";
    space = " ", {" "};
    maybe condition = space, condition ;
    condition = letters ;"""
    s = 'TEST hello there\n'
    parser = ParserEx(g)
    t, r, v = parser.parse(s)
    #print dumps(t, indent=4)
    assert(v)

def main():
    test_syntax_trees()
    test_smoke()
    test_regressions()
    test_nested()
    test_recursion()
    #open_bugs()

if __name__ == '__main__':
    main()
