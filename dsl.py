import typing
from typing import List
import string
from copy import deepcopy
from regfix.regex import *

WS = PositiveClosure(Leaf(' '))
IDENTIFIER = PositiveClosure(Charset(string.ascii_letters + string.digits + '-'))
FILE = PositiveClosure(Charset(string.ascii_letters + string.digits + '-_.'))
FILES = PositiveClosure(Charset(string.ascii_letters + string.digits + '-_.*'))
PATH = PositiveClosure(Charset(string.ascii_letters + string.digits + '-_\.'))
PATHS = PositiveClosure(Charset(string.ascii_letters + string.digits + '-_\.*'))
NUMBER = PositiveClosure(Charset(string.digits))

class Argument :
    def __init__(self, regex: typing.Union[str, Term], mult='1') :
        assert mult in ['1', '?', '*', '+']
        if isinstance(regex, str) :
            if len(regex) and regex[0] == '<' and regex[-1] == '>':
                regex = _predefined_regex_map[regex]
            else :
                regex = Literal(regex)
        self.regex = deepcopy(regex)
        self.mult = mult

class Command :
    def __init__(self, name:str, positional:List[Argument]) :
        self.name = name
        self.positional:List[Argument] = positional
    
    def get_regex(self) -> RegEx :
        terms = [deepcopy(Optional(WS)), Literal(self.name), deepcopy(WS)]
        for arg in self.positional :
            reg = arg.regex
            mult = arg.mult
            if mult == '?' :
                reg = Optional(reg)
            elif mult == '*' :
                reg = KleeneClosure(reg)
            elif mult == '+' :
                reg = PositiveClosure(reg)
            terms.append(reg)
            terms.append(deepcopy(WS))
        terms[-1] = Optional(terms[-1])
        return RegEx(Concat(*terms))