#!/usr/bin/env python3
import regfix
from dfa import DFA
from regex import *

# KleeneClosure(Union(Literal('foo'), Literal('bar')))
regex = RegEx(KleeneClosure(Union(Literal('foo'), Literal('bar'))))
open('reg.gv', 'w').write(regex.export_graphviz('RegEx').source)
dfa = DFA(regex, 'abcdefghijklmnopqrstuvwxyz')
open('graph.gv', 'w').write(dfa.export_graphviz('DFA').source)
fix = regfix.RegFix(dfa, 'bababbabababaaab')
print(fix.cost)
print(fix.fix())