#!/usr/bin/env python3
import glob
import os

cmds = ['apt-get', 'cat', 'cd', 'chmod', 'echo', 'expr', 'kill', 'ln', 'ls', 'man', 'mkdir', 
'mv', 'rmdir', 'tail', 'touch']

for cmd in cmds :
    files = glob.glob(f'dataset-txt/{cmd}-*.in')
    cnt, ok = 0, 0
    for fin in files :
        fout = fin[:-3] + '.out'
        err, corr = open(fin).readlines()
        fix = (open(fout).readlines() + [''])[0]
        cnt += 1
        if corr == fix : ok += 1
    print(cmd, f'{ok}/{cnt}', '%.4f'%(ok/cnt), sep='\t')