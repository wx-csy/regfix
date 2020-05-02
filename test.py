#!/usr/bin/env python3
import regfix
from dfa import DFA
from regex import *

# KleeneClosure(Union(Literal('foo'), Literal('bar')))
dfa = DFA(KleeneClosure(Union(Literal('foo'), Literal('bar'))))
fix = regfix.RegFix(dfa, 'foozbarbaz', 'abcdefghijklmnopqrstuvwxyz')
print(fix.cost)
print(fix.fix())