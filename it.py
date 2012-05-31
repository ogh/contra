#!/usr/bin/env python

'''
Iterators for fun and profit.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-05-30
'''

from itertools import izip, tee

# From the itertools recipies, pretty much
def ngroup(it, n):
    args = [iter(it)] * n
    return izip(*args)

# Generalised pairwise from itertools recipies
def nwise(it, n):
    assert n > 1 
    its = [it]
    for _ in xrange(1, n):
        prev_it = its.pop()
        new_prev_it, next_it = tee(prev_it)
        next(next_it, None)
        its.extend((new_prev_it, next_it, ))
    return izip(*its)

if __name__ == '__main__':
    print '2-Wise:', '({})'.format(', '.join('({})'.format(
        ', '.join(str(e) for e in t)) for t in nwise(xrange(10), 2)))
    print '3-Wise:', '({})'.format(', '.join('({})'.format(
        ', '.join(str(e) for e in t)) for t in nwise(xrange(10), 3)))
    print '2-Group:', '({})'.format(', '.join('({})'.format(
        ', '.join(str(e) for e in t)) for t in ngroup(xrange(10), 2)))
    print '3-Group:', '({})'.format(', '.join('({})'.format(
        ', '.join(str(e) for e in t)) for t in ngroup(xrange(10), 3)))
