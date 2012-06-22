#!/usr/bin/env python

'''
Generate a learning curve through several samplings.

Note: Written while terribly tired, do some clean-up

Author:     Pontus Stenetorp
Version:    2012-06-03
'''

# TODO: Check if there is some established way of determining the number of samples per step
# TODO: Need to hack a somewhat generic framework for executing runs with a given: c, train, test

from argparse import ArgumentParser, FileType
from random import sample

from optimisec import _eval_fold_and_c, ACC_SCORE_LBL

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('train_vecs', type=FileType('r'))
ARGPARSER.add_argument('test_vecs')
ARGPARSER.add_argument('-c', '--c-pow', type=int, default=0)
ARGPARSER.add_argument('-j', '--jobs', type=int, default=1)
ARGPARSER.add_argument('-v', '--verbose', action='store_true')
###


class CachedLines(object):
    def __init__(self, file_handle):
        self._lines = [l for l in file_handle]

    def __len__(self):
        return len(self._lines)

    def sample(self, size):
        # TODO: Returning an iterator by Knuth's sampling algorithm would be a better choice
        return sample(self._lines, size)


from collections import namedtuple
from os import remove

# Sub-optimal name
FoldJob = namedtuple('FoldJob', ('cached_lines', 'fold_size', 'c_pow', 'test_path', ))

from tempfile import NamedTemporaryFile

def __eval_fold(cached_lines, fold_size, c_pow, test_path):
    train_file_path = None
    try:
        with NamedTemporaryFile('w', delete=False) as train_file:
            train_file_path = train_file.name
            for line in cached_lines.sample(fold_size):
                train_file.write(line)
        # XXX: We are really hacking into the old framework, not pretty
        res = _eval_fold_and_c(test_path, (train_file_path, ), 2 ** c_pow,
                optimisation_target=ACC_SCORE_LBL)
        return fold_size, res.score
    finally:
        if train_file_path is not None:
            remove(train_file_path)

def _eval_fold(args):
    return __eval_fold(*args)

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    cached_lines = CachedLines(argp.train_vecs)
    data_size = len(cached_lines)

    sample_sizes = (i / 100.0 for i in xrange(100, 0, -5))

    runs = []
    for sample_size in sample_sizes:
        fold_size = int(data_size * sample_size)
        # XXX: This heuristic badly needs some work
        if fold_size == data_size:
            folds = 1
        else:
            folds = data_size / fold_size * 3

        for _ in xrange(folds):
            runs.append(FoldJob(c_pow=argp.c_pow, fold_size=fold_size,
                cached_lines=cached_lines, test_path=argp.test_vecs))

    if argp.jobs > 1:
        from multiprocessing import Pool
        pool = Pool(argp.jobs)
    else:
        pool = None

    if pool is not None:
        results = pool.imap_unordered(_eval_fold, runs)
    else:
        results = (_eval_fold(run) for run in runs)

    from collections import defaultdict
    run_results = defaultdict(list)
    from sys import stderr
    for fold_size, score in results:
        #if argp.verbose:
        #    print >> stderr, fold_size, score
        run_results[fold_size].append(score)

    from math import fsum, sqrt
    from collections import OrderedDict
    curve = OrderedDict()
    for fold_size in sorted(s for s in run_results):
        f_results = run_results[fold_size]
        f_sum = fsum(f_results)
        f_mean = f_sum / len(f_results)
        f_stdev = sqrt(fsum((f_res - f_mean) ** 2 for f_res in f_results) / len(f_results))
        curve[fold_size] = (f_mean, f_stdev)
 
    # Output in tsv
    print 'Size\tMean\tStdev'
    for fold_size, fold_res in curve.iteritems():
        f_mean, f_stdev = fold_res
        print '{}\t{}\t{}'.format(fold_size, f_mean, f_stdev)

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
