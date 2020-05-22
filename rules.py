from dsl import *

rules: List[Command] = [
    # apt-get
    Command('apt-get', [
        Argument('install'),
        Argument(IDENTIFIER)
    ]),

    Command('apt-get', [
        Argument('remove'),
        Argument(IDENTIFIER)
    ]),

    Command('apt-get', [
        Argument('update')
    ]),

    Command('apt-get', [
        Argument('upgrade')
    ]),

    # cat
    Command('cat', [
        Argument(FILES, '+')
    ]),

    # cd
    Command('cd', [
        Argument(PATH)
    ]),

    # chmod
    Command('chmod', [
        Argument(PositiveClosure(Charset('au+-rwx'))),
        Argument(FILES, '+')
    ]),

    # echo
    Command('echo', [
        Argument(PositiveClosure(
                Charset(' !$\',-.0123456789?ABCDEFGHIJKLMNOPQRSTUVWXYZ^abcdefghijklmnopqrstuvwxyz+/"*:|(){}_\\')
            ), '*')
    ]),

    # expr
    Command('expr', [
        Argument(NUMBER),
        Argument(Charset('+-*/')),
        Argument(NUMBER)
    ]),

    # find
    # to be done

    # kill
    Command('kill', [
        Argument(NUMBER)
    ]),

    # ln
    Command('ln', [
        Argument('-s', '?'),
        Argument(PATHS, '+'),
        Argument(PATH)
    ]),

    # ls
    Command('ls', [
        Argument(Union(Literal('-al'), Literal('-d')), '?'),
        Argument(PATHS, '+')
    ]),

    # man
    Command('man', [
        Argument(NUMBER, '?'),
        Argument(IDENTIFIER)
    ]),
    
    # mkdir
    Command('mkdir', [
        Argument(PATH, '+')
    ]),

    # mv
    Command('mv', [
        Argument(PATHS, '+'),
        Argument(PATH)
    ]),

    # ping
    # to be done

    # rmdir
    Command('rmdir', [
        Argument(PATHS, '+')
    ]),

    # sort
    # to be done

    # tail
    Command('tail', [
        Argument(Concat(Leaf('-'), NUMBER), '?'),
        Argument(PATH)
    ]),

    # touch
    Command('touch', [
        Argument(PATHS, '+')
    ])
]