from abc import ABC, abstractproperty
from typing import Set, List, Iterable
from memoize import *
from graphviz import Digraph

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

class _Terminator(Leaf) :
    def __init__(self) :
        self.char = ''
        self.follow:Set[Leaf] = frozenset()

    @memoize_property
    def is_terminator(self) -> bool :
        return True

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

class RegEx :
    def __init__(self, term:Term) :
        self.term = Concat(term, _Terminator())

def Literal(s: str) -> Concat :
    return Concat(*map(Leaf, s))
