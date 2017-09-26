from sys import exit
from lexem import *
from syntax import *

"""

# todo:

- recursive rules ??? we probably need one more round after building parse tree
- greedy parsing ???
- visualisation: if name or value is not alnum => present as "\n" or ord(ch)
- gtk grammar probe

"""

class ParserException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class Parser:

    def __init__(self, grammar):
        self.rules = {}
        self.plugs = {}
        self.tree = None
        self.started_rules = [] # recursion catcher
        self.rule_table = {}
        self.grammar = grammar
        if self.grammar:
            tokens = tokenize_ebnf_grammar(self.grammar)
            self.rules = tokens_to_rules(tokens)

    def get_tree(self):
        if not self.tree:
            self.tree = self.rule_to_tree('*')
        return self.tree

    def add_rule(self, name, rule):
        self.plugs[name] = rule

    def parse(self, string):
        #print self.rules
        return self.get_tree().parse(string)

    def rule_to_tree(self, rule_name):
        if rule_name in self.rules:
            return self.parse_syntax(self.rules[rule_name], name = rule_name)
        elif rule_name in self.plugs:
            return Leaf(value = self.plugs[rule_name], tag = rule_name)
        else:
            raise ParserException("Rule %s not found!")

    def token_to_node(self, token):
        
        if Token.terminal == token.kind:
            return Leaf(value = token.value)
        
        elif Token.name == token.kind:
            # identifier - this could be a start of an endless recursion
            return self.rule_to_tree(token.value)

        elif Token.alternation == token.kind:
            return OrTree()

        elif Token.optional == token.kind:
            return OrTree(left = '', right = self.parse_syntax(token.value))

        elif Token.repetition == token.kind:
            return RepeatTree(right = self.parse_syntax(token.value))

        elif Token.grouping == token.kind:
            return  self.parse_syntax(token.value)

        else:
            raise ParserException("Unknown type of token")

    def parse_syntax(self, _tokens, name = ''):

        # work on copy, since it would be modified
        tokens = list(_tokens)

        if '*' == name:
            name = ''
            # also we suppose starting rule could not be included in other rules

        if name:
            if name in self.started_rules:
                raise ParserException("Rule Recursion in %s!!!" % (name))
                # todo: this leaf needs to be set to 'name' node further...
                return Loop(name)
            else:
                self.started_rules.append(name)

        head_token = None
        head = None
        node = None
        
        # todo: case OPT:[ID:id] ; id = "term" ;
        # id name should be translated further to OPT
        # [] --> (("")|(term)) --> (""id:|(term))

        # also todo: avoid empty string matches with tag saved: {id:""}
        
        while len(tokens):
            #print traverse_tree(head)
            token = tokens.pop(0)
            # 0) initial state:
            if not head:
                head = self.token_to_node(token)
                head_token = token
                continue
            # 1) head is terminal
            if not isinstance(head, AndTree):
                node = self.token_to_node(token)
                if not isinstance(node, AndTree):
                    # concat 2 terminals
                    head = AndTree(left = head, right = node)
                    head_token = token
                    continue
                else:
                    # new node is non-terminal
                    # todo: case of rule = "a",["b"] ;
                    # (a|b) <-- wrong !!!
                    # should be (a & (""|"a"))
                    if None == node.L:
                        node.L = head
                    else:
                        node = AndTree(left = head, right = node)
                    head = node
                    head_token = token
                    continue
            # 2) head is Node, (node not None ???)
            else:
                node = self.token_to_node(token)
                if (None == head.R):
                    # right branch is empty
                    head.R = node
                    continue
                else:
                    # right branch is full
                    if not isinstance(node, AndTree):
                        # concat new terminal with right
                        # right could not be a node now ??
                        if head_token.kind in [Token.grouping,
                                               Token.optional,
                                               Token.repetition]:
                            # todo: case of ('a'|'b')&'c':
                            #       while reading ,c: c is a term
                            #       and head is a Tree
                            #       a|(b&c) <-- wrong
                            #  head is grouped !!!
                            head = AndTree(left = head, right = node)
                            head_token = token
                        else:
                            head.R = AndTree(left = head.R, right = node)
                        continue
                    else:
                        # token is non-terminal =>
                        # create new node as head and glue old one as its left branch
                        if (None != node.R) and (None != node.L):
                            # f.e. full node read via identifier
                            head = AndTree(left = head, right = node)
                            head_token = token
                            continue
                        else:
                            # new 'operator' token read
                            # todo: only left
                            oldnode = head
                            head = node
                            head_token = token
                            head.L = oldnode
        if name:
            if isinstance(head, AndTree) or isinstance(head, Leaf):
                head.tag = name
            else:
                head = Leaf(head, tag = name)
            self.started_rules.remove(name)
            self.rule_table[name] = head
        return head

# ---- reusable rules ----
#isdigit
#isalnum
# def r_hexadecimal

def r_letter(string):
    if not(string and len(string) > 0):
        return None, string, False
    if string[:1].isalpha():
        return string[:1], string[1:], True
    else:
        return None, string, False

def r_letters(string):
    if not(string and len(string) > 0):
        return None, string, False
    i = 0
    l = len(string)
    found = True
    while i < l and string[:i+1].isalpha():
        i += 1
    if i > 0:
        return string[:i], string[i:], True
    else:
        return None, string, False

class ParserEx(Parser):
    def __init__(self, grammar):
        Parser.__init__(self, grammar)
        self.add_rule('letter', r_letter)
        self.add_rule('letters', r_letters)

#-------------------------------------
import random
def generate_random(tree):
    if not tree:
        return ''
    repeat_max = 5
    s = ''
    if isinstance(tree, RepeatTree):
        for i in range(random.randint(0,repeat_max)):
            s += generate_random(tree.R)
        return s
    elif isinstance(tree, OrTree):
        if random.randint(0,100) % 2 == 0:
            return generate_random(tree.R)
        else:
            return generate_random(tree.L)
    elif isinstance(tree, AndTree):
        s += generate_random(tree.L)
        s += generate_random(tree.R)
        return s
    elif isinstance(tree, Leaf):
        if isinstance(tree.value, str):
            return tree.value
        else:
            # todo functions to generate
            raise ParserException("Could not generate from non string!")
    else:
        raise ParserException("Wrong tree type!")

