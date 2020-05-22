#!/usr/bin/env python3

from regfix.dfa import DFA
import regfix.regex
import regfix
import rules

total_regex = regfix.regex.Union(*(rule.get_regex().as_term() for rule in rules.rules))
reg = regfix.regex.RegEx(total_regex)

err = input()
fix = regfix.RegFix(reg, err)
print(fix.fix())
print(fix.cost)