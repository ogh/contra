#!/usr/bin/env python

'''
Featurise a context file.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-29
'''

from argparse import ArgumentParser
from collections import defaultdict
from functools import partial
from sys import stdin, stdout, stderr

from clusters import BrownReader, GoogleReader, DavidReader, TsvReader
from config import BROWN_CLUSTERS_BY_SIZE, PUBMED_BROWN_CLUSTERS_BY_SIZE
# Import the wordrepr paths from the config
from config import HLBL_BIO_PUBMED_100K_PATH, HLBL_BIO_PUBMED_500K_PATH, HLBL_NEWS_100D_PATH
from config import LSPACE_BIO_170D_PATH, LSPACE_BIO_PREPRO_PATH, LSPACE_BIO_170D_EXACT_PATH
from config import LSPACE_BIO_170D_PROB_PATH
from config import HLBL_BIO_PUBMED_100K_MINMAXCOL_NORM_PATH, HLBL_BIO_PUBMED_500K_MINMAXCOL_NORM_PATH
from config import HLBL_BIO_PUBMED_100K_VECLENGTH_NORM_PATH, HLBL_BIO_PUBMED_500K_VECLENGTH_NORM_PATH
from config import SPEED_BIO_50D_PATH
from it import nwise
from graph import prev_next_graph, SeqLblSearch
from gtbtokenize import tokenize

### Constants
BOW_TAG = 'bow'
COMP_TAG = 'comp'
BROWN_TAG = 'brown-{0}'
PUBMED_BROWN_TAG = 'pubmed_brown-{0}'
HLBL_PUBMED_100K_TAG = 'hlbl-pubmed-100k'
HLBL_PUBMED_500K_TAG = 'hlbl-pubmed-500k'
HLBL_PUBMED_100K_MINMAXCOL_NORM_TAG = 'hlbl-pubmed-100k-minmaxcol-norm'
HLBL_PUBMED_500K_MINMAXCOL_NORM_TAG = 'hlbl-pubmed-500k-minmaxcol-norm'
HLBL_PUBMED_100K_VECLENGTH_NORM_TAG = 'hlbl-pubmed-100k-veclength-norm'
HLBL_PUBMED_500K_VECLENGTH_NORM_TAG = 'hlbl-pubmed-500k-veclength-norm'
HLBL_NEWS_100D_TAG = 'hlbl-news-100d'
LSPACE_BIO_170D_TAG = 'lspace-bio-170d'
LSPACE_BIO_170D_PROB_TAG = 'lspace-bio-170d-prob'
LSPACE_BIO_170D_EXACT_TAG = 'lspace-bio-170d-exact'
SPEED_BIO_50D_TAG = 'speed-bio-50d'
LSPACE_BIO_PREPRO_TAG = 'lspace-bio-preprocessed'
GOOGLE_TAG = 'google'
DAVID_TAG = 'david'
# From Turian et al. (2010)
BROWN_GRAMS = (4, 6, 10, 20, )
# Global dictionary that contains all the readers
# The readers will be initialized lazily
READERS = {}

FOCUS_DUMMY = "('^_^)WhatAmIDoingInAFeatureRepresentation?"
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

def _brown_featurise(clusters_by_size, size, nodes, graph, focus):
    # TODO: This is not a particularily pretty way to handle the readers
    global READERS
    if 'BROWN_READERS' not in READERS:
        READERS['BROWN_READERS'] = defaultdict(dict)
    BROWN_READERS = READERS['BROWN_READERS']
    reader_key = ''.join(str(k) for k in clusters_by_size)
    try:
        reader = BROWN_READERS[reader_key][size]
    except KeyError:
        with open(clusters_by_size[size], 'r') as brown_file:
            reader = BrownReader(l.rstrip('\n') for l in brown_file)
        BROWN_READERS[reader_key][size] = reader

    # XXX: TODO: Limited to three steps
    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        try:
            brown_cluster = reader[node.value]
            for brown_gram in BROWN_GRAMS:
                if len(brown_cluster) < brown_gram:
                    # Don't overgenerate if we don't have enough grams
                    break
                f_name = 'BROWN-{0}-{1}-{2}'.format(size,
                        '-'.join(lbl_path), brown_cluster)
                yield f_name, 1.0
        except KeyError:
            # Only generate if we actually have an entry in the cluster
            pass

def _david_featurise(nodes, graph, focus):
    global READERS
    if 'DAVID_READER' not in READERS:
        from config import DAVID_CLUSTERS_PATH
        with open(DAVID_CLUSTERS_PATH, 'r') as david_file:
            READERS['DAVID_READER'] = DavidReader(l.rstrip('\n') for l in david_file)
    DAVID_READER = READERS['DAVID_READER']
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
    global READERS
    if 'GOOGLE_READER' not in READERS:
        from config import PHRASE_CLUSTERS_PATH
        with open(PHRASE_CLUSTERS_PATH, 'r') as google_file:
            READERS['GOOGLE_READER'] = GoogleReader(l.rstrip('\n') for l in google_file)
    GOOGLE_READER = READERS['GOOGLE_READER']

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

def _tsv_featurise(wordrepr_path,separator,wordrepr_name,reader_id,nodes, graph, focus):
    global READERS
    reader_key = wordrepr_name + '_'+reader_id+'_READER'
    if reader_key not in READERS:
        with open(wordrepr_path, 'r') as input_file:
            READERS[reader_key] = TsvReader([l.rstrip('\n') for l in input_file],separator)
    CURRENT_READER = READERS[reader_key]

    for _, lbl_path, node in chain(
            graph.walk(focus, SeqLblSearch(('PRV', 'PRV', 'PRV'))),
            graph.walk(focus, SeqLblSearch(('NXT', 'NXT', 'NXT')))
            ):
        try:
            vector_value = CURRENT_READER[node.value]
            for component, value in vector_value.iteritems():
                f_name = '{3}_{2}-{0}-{1}'.format('-'.join(lbl_path), component, reader_id, wordrepr_name)
                yield f_name, value
        except KeyError:
            # Only generate if we actually have an entry in the cluster
            pass
            
### Trailing constants
F_FUNC_BY_F_SET = {
        BOW_TAG: _bow_featurise,
        COMP_TAG: _comp_featurise,
        GOOGLE_TAG: _google_featurise,
        # HLBL
        HLBL_PUBMED_100K_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_100K_PATH, ' ', 'HLBL', 'bio_pubmed_100k'),
        HLBL_PUBMED_500K_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_500K_PATH, ' ', 'HLBL', 'bio_pubmed_500k'),
        HLBL_PUBMED_100K_MINMAXCOL_NORM_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_100K_MINMAXCOL_NORM_PATH, ' ', 'HLBL', 'bio_pubmed_100k_minmaxcol_norm'),
        HLBL_PUBMED_500K_MINMAXCOL_NORM_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_500K_MINMAXCOL_NORM_PATH, ' ', 'HLBL', 'bio_pubmed_500k_minmaxcol_norm'),
        HLBL_PUBMED_100K_VECLENGTH_NORM_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_100K_VECLENGTH_NORM_PATH, ' ', 'HLBL', 'bio_pubmed_100k_veclength_norm'),
        HLBL_PUBMED_500K_VECLENGTH_NORM_TAG: partial(_tsv_featurise, HLBL_BIO_PUBMED_500K_VECLENGTH_NORM_PATH, ' ', 'HLBL', 'bio_pubmed_500k_veclength_norm'),
        HLBL_NEWS_100D_TAG: partial(_tsv_featurise, HLBL_NEWS_100D_PATH,' ','HLBL', 'news_100d'),
        # LSPACE
        LSPACE_BIO_170D_TAG: partial(_tsv_featurise, LSPACE_BIO_170D_PATH, ' ', 'LSPACE', 'lspace_bio_170d'),
        LSPACE_BIO_170D_PROB_TAG: partial(_tsv_featurise, LSPACE_BIO_170D_PROB_PATH, '\t', 'LSPACE', 'lspace_bio_170d_prob'),
        LSPACE_BIO_170D_EXACT_TAG: partial(_tsv_featurise, LSPACE_BIO_170D_EXACT_PATH, '\t', 'LSPACE', 'lspace_bio_170d_exact'),
        LSPACE_BIO_PREPRO_TAG: partial(_tsv_featurise, LSPACE_BIO_PREPRO_PATH, ' ', 'LSPACE', 'lspace_bio_preprocessed'),
        # My Own attempt at wordreprs
        SPEED_BIO_50D_TAG: partial(_tsv_featurise, SPEED_BIO_50D_PATH,' ', 'SPEED', 'bio_50d'),
        # ClarkNE
        DAVID_TAG: _david_featurise,
        }
# Since the Brown clusters have sizes, we treat them specially
for brown_size in BROWN_CLUSTERS_BY_SIZE:
    F_FUNC_BY_F_SET[BROWN_TAG.format(brown_size)] = partial(_brown_featurise,
            BROWN_CLUSTERS_BY_SIZE, brown_size)
for brown_size in PUBMED_BROWN_CLUSTERS_BY_SIZE:
    F_FUNC_BY_F_SET[PUBMED_BROWN_TAG.format(brown_size)] = partial(
            _brown_featurise, PUBMED_BROWN_CLUSTERS_BY_SIZE, brown_size)
###

def _argparser():
    argparser = ArgumentParser()#XXX:
    argparser.add_argument('-f', '--features',
            choices=tuple(sorted(s for s in F_FUNC_BY_F_SET)),
            action='append')
    return argparser

def main(args):
    argp = _argparser().parse_args(args[1:])

    # TODO: Update the default to the best one we got after experiments
    # TODO: Adding a default has unforeseen consequences
    assert argp.features

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
        for f_set in argp.features:
            for f_name, f_val in F_FUNC_BY_F_SET[f_set](nodes, graph, focus):
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
