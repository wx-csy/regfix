from abc import ABC, abstractproperty
from typing import Set, List, Iterable
from .memoize import *
from graphviz import Digraph

class _Graphviz_Drawer :
    def __init__(self, name:str='') :
        self.graph = Digraph(name=name)
        self.graph.attr(ordering='out')
        self.statemap:Dict['Term', int] = dict()

class Term(ABC) :
    @abstractproperty
    def nullable(self) -> bool:
        # whether the term can generate empty string
        pass

    @abstractproperty
    def first(self) -> Set['Leaf'] :
        # the set of first possible character of this term
        pass

    @abstractproperty
    def last(self) -> Set['Leaf'] :
        # the set of last possible character of this term
        pass

    @abstractproperty
    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        pass

class Leaf(Term) :
    def __init__(self, char:str) :
        assert len(char) == 1
        self.char = char
        self.follow:Set['Leaf'] = frozenset()
    
    def __hash__(self) :
        return id(self)

    @memoize_property
    def nullable(self) -> bool:
        return False

    @memoize_property
    def first(self) -> Set['Leaf']:
        return frozenset([self])
    
    @memoize_property
    def last(self) -> Set['Leaf']:
        return frozenset([self])

    @memoize_property
    def is_terminator(self) -> bool :
        return False

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label=self.char, shape='plain')
        return identifier

    def __repr__(self) -> str:
        return self.char

class _Terminator(Leaf) :
    def __init__(self) :
        self.char = ''
        self.follow:Set[Leaf] = frozenset()

    @memoize_property
    def is_terminator(self) -> bool :
        return True
    
    def __repr__(self) -> str:
        return '$'

class Empty(Term) :
    def __init__(self) :
        pass
    
    @memoize_property
    def nullable(self) -> bool :
        return True
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        return frozenset()
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        return frozenset()

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='', shape='circle')
        return identifier
    
    def __repr__(self) -> str:
        return ''

class Optional(Term) :
    def __init__(self, term:Term) :
        self.term:Term = term
    
    @memoize_property
    def nullable(self) -> bool :
        return True
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        return self.term.first
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        return self.term.last

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='?', shape='circle')
        drawer.graph.edge(str(identifier), str(self.term._export_graphviz(drawer)))
        return identifier

    def __repr__(self) -> str:
        return f'({repr(self.term)})?'
    
class Concat(Term) :
    def __init__(self, *terms) :
        self.terms:List[Term] = list(terms)
        
        # update follow
        lasts = []
        last = set()
        for t in terms :
            if t.nullable :
                last |= t.last
            else :
                last = t.last
            lasts.append(frozenset(last))

        firsts = []
        first = set()
        for t in reversed(terms) :
            if t.nullable :
                first |= t.first
            else :
                first = t.first
            firsts.append(frozenset(first))
        firsts = list(reversed(firsts))

        for i in range(1, len(self.terms)) :
            for leaf in lasts[i-1] :
                leaf.follow |= firsts[i]
    
    @memoize_property
    def nullable(self) -> bool :
        for term in self.terms :
            if not term.nullable :
                return False
        return True
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        ret = set()
        for term in self.terms :
            ret |= term.first
            if not term.nullable :
                break
        return frozenset(ret)
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        ret = set()
        for term in reversed(self.terms) :
            ret |= term.last
            if not term.nullable :
                break
        return frozenset(ret)

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='', shape='circle')
        for child in self.terms :
            drawer.graph.edge(str(identifier), str(child._export_graphviz(drawer)))
        return identifier
    
    def __repr__(self) -> str:
        return f'({"".join(map(repr, self.terms))})'

class Union(Term) :
    def __init__(self, *terms) :
        self.terms:List[Term] = list(terms)
    
    @memoize_property
    def nullable(self) -> bool :
        for term in self.terms :
            if term.nullable :
                return True
        return False
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        ret = set()
        for term in self.terms :
            ret |= term.first
        return frozenset(ret)
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        ret = set()
        for term in reversed(self.terms) :
            ret |= term.last
        return frozenset(ret)

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='|', shape='circle')
        for child in self.terms :
            drawer.graph.edge(str(identifier), str(child._export_graphviz(drawer)))
        return identifier

    def __repr__(self) :
        return f'({"|".join(map(repr, self.terms))})'

class KleeneClosure(Term) :
    def __init__(self, term:Term) :
        self.term:Term = term

        # update follow
        for leaf in term.last :
            leaf.follow = frozenset(leaf.follow | term.first)
    
    @memoize_property
    def nullable(self) -> bool :
        return True
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        return self.term.first
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        return self.term.last

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='*', shape='circle')
        drawer.graph.edge(str(identifier), str(self.term._export_graphviz(drawer)))
        return identifier

    def __repr__(self) -> str:
        return f'({repr(self.term)}*)'

class PositiveClosure(Term) :
    def __init__(self, term:Term) :
        self.term:Term = term
        
        # update follow
        for leaf in term.last :
            leaf.follow = frozenset(leaf.follow | term.first)
    
    @memoize_property
    def nullable(self) -> bool :
        return self.term.nullable
    
    @memoize_property
    def first(self) -> Set[Leaf] :
        return self.term.first
    
    @memoize_property
    def last(self) -> Set[Leaf] :
        return self.term.last

    def _export_graphviz(self, drawer:_Graphviz_Drawer) :
        identifier = len(drawer.statemap) + 1
        drawer.statemap[self] = identifier
        drawer.graph.node(str(identifier), label='*', shape='circle')
        drawer.graph.edge(str(identifier), str(self.term._export_graphviz(drawer)))
        return identifier


    def __repr__(self) -> str:
        return f'({repr(self.term)}+)'

class RegEx :
    def __init__(self, term:Term) :
        self.term = Concat(term, _Terminator())
    
    def export_graphviz(self, name:str='') -> Digraph :
        drawer = _Graphviz_Drawer(name)
        self.term.terms[0]._export_graphviz(drawer)
        return drawer.graph

    def __repr__(self) -> str :
        return f'^{self.term.terms[0]}$'

def Literal(s: str) -> Concat :
    return Concat(*map(Leaf, s))
