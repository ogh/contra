'''
Readers and processing for various cluster formats.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-30
'''

from it import ngroup
from re import compile as re_compile

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
