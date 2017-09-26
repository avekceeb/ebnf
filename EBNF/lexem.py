
class LexemException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class Token:

    terminal, \
    name, \
    definition, \
    alternation, \
    optional, \
    grouping, \
    repetition, \
    end = range(1, 9)

    @staticmethod
    def nm(k):
        return {
            Token.terminal:'',
            Token.name:'ID:',
            Token.definition:'EQ:',
            Token.alternation:'',
            Token.optional:'OPT:',
            Token.grouping:'GRP:',
            Token.end:'END',
            Token.repetition:'REP:'}[k]
    
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return "%s%s" % (Token.nm(self.kind), self.value)

####################################################################

def tokenize_ebnf_grammar(string):
    if not string:
        return []
    l = len(string)
    if not l:
        return []

    tokens = []
    current_token_type = None
    current_token = ""
    i = -1
    
    while i < l-1:
        i = i + 1
        c = string[i]
        if "'" == c:
            # open terminal
            i0 = i + 1
            c = string[i0]
            while "'" != c:
                i += 1
                if i > l-1:
                    raise LexemException("Closing quote not found!")
                c = string[i]
            tokens.append(Token(Token.terminal, string[i0:i]))
            current_token_type = None
            current_token = ''
            continue
        if '"' == c:
            # open terminal
            i0 = i + 1
            c = string[i0]
            while '"' != c:
                i += 1
                if i > l-1:
                    raise LexemException("Closing quote not found!")
                c = string[i]
            tokens.append(Token(Token.terminal, string[i0:i]))
            current_token_type = None
            current_token = ''
            continue
        if c in '\n\t':
            # todo : more ws stuff
            continue
        elif (' ' == c) and (not current_token.strip()):
                continue
        elif c in ',;|=':
            # if there is token waiting - push it
            if (current_token):
                # todo : check alphanum
                if (current_token_type == None):
                    current_token_type = Token.name
                    current_token = current_token.strip()
                tokens.append(Token(current_token_type, current_token))
                current_token_type = None
                current_token = ''
            if ';' == c:
                tokens.append(Token(Token.end, ';'))
            if '|' == c:
                tokens.append(Token(Token.alternation, '|'))
            if '=' == c:
                tokens.append(Token(Token.definition, '='))
            # if ',' - default action - concatenation
            current_token = ''
            continue
        elif '[' == c:
            # open optional lexem
            #i0 = i + 1
            #"""
            toks, k = tokenize_nested(string[i+1:], '[', ']', Token.optional)
            tokens.append(toks)
            i += k
            current_token_type = None
            current_token = ''
            continue
        elif '{' == c:
            # open repetition lexem
            toks, k = tokenize_nested(string[i+1:], '{', '}', Token.repetition)
            tokens.append(toks)
            i += k
            current_token_type = None
            current_token = ''
            continue
        elif '(' == c:
            # open group
            toks, k = tokenize_nested(string[i+1:], '(', ')', Token.grouping)
            tokens.append(toks)
            i += k
            current_token_type = None
            current_token = ''
            continue
        else:
            current_token += c

    if current_token:
        tokens.append(Token(Token.name, current_token.strip()))

    return tokens

def tokenize_nested(string, openning, closing, token_kind):
    nested = 1
    i = 0
    l = len(string)
    for j in string:
        i += 1
        if openning == j:
            nested += 1
            continue
        if closing == j:
            nested -= 1
            if nested < 0:
                raise LexemException("] without [")
            if nested == 0:
                break
            else:
                continue
    if nested != 0:
        raise LexemException("Closing not found")
    return Token(token_kind, tokenize_ebnf_grammar(string[:i-1])), i


####################################################################

def tokens_to_rules(tokens):
    tok_len = len(tokens)
    _rules = {}
    t = 0
    while t < tok_len-1:
        rule, eq = tokens[t:t+2]
        if (rule.kind == Token.name) and (eq.kind == Token.definition):
            if t == 0:
                rule.value = "*" # force first rule to has redefined name
            t += 2
            rule_tokens = []
            n = t
            while t < tok_len:
                if tokens[t].kind == Token.end:
                    _rules[rule.value] = tokens[n:t]
                    break
                t += 1
        else:
            t += 1
    return _rules

####################################################################
