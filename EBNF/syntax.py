

"""
this is an artificial type of node
during parsing grammar if we met a recursion
we don't have a node to refer to yet (it is to be built later on)
so this is to create a 'future connection'
"""
class Loop():
    def __init__(self, loop):
        self.loop = loop

class Leaf():

    def __init__(self, value='', tag = None):
        self.value = value
        self.tag = tag

    def parse(self, string):
        
        # plugable or predefined/reusable rules
        if callable(self.value):
            # todo: ugly....
            p, r, i = self.value(string)
            if i:
                return {'tag': self.tag, 'val': p}, r, i
            else:
                return None, string, False
                
        l = len(self.value)
        # empty or None always match
        if not l:
            return "", string, True
        if l > len(string):
            return None, string, False
        if self.value == string[:l]:
            return self.wrap_into_node(), string[l:], True
        else:
            return None, string, False

    def __str__(self):
        if self.tag:
            return "{%s:%s}" % (self.tag, self.value)
        else:
            return self.value
        
    def __repr__(self):
        return self.__str__()

    def wrap_into_node(self):
        return {'tag': self.tag, 'val': self.value}

# todo: Leaf::value not used in ancestors
class AndTree(Leaf):
    
    def __init__(self, left = None, right = None, tag = None):
        Leaf.__init__(self, tag = tag)
        if isinstance(left, str):
            self.L = Leaf(value = left)
        else:
            self.L = left
        if isinstance(right, str):
            self.R = Leaf(value = right)
        else:
            self.R = right

    def parse(self, string):
        node =  {'tag':self.tag, 'child':[]}
        parsed, remainder, matched = self.L.parse(string)
        if not matched:
            return None, string, False
        more_parsed, remainder, matched = self.R.parse(remainder)
        if not matched:
            return None, string, False
        node['child'] = [parsed, more_parsed]
        return node, remainder, True

    def __str__(self):
        if self.tag:
            return "%s:&&" % (self.tag)
        else:
            return '&&'
        
# | - node
class OrTree(AndTree):
    
    def __init__(self, left = None, right = None, tag = None):
        AndTree.__init__(self, left = left, right = right, tag = tag)
        
    def parse(self, string):
        node =  {'tag':self.tag, 'child':[]}
        # beginning from right branch
        parsed, remainder, matched = self.R.parse(string)
        if matched:
            node['child'] = [parsed]
            return node, remainder, True
        parsed, remainder, matched = self.L.parse(string)
        if matched:
            node['child'] = [parsed]
            return node, remainder, True
        else:
            return None, string, False
      
    def __str__(self):
        if self.tag:
            return "%s:||" % (self.tag)
        else:
            return '||'

# { }
class RepeatTree(AndTree):
    
    def __init__(self, left = '', right = None, tag = None):
        AndTree.__init__(self, left = '', right = right, tag = None)
        
    def __str__(self):
        return '??'

    def parse(self, string):
        node =  {'tag':self.tag, 'child':[]}
        found = []
        matched = True
        remainder = string
        # find longest match
        while matched and remainder:
            parsed, remainder, matched = self.R.parse(remainder)
            found.append(parsed)
        if found: # we have previous match
            node['child'] = found
            return node, remainder, True
        else:
            return None, string, True

####################################################################

def traverse_tree(tree):
    if not tree:
        return '(Null)'
    else:
        s = '('
        if isinstance(tree, AndTree):
            s += traverse_tree(tree.L) 
        s += str(tree)
        if isinstance(tree, AndTree):
            s += traverse_tree(tree.R)
        s += ')'
        return s
