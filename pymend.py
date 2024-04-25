from enum import Enum
from random import randint



DIGITS = '0123456789'
ALPHABET_LOW = 'abcdefghijklmnopqrstuvwxyz'
ALPHABET_HIGH = ALPHABET_LOW.upper()
ALPHABET = ALPHABET_LOW + ALPHABET_HIGH
VALID_FOR_VARNAMES = ALPHABET + '_' + DIGITS


KEYWORDS = [
    'if',
    'then',
    'get',
    'repeat',
    'end',
    'log',
    'is',
    'less',
    'more',
    'not',
    'isnot',
    'immut',
    'mut',
    'set',
    'nil',
    'as',
    'func',
    'stop',
]



class ImmutDict:
    def __init__(self):
        self.val = {}
    
    def get(self, key, default=None):
        return self.val.get(key, default)

    def add(self, key, value):
        if key not in list(self.val): self.val[key] = value
    
    def remove(self, key):
        if key in list(self.val): self.val.pop(key)



class TT(Enum):
    STRING = 'STRING'
    INT = 'INT'
    FLOAT = 'FLOAT'
    BOOL = 'BOOL'
    KEYWORD = 'KEYWORD'
    IDENT = 'IDENT'
    ILLEGAL = 'ILLEGAL'
    #EQUALS = 'EQUALS'
    COMMENT = 'COMMENT'
    EOF = 'EOF'


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f'{self.type}: {self.value}'
        


class LineLexer:
    def __init__(self, line: str):
        self.text = line
        self.idx = -1
        self.c_char = None
        self.advance()
    
    def advance(self):
        self.idx += 1
        self.c_char = self.text[self.idx] if self.idx < len(self.text) else None

    def lex_to_tokens(self):
        tokens: list[Token] = []

        while self.c_char != None:
            if self.c_char in ' \t' or self.c_char == '\n': self.advance()
            elif self.c_char in DIGITS: tokens.append(self.make_number())
            elif self.c_char == '"': tokens.append(self.make_string())
            elif self.c_char in VALID_FOR_VARNAMES: tokens.append(self.make_ident())
            elif self.c_char == '-':
                self.advance()
                if self.c_char == '-': tokens.append(self.make_comment())
                else: tokens.append(Token(TT.ILLEGAL, self.c_char)); self.advance()
            else: tokens.append(Token(TT.ILLEGAL, self.c_char)); self.advance()

        return tokens

    
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.c_char != None and self.c_char in DIGITS + '.':
            if self.c_char == '.':
                if dot_count == 1: break
                dot_count += 1; num_str += '.'
            else: num_str += self.c_char
            self.advance()
        if dot_count == 0: return Token(TT.INT, int(num_str))
        return Token(TT.FLOAT, float(num_str))
        
    def make_string(self):
        string_str = ''
        self.advance()

        while self.c_char != None and self.c_char != '"':
            string_str += self.c_char
            self.advance()
        self.advance()
        return Token(TT.STRING, string_str)
    
    def make_ident(self):
        ident_str = ''

        while self.c_char != None and self.c_char in VALID_FOR_VARNAMES:
            ident_str += self.c_char
            self.advance()
        self.advance()
        if ident_str in KEYWORDS:
            return Token(TT.KEYWORD, ident_str)
        return Token(TT.IDENT, ident_str)

    def make_comment(self):
        comment_str = ''
        self.advance()
        if self.c_char == ' ': self.advance()
        
        while self.c_char != None and self.c_char != '\n':
            comment_str += self.c_char
            self.advance()
        self.advance()
        return Token(TT.COMMENT, comment_str)


def getstate(left: Token, op: Token, right: Token):
    match op.value:
        case 'is': return left.value == right.value
        case 'not' | 'isnot': return left.value != right.value
        case 'less': return left.value < right.value
        case 'more': return left.value > right.value
        case x: return

def log_error(details: str, line: int): print(f"error: {details} on line {line+1}")

def interpret(code: str | list[str] | tuple[str]):
    lines = code.split('\n') if isinstance(code, str) else list(code)
    
    #typed = None
    vars = {}
    consts = ImmutDict()
    ln = 0
    while ln < len(lines):
        toks_uncleaned = LineLexer(lines[ln]).lex_to_tokens()
        toks = [t for t in toks_uncleaned if t.type != TT.COMMENT]
        
        if len(toks) < 1: ln += 1; continue
        else:
            print(toks)
            for t in toks:
                if t.type == TT.ILLEGAL:
                    log_error(f"illegal char '{t.value}'", ln)
                    return

            if toks[0].type == TT.KEYWORD:
                if toks[0].value == 'stop': return
                elif toks[0].value == 'log':
                    if len(toks) >= 2:
                        if toks[1].type == TT.IDENT:
                            not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                            from_mutable = vars.get(toks[1].value, not_found_id)
                            if from_mutable == not_found_id:
                                from_immutable = consts.get(toks[1].value, not_found_id)
                                if from_immutable == not_found_id:
                                    log_error(f"could not log unknown var '{toks[1].value}'", ln)
                                else: print(from_immutable)
                            else: print(from_mutable)
                        else: print(toks[1].value)
                    else: print()
                elif toks[0].value == 'get':
                    if len(toks) >= 2:
                        if toks[1].type == TT.IDENT:
                            uinp = input('give input\n')
                            consts.add(toks[1].value, uinp)
                elif toks[0].value == 'if':
                    if toks[-1].type != TT.KEYWORD or toks[-1].value != 'then':
                        log_error("missing 'then' to close 'if'", ln)
                        return
                elif toks[0].value == 'mut':
                    if len(toks) == 2:
                        if toks[1].type == TT.IDENT: vars[toks[1].value] = None
                        else: log_error('malformed variable declaration', ln)
                    elif len(toks) > 2:
                        pass
                    else: log_error('malformed variable declaration', ln)


        ln += 1



with open('./test.mend', 'rt') as f: interpret(f.read())