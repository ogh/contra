#!/usr/bin/env python

'''
Featurise a context file.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-29
'''

from argparse import ArgumentParser
from sys import stdin, stdout

from gtbtokenize import tokenize

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('-f', '--features', choices=('BOW', ), default='BOW')
###

def main(args):
    argp = ARGPARSER.parse_args(args[1:])
    for line in (l.rstrip('\n') for l in stdin):
        _, lbl, pre, _, post = line.split('\t')
        
        # Tokenise the context
        # XXX: Discards meaningful spaces
        pre_toks = tokenize(pre.strip()).split()
        pre_toks.reverse()
        post_toks = tokenize(post.strip()).split()

        #XXX: This is the BoW featurisation code
        f_vec = {}
        for pre_tok_i, pre_tok in enumerate(pre_toks, start=1):
            f_name = 'BEFORE-{}'.format(pre_tok)
            f_val = 1.0 / (2 ** (pre_tok_i - 1))
            f_vec[f_name] = f_val
            if pre_tok_i >= 3:
                break
        for post_tok_i, post_tok in enumerate(post_toks, start=1):
            f_name = 'AFTER-{}'.format(post_tok)
            f_val = 1.0 / (2 ** (post_tok_i - 1))
            f_vec[f_name] = f_val
            if post_tok_i >= 3:
                break

        stdout.write(lbl)
        stdout.write('\t')
        stdout.write(' '.join('{}:{}'.format(f_name, f_vec[f_name])
            for f_name in sorted(f_vec)))
        stdout.write('\n')

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
