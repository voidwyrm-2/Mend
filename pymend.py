from enum import Enum
from random import randint
from typing import Any



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
    'else',
    'log',
    'is',
    'and',
    'or',
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
    'return',
    'stop',
]



class ImmutDict:
    def __init__(self):
        self.__val = {}
    
    def get(self, key, default=None):
        return self.__val.get(key, default)

    def add(self, key, value):
        if key not in list(self.__val): self.__val[key] = value
    
    def remove(self, key):
        if key in list(self.__val): self.__val.pop(key)
    
    def keys(self): return self.__val.keys()

    def values(self): return self.__val.values()

    #def extend(self, ):
    
    def __str__(self): return str(self.__val)



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
    COMMA = 'COMMA'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
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
            elif self.c_char == ',': tokens.append(Token(TT.COMMA)); self.advance()
            elif self.c_char == '(': tokens.append(Token(TT.LPAREN)); self.advance()
            elif self.c_char == ')': tokens.append(Token(TT.RPAREN)); self.advance()
            elif self.c_char == '[': tokens.append(Token(TT.LBRACKET)); self.advance()
            elif self.c_char == ']': tokens.append(Token(TT.RBRACKET)); self.advance()
            elif self.c_char == '{': tokens.append(Token(TT.LBRACE)); self.advance()
            elif self.c_char == '}': tokens.append(Token(TT.RBRACE)); self.advance()
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
        #self.advance()
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



class AnyToken:
    def __str__(self): return 'AnyToken'

def istoken(tok: Token, type: Any | tuple[Any] = AnyToken, value: Any | tuple[Any] = AnyToken):
    ofvalue = lambda v, check: v in check if isinstance(check, (tuple, list)) else v == check
    #print(f'{tok}, {type}, {value}, {tok.type == type}, {tok.value == value}')
    if type == AnyToken and value == AnyToken: return isinstance(tok, Token)
    if type == AnyToken: return ofvalue(tok.value, value)
    if value == AnyToken: return ofvalue(tok.type, type)
    return ofvalue(tok.type, type) and ofvalue(tok.value, value)

def hastoken(tokens: list[Token], type: Any | tuple[Any] = AnyToken, value: Any | tuple[Any] = AnyToken):
    for t in tokens:
        if istoken(t, type, value): return True
    return False



def getstate(left: Token, op: Token, right: Token, line: int):
    try:
        match op.value:
            case 'is': return left.value == right.value
            case 'not' | 'isnot': return left.value != right.value
            case 'less': return left.value < right.value
            case 'more': return left.value > right.value
            case 'plus': return left.value + right.value
            case 'minus': return left.value - right.value
            case 'mult': return left.value * right.value
            case 'div': return left.value / right.value
            case 'fdiv': return left.value // right.value
            case x: return None
    except ValueError as e: log_error(e, line); return None


def log_error(details: str, line: int): print(f"error: {details} on line {line+1}")


class listgetter_fail: pass

def get_list(toks: list[Token], line, starting_idx: int = 4, return_as_failure = listgetter_fail, call_raf: bool = True):
    c_tok = starting_idx
    acc = []
    looking_for_comma = False
    while not istoken(toks[c_tok], TT.RBRACKET):
        if looking_for_comma:
            if not istoken(toks[c_tok], TT.COMMA): log_error('malformed variable declaration(missing comma)', line); return return_as_failure() if call_raf else return_as_failure
            c_tok += 1
            looking_for_comma = False
        else:
            if istoken(toks[c_tok], (TT.FLOAT, TT.INT, TT.STRING, TT.BOOL)): acc.append(toks[c_tok].value); looking_for_comma = True; c_tok += 1
            elif istoken(toks[c_tok], TT.LBRACKET):
                ngotten = get_list(toks, line, c_tok+1, return_as_failure, call_raf)
                if call_raf:
                    if isinstance(ngotten, return_as_failure): return ngotten
                else:
                    if ngotten == return_as_failure: return ngotten
                acc.append(ngotten)
                looking_for_comma = True
                c_tok += 1
            else: log_error(f"malformed variable declaration(invalid type '{toks[c_tok].type}')", line); return return_as_failure() if call_raf else return_as_failure
    return acc


class Null:
    def __str__(self): return 'null'

def interpret(token_lines: list[list[Token]], isfunc: bool = False, isimported: bool = False):
    # flags
    jump_to_next_end = False

    vars = {}
    consts = ImmutDict()
    funcs: dict[str, tuple[tuple[tuple[tuple[str, bool]], list[Token]]]] = {
        'AHH': (
            (),
            ([Token(TT.KEYWORD, 'log'), Token(TT.STRING, 'AHHHHHHHHHHHHHHHHHHHHHHH')],)
        )
    }

    caches = {
        'funcs': []
    }

    #if isfunc: print(token_lines)

    ln = 0
    while ln < len(token_lines):
        toks = token_lines[ln]
        
        if len(toks) < 1: ln += 1; continue
        else:
            #print(toks)
            if jump_to_next_end:
                if istoken(toks[0], TT.KEYWORD, 'end'): jump_to_next_end = False
                ln += 1
                continue
            for t in toks:
                if istoken(t, TT.ILLEGAL):
                    log_error(f"illegal char '{t.value}'", ln)
                    return

            if istoken(toks[0], TT.KEYWORD):
                if istoken(toks[0], value='stop'): return

                elif istoken(toks[0], value='log'):
                    if len(toks) >= 2:
                        if istoken(toks[1], TT.IDENT):
                            not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                            from_mutable = vars.get(toks[1].value, not_found_id)
                            if from_mutable == not_found_id:
                                from_immutable = consts.get(toks[1].value, not_found_id)
                                if from_immutable == not_found_id:
                                    log_error(f"could not log unknown variable '{toks[1].value}'", ln)
                                else: print(from_immutable)
                            else: print(from_mutable)
                        else: print(toks[1].value)
                    else: print()
                
                elif istoken(toks[0], value='get'):
                    if len(toks) >= 2:
                        if istoken(toks[1], TT.IDENT):
                            uinp = input('give input\n')
                            vars[toks[1].value] = uinp
                
                elif istoken(toks[0], value='if'):
                    if not istoken(toks[-1], TT.KEYWORD, 'then'):
                        log_error("missing 'then' to close 'if'", ln)
                        return
                
                elif istoken(toks[0], value='mut'):
                    if len(toks) == 2:
                        if istoken(toks[1], TT.IDENT):
                            if istoken(toks[1], value=tuple(vars.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return
                            vars[toks[1].value] = Null()
                        else: log_error('malformed variable declaration(missing variable name)', ln); return
                    elif len(toks) >= 4:
                        if istoken(toks[1], TT.IDENT) and istoken(toks[2], TT.KEYWORD, 'as'):
                            if istoken(toks[1], value=tuple(vars.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return
                            if istoken(toks[3], (TT.FLOAT, TT.INT, TT.STRING, TT.BOOL)): vars[toks[1].value] = toks[3].value
                            elif istoken(toks[3], TT.KEYWORD):
                                if istoken(toks[3], value='get'): vars[toks[1].value] = input('give input\n')
                                else:
                                    log_error(f"malformed variable declaration(invalid keyword '{toks[3].value}')", ln); return
                            elif istoken(toks[3], TT.IDENT):
                                not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                                from_mutable = vars.get(toks[1].value, not_found_id)
                                if from_mutable == not_found_id:
                                    from_immutable = consts.get(toks[1].value, not_found_id)
                                    if from_immutable == not_found_id:
                                        log_error(f"malformed variable declaration(unknown variable '{toks[1].value}')", ln); return
                                    else: vars[toks[1].value] = from_immutable
                                else: vars[toks[1].value] = from_mutable
                            elif istoken(toks[3], TT.LBRACKET):
                                ls = get_list(toks, ln)
                                if isinstance(ls, listgetter_fail): return
                                vars[toks[1].value] = ls
                            else: log_error(f"malformed variable declaration(invalid value '{toks[3].value}')", ln); return
                        else: log_error(f"malformed variable declaration(missing variable name and 'as' keyword)", ln); return
                    else: log_error('malformed variable declaration(missing variable name)', ln); return
                
                elif istoken(toks[0], value='immut'):
                    if len(toks) == 2:
                        if istoken(toks[1], TT.IDENT):
                            if istoken(toks[1], value=tuple(consts.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return
                            consts.add(toks[1].value, Null())
                        else: log_error('malformed variable declaration(missing variable name)', ln); return
                    elif len(toks) >= 4:
                        if istoken(toks[1], TT.IDENT) and istoken(toks[2], TT.KEYWORD, 'as'):
                            if istoken(toks[1], value=tuple(consts.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return
                            if istoken(toks[3], (TT.FLOAT, TT.INT, TT.STRING, TT.BOOL)): consts.add(toks[1].value, toks[3].value)
                            elif istoken(toks[3], TT.KEYWORD):
                                consts.add(toks[1].value,input('give input\n'))
                            elif istoken(toks[3], TT.IDENT):
                                not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                                from_mutable = consts.get(toks[1].value, not_found_id)
                                if from_mutable == not_found_id:
                                    from_immutable = consts.get(toks[1].value, not_found_id)
                                    if from_immutable == not_found_id:
                                        log_error(f"malformed variable declaration(unknown variable '{toks[1].value}')", ln); return
                                    else: consts.add(toks[1].value, from_immutable)
                                else: consts.add(toks[1].value, from_mutable)
                            elif istoken(toks[3], TT.LBRACKET):
                                ls = get_list(toks, ln)
                                if isinstance(ls, listgetter_fail): return
                                consts.add(toks[1].value, ls)
                            else: log_error(f"malformed variable declaration(invalid value '{toks[3].value}')", ln); return
                        else: log_error(f"malformed variable declaration(missing variable name and 'as' keyword)", ln); return
                    else: log_error('malformed variable declaration(missing variable name)', ln); return
                
                elif istoken(toks[0], value='set'): pass

                elif istoken(toks[0], value='return'):
                    if isfunc: pass
                    else: pass

            elif istoken(toks[0], TT.IDENT):
                if istoken(toks[0], value=tuple(funcs)):
                    if len(toks) >= 3:
                        if istoken(toks[1], TT.LPAREN) and istoken(toks[-1], TT.RPAREN):
                            returned = interpret(funcs[toks[0].value][1], True)
                            if returned != None: pass
                        else: log_error("malformed function call(missing parentheses)", ln); return
                    elif len(toks) != 1: log_error("malformed function call(mismatched parentheses)", ln); return
                elif istoken(toks[0], value=tuple(vars)) or istoken(toks[0], value=tuple(consts.keys())): pass
                else: log_error(f"unknown value '{toks[0].value}'", ln); return


        #print('vars', vars)
        #print('consts', consts)
        
        ln += 1
    if isimported: return vars, consts, funcs



def run(code: str | list[str] | tuple[str]):
    lines = code.split('\n') if isinstance(code, str) else list(code)

    token_lines = [[t for t in LineLexer(l).lex_to_tokens() if t.type != TT.COMMENT] for l in lines]

    interpret(token_lines)


with open('./test.mend', 'rt') as f: run(f.read())