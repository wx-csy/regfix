#!/usr/bin/env python3
import regfix
from dfa import DFA
from regex import *

# KleeneClosure(Union(Literal('foo'), Literal('bar')))
dfa = DFA(RegEx(KleeneClosure(Union(Literal('foo'), Literal('bar')))),
    'abcdefghijklmnopqrstuvwxyz')
open('graph.gv', 'w').write(dfa.export_graphviz('DFA').source)
fix = regfix.RegFix(dfa, 'bababbabababaaab')
print(fix.cost)
print(fix.fix())