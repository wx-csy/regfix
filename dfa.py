from regex import RegEx, Term, Leaf
from typing import Set
from memoize import *
from graphviz import Digraph
import functools

class _Graphviz_Drawer :
    def __init__(self, name:str='') :
        self.graph = Digraph(name=name)
        self.statemap:Dict['State', int] = dict()
        self.graph.attr(rankdir='LR')

class DFA :
    def __init__(self, expr:RegEx, charset:str) :
        assert isinstance(expr, RegEx)
        self.regex:Term = expr.term
        self.states:Dict[Set[Leaf], 'State'] = dict()
        self.charset:str = charset
        self.nullstate:'State' = self.get_state(frozenset())

    def get_state(self, leaves:Set[Leaf]) -> 'State' :
        leaves = frozenset(leaves)
        if leaves not in self.states :
            self.states[leaves] = State(self, leaves)
        return self.states[leaves]

    @memoize_property
    def initial(self) -> 'State' :
        return self.get_state(self.regex.first)

    def export_graphviz(self, name:str='') -> Digraph :
        ''' Generate graphviz object.
        >>> from regex import *
        >>> dfa = DFA(RegEx(KleeneClosure(Union(Literal('foo'), Literal('bar')))),
        ... 'abcdefghijklmnopqrstuvwxyz')
        >>> print(dfa.export_graphviz('DFA').source) # doctest: +NORMALIZE_WHITESPACE
        digraph DFA {
            rankdir=LR
            1 [shape=doublecircle]
            2 [shape=circle]
            3 [shape=circle]
            3 -> 1 [label=r]
            2 -> 3 [label=a]
            1 -> 2 [label=b]
            4 [shape=circle]
            5 [shape=circle]
            5 -> 1 [label=o]
            4 -> 5 [label=o]
            1 -> 4 [label=f]
        }
        '''
        drawer = _Graphviz_Drawer(name=name)
        drawer.statemap[self.nullstate] = 0
        self.initial._export_graphviz(drawer)
        return drawer.graph

class State :
    def __init__(self, dfa:DFA, leaves:Set[Leaf]) :
        self.dfa = dfa
        self.leaves = frozenset(leaves)

    def __hash__(self) ->int :
        return hash(self.leaves)

    def __repr__(self) -> str :
        return repr(self.leaves) + ' ' + ':'.join(map(lambda x: str(x.follow), self.leaves))
    
    @memoize_property
    def accept(self) :
        for leaf in self.leaves :
            if leaf.is_terminator :
                return True
        return False

    @memoize
    def next(self, char:str) :
        ret = set()
        for leaf in self.leaves :
            if leaf.char == char :
                ret |= leaf.follow
        return self.dfa.get_state(ret)

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        if self in drawer.statemap :
            return drawer.statemap[self]
        identifier = len(drawer.statemap)
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), shape='doublecircle' if self.accept else 'circle')
        for ch in self.dfa.charset :
            next_identifier = self.next(ch)._export_graphviz(drawer)
            if next_identifier :
                drawer.graph.edge(str(identifier), str(next_identifier), label=ch)
        return identifier