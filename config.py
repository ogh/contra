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

PUBMED_BROWN_CLUSTERS_DIR = path_join(CLUSTERS_DIR, 'pubmed_brown')
PUBMED_BROWN_CLUSTERS_FNAME_TEMPLATE = 'PubMed-random-100K-c{0}-paths'
PUBMED_BROWN_CLUSTERS_BY_SIZE = {}
for size in (100, 320, 1000, 3200, ):
    PUBMED_BROWN_CLUSTERS_BY_SIZE[size] = path_join(PUBMED_BROWN_CLUSTERS_DIR,
            PUBMED_BROWN_CLUSTERS_FNAME_TEMPLATE.format(size))

PHRASE_CLUSTERS_PATH = path_join(CLUSTERS_DIR,
        'google/phraseClusters.toks.txt')

DAVID_CLUSTERS_PATH = path_join(CLUSTERS_DIR,
        'david/pubmed_abstract_corpus_big.clusters.45')

#### HLBL ####        

HLBL_BIO_PUBMED_100K_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-100k.txt')
        
HLBL_BIO_PUBMED_500K_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-500k.txt')
        
HLBL_BIO_PUBMED_100K_MINMAXCOL_NORM_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-100k-normalized-minmaxcol.txt')
        
HLBL_BIO_PUBMED_500K_MINMAXCOL_NORM_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-500k-normalized-minmaxcol.txt')
        
HLBL_BIO_PUBMED_100K_VECLENGTH_NORM_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-100k-normalized-veclength.txt')
        
HLBL_BIO_PUBMED_500K_VECLENGTH_NORM_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl-pubmed-500k-normalized-veclength.txt')
        
HLBL_NEWS_100D_PATH = path_join(CLUSTERS_DIR,
        'hlbl/hlbl_reps_clean_1.rcv1.clean.tokenized-CoNLL03.case-intact.txt')
        
#### LSPACE ####  
        
LSPACE_BIO_170D_PATH = path_join(CLUSTERS_DIR,
        'lspace/lspace-pubmed-170d.txt')
        
LSPACE_BIO_170D_PROB_PATH = path_join(CLUSTERS_DIR,
        'lspace/lspace-pubmed-170d-prob.txt')

LSPACE_BIO_170D_EXACT_PATH = path_join(CLUSTERS_DIR,
        'lspace/lspace-pubmed-170d-exact.txt')
        
LSPACE_BIO_PREPRO_PATH = path_join(CLUSTERS_DIR,
        'lspace/lspace-preprocessed.txt')
        
#### My Own attempt at quick-inducible wordreprs ####  
        
SPEED_BIO_50D_PATH = path_join(CLUSTERS_DIR,
        'speed/speed-pubmed-500k-50d.txt')
        