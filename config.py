'''
Configuration, mostly for the location of various resources.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-30
'''

from os.path import join as path_join, dirname

ROOT_DIR = dirname(__file__)
CLUSTERS_DIR = path_join(ROOT_DIR, 'res/clusters')

TURIAN_DIR = path_join(CLUSTERS_DIR, 'turian_et_al_2010_clusters')

BROWN_CLUSTERS_DIR = path_join(TURIAN_DIR, 'brown-clusters-ACL2010')
BROWN_CLUSTERS_FNAME_TEMPLATE = 'brown-rcv1.clean.tokenized-CoNLL03.txt-c{0}-freq1.txt'
BROWN_CLUSTERS_BY_SIZE = {}
for size in (100, 320, 1000, 3200, ):
    BROWN_CLUSTERS_BY_SIZE[size] = path_join(BROWN_CLUSTERS_DIR,
            BROWN_CLUSTERS_FNAME_TEMPLATE.format(size))

PUBMED_BROWN_CLUSTERS_PATH = path_join(CLUSTERS_DIR,
        'pubmed_brown/PubMed-random-100K-c500-p1.out/paths')

PHRASE_CLUSTERS_PATH = path_join(CLUSTERS_DIR,
        'google/phraseClusters.toks.txt')

DAVID_CLUSTERS_PATH = path_join(CLUSTERS_DIR,
        'david/pubmed_abstract_corpus_big.clusters.45')
