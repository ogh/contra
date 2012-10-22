'''
Readers and processing for various cluster formats.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-30
'''

from it import ngroup
from re import compile as re_compile

from sys import stderr

### Constants
DIGIT_REGEX = re_compile(r'\d')
###



# TODO: Naive, should not load it all into memory
class DavidReader(object):
    def __init__(self, lines):
        self._table = {}
        for line in lines:
            try:
                esc_token, cluster, _ = line.rsplit(' ', 2)
                from ptbesc import unescape
                token = unescape(esc_token)
                self._table[token] = cluster
            except ValueError:
                # a very small number of cases have four fields
                pass
        
    def __getitem__(self, val):
        return self._table[val.upper()]

# TODO: Naive, should not load it all into memory
class BrownReader(object):
    def __init__(self, lines):
        self._table = {}
        for line in lines:
            cluster, token, _ = line.split('\t')
            self._table[token] = cluster
        
    def __getitem__(self, val):
        return self._table[val]
        
class TsvReader(object):
    """
    This class reads a tab separated table file.
    The rows are assumed to be the word representations.
    The first column is supposed to contain the token, 
    the remaining columns contain the values (float) of the representation vector.
    All representation vectors have to be of the same length.
    """
    def __init__(self, lines, separator):
        self._table = {}
        # check whether all the lines have the same number of components
        nTokens = None
        for line in lines:
            tokens = line.split(separator)
            # Remove empty tokens 
            # (in some files there might be multiple whitespaces between the columns)
            tokens = filter(lambda x: x != "", tokens)
            if nTokens == None:
                nTokens = len(tokens)
            else:
                if nTokens != len(tokens):
                    print >> stderr, "Error: all the vectors in the tsv wordrepr file should have the same length"
            # Not really sparse actually, but using dict here to make it work with the rest of the tool
            sparse_vector = {}
            for i,val in enumerate(tokens[1:]):
                # Ignore empty lines
                if val == "":
                    continue
                # Fill the vector
                sparse_vector[i] = float(val)
            # Assign vector to word
            self._table[tokens[0]] = sparse_vector
        
    def __getitem__(self, val):
        return self._table[val]

# TODO: Naive, should not load it all into memory
class GoogleReader(object):
    def __init__(self, lines):
        self._table = {}
        for line in lines:
            token, tail = line.split('\t', 1)
            self._table[token] = dict((int(c), float(d))
                    for c, d in ngroup(tail.split('\t'), 2))

    def __getitem__(self, val):
        # When performing a look-up, map all digits to zero as was done during
        # construction of the clusters by Lin et al. (2010)
        return self._table[DIGIT_REGEX.sub('0', val)]
