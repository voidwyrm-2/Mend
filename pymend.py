from enum import Enum
from random import randint
from typing import Any
from pathlib import Path



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
    'isnot',
    'immut',
    'mut',
    'set',
    'nil',
    'as',
    'func',
    'return',
    'import',
    'stop',
    'container',
    'del',
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

    def extend(self, exentsion: dict):
        for e in list(exentsion.keys()):
            if e not in list(self.__val.keys()): self.__val[e] = exentsion[e]
    
    def __str__(self): return str(self.__val)

    def __repr__(self): return str(self.__val)


def extend_dict(orig: dict, exentsion: dict, overwrite_existing: bool = False):
    for e in list(exentsion):
        if overwrite_existing: orig[e] = exentsion[e]
        else:
            if e not in list(orig): orig[e] = exentsion[e]
    return orig



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
    DEBUG = 'DEBUG'
    STOP = 'STOP'
    PERIOD = 'PERIOD'
    STATELABEL = 'STATELABEL'
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
            elif self.c_char == '-': tokens.append(self.make_comment('-'))
            elif self.c_char == '/': tokens.append(self.make_comment('/'))
            elif self.c_char == '#': tokens.append(self.make_comment())
            elif self.c_char == ';': tokens.append(self.make_comment())
            elif self.c_char == '@': tokens.append(self.make_statelabel())
            elif self.c_char == '?':
                if self.idx == len(self.text)-1: tokens.append(Token(TT.DEBUG)); self.advance()
                else: tokens.append(Token(TT.ILLEGAL, (self.c_char, "question mark must be at end of line"))); self.advance()
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
    
    def make_statelabel(self):
        statelabel_str = ''

        self.advance()
        if self.c_char not in VALID_FOR_VARNAMES: return Token(TT.ILLEGAL, (self.c_char, "expected label name after '@'"))

        while self.c_char != None and self.c_char in VALID_FOR_VARNAMES:
            statelabel_str += self.c_char
            self.advance()
        return Token(TT.STATELABEL, statelabel_str)

    def make_comment(self, next_char_needed: str = ''):
        comment_str = ''
        if next_char_needed != '':
            self.advance()
            if self.c_char != next_char_needed:
                return Token(TT.ILLEGAL, (self.c_char, f"expected '{next_char_needed}' but found '{self.c_char}' instead"))
        self.advance()
        if self.c_char == ' ': self.advance()
        
        while self.c_char != None and self.c_char != '\n':
            comment_str += self.c_char
            self.advance()
        self.advance()
        return Token(TT.COMMENT, comment_str)


class MendFuncArg:
    def __init__(self, name: str, required: bool = True) -> None:
        self.__name = name
        self.__required = required

    def getname(self) -> str: return self.__name

    def isrequired(self) -> bool: return self.__required

    def copy(self): return MendFuncArg(self.__name, self.__required)

    def __repr__(self) -> str: return self.__name if self.__required else {self.__name} + "(op)"

class MendFunction:
    def __init__(self, name: str, args: list[MendFuncArg], content: list[list[Token]], is_bulitin: bool = False):
        self.__name = name
        self.__args = args
        self.__content = content
        self.__builtin = is_bulitin
    
    def run(self, root_folder: str = '', arguments: list[list[Any, MendFuncArg]] = []) -> tuple[dict[str, Any], ImmutDict, dict[str, Any]]: return interpret(token_lines=self.__content, isfunc=True, funcargs=arguments, root_folder=root_folder)

    def get_content(self) -> list[list[Token]]: return self.__content

    def get_args(self) -> list[MendFuncArg]: return self.__args

    def hasargs(self) -> bool: return len(self.__args) > 0

    def isempty(self) -> bool: return len(self.__content) == 0

    def isbuiltin(self) -> bool: return self.__builtin

    def get_name(self) -> str: return self.__name

    def hasname(self) -> bool: return self.__name.strip() != ''
    
    def rename(self, new_name: str) -> str: self.__name = new_name

    def copy(self, use_self_name: bool = True, name_to_use_instead: str = ""): return MendFunction(self.__name, self.__args, self.__content, self.__builtin) if use_self_name else MendFunction(name_to_use_instead, self.__args, self.__content, self.__builtin)

    def __repr__(self) -> str:
        str_args = ', '.join([str(a) for a in self.__args])
        out = f"function {self.__name}({str_args})" + "{" + f"{str(self.__content).removeprefix('[').removesuffix(']')}" + "}"
        if self.__builtin: out = 'builtin ' + out
        return out


class NotNeeded: pass
class MendContainer:
    def __init__(self, vars: dict[str, Any], consts: ImmutDict, funcs: dict[str, MendFunction], containers: dict[str, Any]):
        self.__vars = vars
        self.__consts = consts
        self.__funcs = funcs
        self.__containers: dict[str, MendContainer] = containers
    
    def access(self, path: list[str], value: Any = NotNeeded) -> tuple[Any, bool]:
        cpath = path.pop(0)
        if cpath in list(self.__containers):
            if not isinstance(value, MendContainer): log_error(f"invalid value '{value}' for container assignment"); return FullReturn(), False
            if len(path) == 0: self.__containers[cpath] = value; return None, True
            return self.__containers[cpath].access(path.copy(), value)
        else:
            if cpath in list(self.__vars):
                if value != NotNeeded: self.__vars[cpath] = value; return None, True
                else: return self.__vars[cpath], True
            else:
                if cpath in list(self.__consts.keys()):
                    if value != NotNeeded: self.__consts[cpath] = value; return None, True
                    else: return self.__consts[cpath], True
                else:
                    if cpath in list(self.__funcs):
                        if value != NotNeeded: self.__funcs[cpath] = value; return None, True
                        else: return self.__funcs[cpath], True
                    else:
                        return TT.ILLEGAL, False
    
    def copy(self): return MendContainer(self.__vars, self.__consts, self.__funcs, self.__containers)

    def __repr__(self) -> str: return "container{\n" + f"   vars: {self.__vars}\n   consts: {self.__consts}\n   funcs: {self.__funcs}\n   containers: {self.__containers}\n" + "}"



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
            case default: return None
    except ValueError as e: log_error(e, line); return FullReturn()


def log_error(details: str, line: int): print(f"error: {details} on line {line+1}")

def log_warning(details: str, line: int): print(f"warning from line {line+1}: {details}")


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


def get_variable(variable_token: Token, tokens: list[Token], variables: dict[str, Any], constants: ImmutDict, functions: dict[str, tuple[tuple[tuple[tuple[str, bool]], list[Token]]]], line: int, debug: bool = False):
    if istoken(variable_token, TT.IDENT):
        not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
        from_mutable = variables.get(variable_token.value, not_found_id)
        if from_mutable == not_found_id:
            from_immutable = constants.get(variable_token.value, not_found_id)
            if from_immutable == not_found_id: return TT.ILLEGAL
            else: return from_immutable
        else: return from_mutable
    else: return variable_token.value


def scrape_funcinputs(tokens: list[Token], vars: dict[str, Any], consts: ImmutDict, funcs: dict[str, MendFunction], funcargs: list[MendFuncArg], line: int) -> list[list[Any, MendFuncArg]]:
    out = []
    looking_for_comma = False
    for i, t in enumerate(tokens):
        if i in (0, 1, len(tokens)-1): continue
        i -= 3
        if i > len(funcargs)-1: log_error(f"too many arguments given(expected {len(funcargs)}, but got {len([tx for tx in tokens if tx.type != TT.COMMA]) - 3} instead)", line); return TT.ILLEGAL
        if looking_for_comma:
            if not istoken(t, TT.COMMA): log_error("expected comma", line); return TT.ILLEGAL
            looking_for_comma = False
        else:
            if istoken(t, TT.IDENT):
                ident = t.value
                if ident in list(vars): out.append([vars[ident], funcargs[i]])
                else:
                    if ident in list(consts.keys()): out.append([consts[ident], funcargs[i]])
                    else:
                        if ident in list(funcs): out.append([funcs[ident].copy(), funcargs[i]])
                        else: log_error(f"(funcinscrape)unknown variable '{ident}'", line); return TT.ILLEGAL
            elif istoken(t, (TT.BOOL, TT.STRING, TT.INT, TT.FLOAT)): out.append([t.value, funcargs[i]])
            else: log_error("expected 'identifier', 'string', 'int', 'float', or 'bool', but got '' instead", line); return TT.ILLEGAL
            looking_for_comma = True
    return out


def scrape_funcargs(tokens: list[Token], line: int) -> list[MendFuncArg]:
    out = []
    for i, t in enumerate(tokens):
        if i in (0, 1, 2, len(tokens)-1): continue
        if istoken(t, TT.IDENT): out.append(MendFuncArg(t.value, True))
        else: return log_error(f"expected identifier, but found '{t}' instead", line); TT.ILLEGAL
    return out


def inject_args(vars: dict[str, Any], funcs: dict[str, MendFunction], fargs: list[list[Any, MendFuncArg]]):
    for f in fargs:
        value, mfa = f
        if isinstance(value, MendFunction): funcs[mfa.getname()] = value
        vars[mfa.getname()] = value
    return vars, funcs


def record_until_endtoken(token_lines: list[list[Token]], starting_idx: int) -> list[list[Token]]:
    ln = starting_idx
    #, keyword: str
    uses_end = [
        'func',
        'repeat'
    ]
    '''
    if keyword not in uses_end:
        temp = uses_end.pop()
        temp_joined = ', '.join([f"'{u}'" for u in uses_end])
        raise Exception(f"(record_until_endtoken) expected {temp_joined}, or '{temp}' as keyword, but got '{keyword}' instead")
    '''
    out = []
    nest = 0
    while ln < len(token_lines):
        #print(ln, token_lines[ln], nest)
        if len(token_lines[ln]) > 0:
            if istoken(token_lines[ln][0], TT.KEYWORD, 'end'):
                if nest == 0: break
                else: out.append(token_lines[ln]); nest -= 1
            else:
                if istoken(token_lines[ln][0], TT.KEYWORD, tuple(uses_end)): nest += 1
                out.append(token_lines[ln]); ln += 1
        else: ln += 1
    return out, ln


class Null:
    def __repr__(self): return 'null'

class FullReturn: pass

def interpret(token_lines: list[list[Token]], isfunc: bool = False, funcargs: list[list[Any, MendFuncArg]] = [], isimported: bool = False, root_folder: str = ''):
    # flags
    jump_to_next_end = False

    vars: dict[str, Any] = {}
    consts: ImmutDict = ImmutDict()
    '''
    'Yell': MendFunction(
            'Yell',
            [],
            [
                [
                    Token(TT.KEYWORD, 'log'), Token(TT.STRING, 'A' + ('H' * 50))
                ]
            ],
            True
        )
    '''
    funcs: dict[str, MendFunction] = {}
    if len(funcargs) > 0: vars = inject_args(vars, funcargs)

    containers: dict[str, MendContainer] = {}

    #print(funcs)

    #print(vars, isfunc)

    ignore_warnings = 0

    ln = 0
    while ln < len(token_lines):
        print_debug = False
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
                    err = f"illegal character '{t.value[0]}'" if isinstance(t.value, (tuple, list)) else f"illegal character '{t.value}'"
                    if len(t.value) > 1 and isinstance(t.value, (tuple, list)): err += f'({t.value[1]})'
                    log_error(err, ln)
                    return FullReturn()
            
            #print(toks, funcs, istoken(toks[0], value=tuple(funcs.keys())), "\n")
            
            if istoken(toks[-1], TT.DEBUG):
                print_debug = True
                del toks[-1]
                if len(toks) < 1: ln += 1; continue

            if istoken(toks[0], TT.KEYWORD):
                if istoken(toks[0], value='stop'): return TT.STOP

                if istoken(toks[0], value='import'):
                    if len(toks) < 2: log_error("malformed import(missing item to import)", ln); return FullReturn()
                    if istoken(toks[1], (TT.STRING, TT.IDENT)):
                        tok_value = toks[1].value
                        if istoken(toks[1], TT.IDENT):
                            var_result = get_variable(toks[1], toks, vars, consts, funcs, ln)
                            if var_result == TT.ILLEGAL: log_error(f"unknown variable '{toks[1].value}'", ln); return FullReturn()
                            if not isinstance(var_result, str): log_error(f"expected 'string', but got '{var_result}' of type {type(var_result).__name__} instead", ln); return FullReturn()
                            tok_value = var_result
                        import_path = tok_value + '.mend' if '.' not in toks[1].value.removeprefix('./') else tok_value
                        if not Path(root_folder, import_path).exists():
                            log_error(f"malformed import(path '{import_path}' doesn't exist)", ln)
                            if print_debug: print([str(p) for p in Path('./').iterdir()])
                            return FullReturn()
                        try:
                            with open(Path(root_folder, import_path), 'rt') as imp_file:
                                imported = interpret([[t for t in LineLexer(l).lex_to_tokens() if t.type != TT.COMMENT] for l in imp_file.read().split('\n')], isimported=True)
                                #print(imported)
                                if isinstance(imported, FullReturn): return FullReturn()
                                if imported != None:
                                    vars = extend_dict(vars, imported[0], True)
                                    consts.extend(imported[1])
                                    funcs = extend_dict(vars, imported[2], True)
                        except Exception as e: log_error(f"malformed import({e})", ln); return FullReturn()
                    else: log_error(f"malformed import(invalid import item '{toks[1].type}')", ln); return FullReturn()

                elif istoken(toks[0], value='log'):
                    var_result = get_variable(toks[1], toks, vars, consts, funcs, ln)
                    if var_result == TT.ILLEGAL: log_error(f"could not log unknown variable '{toks[1].value}'", ln); return FullReturn()
                    print(var_result)
                
                elif istoken(toks[0], value='get'):
                    if len(toks) == 2:
                        if istoken(toks[1], TT.IDENT):
                            uinp = input('give input\n')
                            vars[toks[1].value] = uinp
                    elif len(toks) > 2:
                        if istoken(toks[1], TT.KEYWORD) and istoken(toks[2], TT.IDENT):
                            match toks[1].value:
                                case 'mut':
                                    uinp = input('give input\n')
                                    vars[toks[1].value] = uinp
                                case 'immut':
                                    uinp = input('give input\n')
                                    vars[toks[1].value] = uinp
                                case default:
                                    log_error(f"malformed get statement(invalid keyword '{toks[1].value}')", ln); return FullReturn()
                    else:
                        log_error(f"malformed get statement(expected 'mut [variable name]', 'immut [variable name]', or '[variable name]')", ln); return FullReturn()
                
                elif istoken(toks[0], value='if'):
                    if not istoken(toks[-1], TT.KEYWORD, 'then'):
                        log_error("missing 'then' to close 'if'", ln)
                        return FullReturn()
                
                elif istoken(toks[0], value='mut'):
                    if len(toks) == 2:
                        if istoken(toks[1], TT.IDENT):
                            if istoken(toks[1], value=tuple(vars.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return FullReturn()
                            vars[toks[1].value] = Null()
                        else: log_error('malformed variable declaration(missing variable name)', ln); return FullReturn()
                    elif len(toks) >= 4:
                        if istoken(toks[1], TT.IDENT) and istoken(toks[2], TT.KEYWORD, 'as'):
                            if istoken(toks[1], value=tuple(vars.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return FullReturn()
                            if istoken(toks[3], (TT.FLOAT, TT.INT, TT.STRING, TT.BOOL)): vars[toks[1].value] = toks[3].value
                            elif istoken(toks[3], TT.KEYWORD):
                                log_error(f"malformed variable declaration(invalid keyword '{toks[3].value}')", ln); return FullReturn()
                            elif istoken(toks[3], TT.IDENT):
                                not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                                from_mutable = vars.get(toks[1].value, not_found_id)
                                if from_mutable == not_found_id:
                                    from_immutable = consts.get(toks[1].value, not_found_id)
                                    if from_immutable == not_found_id:
                                        log_error(f"malformed variable declaration(unknown variable '{toks[1].value}')", ln); return FullReturn()
                                    else: vars[toks[1].value] = from_immutable
                                else: vars[toks[1].value] = from_mutable
                            elif istoken(toks[3], TT.LBRACKET):
                                ls = get_list(toks, ln)
                                if isinstance(ls, listgetter_fail): return
                                vars[toks[1].value] = ls
                            else: log_error(f"malformed variable declaration(invalid value '{toks[3].value}')", ln); return FullReturn()
                        else: log_error(f"malformed variable declaration(missing variable name and 'as' keyword)", ln); return FullReturn()
                    else: log_error('malformed variable declaration(missing variable name)', ln); return FullReturn()
                
                elif istoken(toks[0], value='immut'):
                    if len(toks) == 2:
                        if istoken(toks[1], TT.IDENT):
                            if istoken(toks[1], value=tuple(consts.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return FullReturn()
                            consts.add(toks[1].value, Null())
                        else: log_error('malformed variable declaration(missing variable name)', ln); return FullReturn()
                    elif len(toks) >= 4:
                        if istoken(toks[1], TT.IDENT) and istoken(toks[2], TT.KEYWORD, 'as'):
                            if istoken(toks[1], value=tuple(consts.keys())): log_error(f"can't declare variable '{toks[1].value}', already exists", ln); return FullReturn()
                            if istoken(toks[3], (TT.FLOAT, TT.INT, TT.STRING, TT.BOOL)): consts.add(toks[1].value, toks[3].value)
                            elif istoken(toks[3], TT.KEYWORD):
                                log_error(f"malformed variable declaration(invalid keyword '{toks[3].value}')", ln); return FullReturn()
                            elif istoken(toks[3], TT.IDENT):
                                not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                                from_mutable = consts.get(toks[1].value, not_found_id)
                                if from_mutable == not_found_id:
                                    from_immutable = consts.get(toks[1].value, not_found_id)
                                    if from_immutable == not_found_id:
                                        log_error(f"malformed variable declaration(unknown variable '{toks[1].value}')", ln); return FullReturn()
                                    else: consts.add(toks[1].value, from_immutable)
                                else: consts.add(toks[1].value, from_mutable)
                            elif istoken(toks[3], TT.LBRACKET):
                                ls = get_list(toks, ln)
                                if isinstance(ls, listgetter_fail): return
                                consts.add(toks[1].value, ls)
                            else: log_error(f"malformed variable declaration(invalid value '{toks[3].value}')", ln); return FullReturn()
                        else: log_error(f"malformed variable declaration(missing variable name and 'as' keyword)", ln); return FullReturn()
                    else: log_error('malformed variable declaration(missing variable name)', ln); return FullReturn()
                
                elif istoken(toks[0], value='set'): pass

                elif istoken(toks[0], value='return'):
                    if isfunc:
                        if len(toks) == 1: return
                        else:
                            if istoken(toks[1], TT.IDENT):
                                about_to_return = get_variable(toks[1])
                                if about_to_return == TT.ILLEGAL: log_error(f"unknown variable '{toks[1].value}'", ln); return FullReturn()
                                return about_to_return
                            else: log_error(f"invalid type for return '{toks[1].type}'", ln); return FullReturn()
                    else: log_error("invalid 'return'", ln); return FullReturn()
                
                elif istoken(toks[0], value='repeat'):
                    amount = 0
                    repeated, ln = record_until_endtoken(token_lines, ln+1)
                    ln += 1 # needed or the current line will be the loop's end token
                    if len(toks) >= 2:
                        if istoken(toks[1], (TT.IDENT)):
                            not_found_id = f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}'
                            from_mutable = vars.get(toks[1].value, not_found_id)
                            if from_mutable == not_found_id:
                                from_immutable = consts.get(toks[1].value, not_found_id)
                                if from_immutable == not_found_id: log_error(f"unknown variable '{toks[1].value}'", ln); return FullReturn()
                                else: amount = from_immutable
                            else: amount = from_mutable
                        elif istoken(toks[1], (TT.INT)): amount = toks[1].value
                        else: log_error(f"malformed repeat(invalid repeat amount {toks[1].type})", ln); return FullReturn()
                    else: log_error('malformed repeat(amount not given)', ln); return FullReturn()
                    for _ in range(amount):
                        iter_result = interpret(repeated)
                        if isinstance(iter_result, FullReturn): return FullReturn()
                        if iter_result == TT.STOP: break
                
                elif istoken(toks[0], value='func'):
                    if len(toks) >= 3:
                        if istoken(toks[1], TT.IDENT):
                            is_a_builtin_func = False
                            if len(toks) >= 5:
                                if istoken(toks[-1], TT.STATELABEL, 'builtin'):
                                    del toks[-1]
                                    is_a_builtin_func = True
                            if istoken(toks[2], TT.LPAREN) and istoken(toks[-1], TT.RPAREN):
                                funcname = toks[1].value
                                function_contents, ln = record_until_endtoken(token_lines, ln+1)
                                #print(function_contents)
                                ln += 1 # needed or the current line will be the function's end token
                                if funcname in list(funcs) and ignore_warnings == 0:
                                    if funcs[funcname].isbuiltin(): log_warning(f"declaration of function '{funcname}' is overriding a builtin function, did you mean to do this?(to stop this warning, add '@ignorewarning' on the line before)", ln)
                                    else: log_warning(f"declaration of function '{funcname}' is overriding a previous function, did you mean to do this?(to stop this warning, add '@ignorewarning' on the line before)", ln)
                                if len(toks) > 4: gotten_args = scrape_funcargs(toks, ln)
                                else: gotten_args = []
                                funcs[funcname] = MendFunction(funcname, gotten_args, function_contents, is_a_builtin_func)
                            else: log_error("malformed function declaration(missing parentheses)", ln); return FullReturn()
                        else: log_error("malformed function declaration(missing function name)", ln); return FullReturn()
                    else: log_error("malformed function declaration(missing function name and parentheses)", ln); return FullReturn()

            elif istoken(toks[0], TT.IDENT):
                if istoken(toks[0], value=tuple(funcs.keys())):
                    if len(toks) >= 3:
                        if istoken(toks[1], TT.LPAREN) and istoken(toks[-1], TT.RPAREN):
                            gottenfunction = funcs[toks[0].value]
                            if len(toks) > 3: gotten_inputs = scrape_funcinputs(toks, vars, consts, funcs, gottenfunction.get_args(), ln)
                            else: gotten_inputs = []
                            if gotten_inputs == TT.ILLEGAL: return FullReturn()
                            if print_debug: print('running function:'); print(gottenfunction); print('with inputs:'); print(gotten_inputs)
                            returned = gottenfunction.run(root_folder, gotten_inputs)
                            if isinstance(returned, FullReturn): return FullReturn()
                            if returned != None: pass
                        else: log_error("malformed function call(missing parentheses)", ln); return FullReturn()
                    elif len(toks) != 1: log_error("malformed function call", ln); return FullReturn()
                elif istoken(toks[0], value=tuple(vars)) or istoken(toks[0], value=tuple(consts.keys())):
                    if ignore_warnings == 0: log_warning(f"unused variable '{toks[0].value}'", ln)
                else:
                    log_error(f"unknown value '{toks[0].value}'", ln); return FullReturn()
            
            elif istoken(toks[0], TT.STATELABEL):
                if istoken(toks[0], value='ignorewarning'): ignore_warnings = 2
                else: log_error(f"unknown statelabel '{toks[0].value}'", ln); return FullReturn()


        #print('vars', vars)
        #print('consts', consts)
        
        if ignore_warnings > 0: ignore_warnings -= 1
        ln += 1
    if isimported: return vars, consts, funcs



def run(code: str | list[str] | tuple[str], root_folder: str = ''):
    lines = code.split('\n') if isinstance(code, str) else list(code)

    token_lines = [[t for t in LineLexer(l).lex_to_tokens() if t.type != TT.COMMENT] for l in lines]

    #print(token_lines)

    interpret(token_lines, root_folder=root_folder)


#with open('./repeat_test.mend', 'rt') as f: run(f.read())