#!/usr/bin/env python3

from regfix.dfa import DFA
import regfix.regex
import regfix
import rules

total_regex = regfix.regex.Union(*(rule.get_regex().as_term() for rule in rules.rules))
dfa = DFA(regfix.regex.RegEx(total_regex),
        ' !$\',-.0123456789?ABCDEFGHIJKLMNOPQRSTUVWXYZ^abcdefghijklmnopqrstuvwxyz+/"*:|(){}_\\')

err = input()
fix = regfix.RegFix(dfa, err)
print(fix.cost, fix.fix())