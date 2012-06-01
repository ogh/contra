#!/usr/bin/env python

'''
Featurise a context file.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-29
'''

from argparse import ArgumentParser
from sys import stdin, stdout, stderr

from clusters import BrownReader, GoogleReader, DavidReader
from config import BROWN_CLUSTERS_BY_SIZE
from it import nwise
from graph import prev_next_graph, SeqLblSearch
from gtbtokenize import tokenize

### Constants
BOW_TAG = 'bow'
COMP_TAG = 'comp'
BROWN_TAG = 'brown'
GOOGLE_TAG = 'google'
DAVID_TAG = 'david'
# From Turian et al. (2010)
BROWN_GRAMS = (4, 6, 10, 20, )
# Could be: 100, 320, 1000 or 3200
BROWN_SIZE = 3200
BROWN_READER = None
GOOGLE_READER = None

ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('-f', '--features',
        choices=(BOW_TAG, COMP_TAG, BROWN_TAG, GOOGLE_TAG, DAVID_TAG, ),
        # TODO: Update the default to the best one we got after experiments
        default=BOW_TAG)

FOCUS_DUMMY = "('^_^)WhatAmIDoingHere?"
###

from itertools import chain

def _bow_featurise(nodes, graph, focus):
    # XXX: TODO: Limited to three steps
    for _, _, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        yield 'BOW-{0}'.format(node.value), 1.0

def _comp_featurise(nodes, graph, focus):
    # XXX: TODO: Limited to three steps

    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        f_name = 'WEIGHTED-POSITIONAL-{0}-{1}'.format('-'.join(lbl_path),
                node.value)
        f_val = 1.0 / (2 ** (len(lbl_path) - 1))
        yield f_name, f_val

    # Token grams
    for gram_size in (3, ):
        for tok_gram in nwise((n.value for n in nodes), gram_size):
            yield 'TOK-GRAM-{0}-{1}'.format(gram_size, '-'.join(tok_gram)), 1.0

def _brown_featurise(nodes, graph, focus):
    # "Inherit" all competitive features
    for res in _comp_featurise(nodes, graph, focus):
        yield res

    global BROWN_READER
    if BROWN_READER is None:
        # For experiments with different size non-PubMed clusters
        #with open(BROWN_CLUSTERS_BY_SIZE[BROWN_SIZE], 'r') as brown_file:
        from config import PUBMED_BROWN_CLUSTERS_PATH
        with open(PUBMED_BROWN_CLUSTERS_PATH, 'r') as brown_file:
            BROWN_READER = BrownReader(l.rstrip('\n') for l in brown_file)

    # XXX: TODO: Limited to three steps
    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        try:
            brown_cluster = BROWN_READER[node.value]
            for brown_gram in BROWN_GRAMS:
                if len(brown_cluster) < brown_gram:
                    # Don't overgenerate if we don't have enough grams
                    break
                f_name = 'BROWN-{0}-{1}'.format('-'.join(lbl_path),
                        brown_cluster)
                yield f_name, 1.0
        except KeyError:
            # Only generate if we actually have an entry in the cluster
            pass

DAVID_READER = None
def _david_featurise(nodes, graph, focus):
    # "Inherit" all competitive features
    for res in _comp_featurise(nodes, graph, focus):
        yield res

    global DAVID_READER
    if DAVID_READER is None:
        from config import DAVID_CLUSTERS_PATH
        with open(DAVID_CLUSTERS_PATH, 'r') as david_file:
            DAVID_READER = DavidReader(l.rstrip('\n') for l in david_file)

    # XXX: TODO: Limited to three steps
    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        try:
            david_cluster = DAVID_READER[node.value]
            f_name = 'DAVID-{0}-{1}'.format('-'.join(lbl_path),
                    david_cluster)
            yield f_name, 1.0
        except KeyError:
            # Only generate if we actually have an entry in the cluster
            pass

def _google_featurise(nodes, graph, focus):
    # "Inherit" all competitive features
    for res in _comp_featurise(nodes, graph, focus):
        yield res

    global GOOGLE_READER
    if GOOGLE_READER is None:
        from config import PHRASE_CLUSTERS_PATH
        with open(PHRASE_CLUSTERS_PATH, 'r') as google_file:
            GOOGLE_READER = GoogleReader(l.rstrip('\n') for l in google_file)

    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        try:
            distance_by_cluster = GOOGLE_READER[node.value]
            for cluster, distance in distance_by_cluster.iteritems():
                f_name = 'GOOGLE-{0}-{1}'.format('-'.join(lbl_path), cluster)
                yield f_name, distance
        except KeyError:
            # Only generate if we actually have an entry in the cluster
            pass

F_FUNC_BY_F_SET = {
        BOW_TAG: _bow_featurise,
        COMP_TAG: _comp_featurise,
        BROWN_TAG: _brown_featurise,
        GOOGLE_TAG: _google_featurise,
        DAVID_TAG: _david_featurise,
        }

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    for line in (l.rstrip('\n') for l in stdin):
        _, lbl, pre, _, post = line.split('\t')
        
        # Tokenise the context
        # XXX: Discards meaningful spaces
        pre_toks = tokenize(pre.strip()).split()
        post_toks = tokenize(post.strip()).split()

        toks = pre_toks[-3:] + [FOCUS_DUMMY] + post_toks[:3]

        graph, nodes = prev_next_graph(toks)
        for node in nodes:
            if node.value == FOCUS_DUMMY:
                focus = node
                break
        else:
            assert False

        f_vec = {}
        for f_name, f_val in F_FUNC_BY_F_SET[argp.features](nodes, graph,
                focus):
            f_vec[f_name] = f_val

        if not f_vec:
            print >> stderr, 'WARNING: No features generated!'
            continue

        stdout.write(lbl)
        stdout.write('\t')
        stdout.write(' '.join('{0}:{1}'.format(f_name, f_vec[f_name])
            for f_name in sorted(f_vec)))
        stdout.write('\n')

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
