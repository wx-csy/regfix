import regex
from regex import Leaf, Term, Concat
from typing import Set
from memoize import *
import functools

class _Terminator(Leaf) :
    def __init__(self) :
        self.char = ''
        self.follow:Set[Leaf] = frozenset()

class DFA :
    def __init__(self, expr:Term) :
        self.regex = Concat(expr, _Terminator())
        self.states:Dict[Set[Leaf], 'State'] = dict()
        self.get_state(frozenset())

    def get_state(self, leaves:Set[Leaf]) -> 'State' :
        leaves = frozenset(leaves)
        if leaves not in self.states :
            self.states[leaves] = State(self, leaves)
        return self.states[leaves]

    @memoize_property
    def initial(self) -> 'State' :
        return self.get_state(self.regex.first)

    def capacity(self) -> int :
        return len(self.get_state.memo)

class State :
    def __init__(self, dfa:DFA, leaves:Set[Leaf]) :
        self.dfa = dfa
        self.leaves = frozenset(leaves)

    def __hash__(self) ->int :
        return hash(self.leaves)

    def __repr__(self) -> str :
        return repr(self.leaves) + ' ' + ':'.join(map(str, [x.follow for x in self.leaves]))
    
    @memoize_property
    def acceptable(self) :
        for leaf in self.leaves :
            if isinstance(leaf, _Terminator) :
                return True
        return False

    @memoize
    def next(self, char:str) :
        ret = set()
        for leaf in self.leaves :
            if leaf.char == char :
                ret |= leaf.follow
        return self.dfa.get_state(ret)