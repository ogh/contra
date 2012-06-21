#!/usr/bin/env python

'''
Optimise the liblinear penalty parameter using cross-validation.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-26
'''

from argparse import ArgumentParser
from atexit import register as atexit_register
from collections import defaultdict, namedtuple
from itertools import izip_longest
from math import fsum
from os import remove
from random import sample
from shutil import move
from sys import stderr
from tempfile import NamedTemporaryFile

from lib.fixedseed import FixedSeed

### Constants
F_SCORE_LBL = 'f-score'
ACC_SCORE_LBL = 'accuracy'

ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('data')
ARGPARSER.add_argument('model')
ARGPARSER.add_argument('-f', '--folds', type=int, default=10)
ARGPARSER.add_argument('-j', '--jobs', type=int, default=1)
ARGPARSER.add_argument('-l', '--liblinear-train-cmd', default='train')
ARGPARSER.add_argument('-s', '--seed', type=int, default=0x5648765a)
ARGPARSER.add_argument('-v', '--verbose', action='store_true')
ARGPARSER.add_argument('-p', '--optimisation',
        choices=(ACC_SCORE_LBL, F_SCORE_LBL, ), default=F_SCORE_LBL)
# TODO: C ranges
# TODO: Model types for liblinear
NEG_LBL = 1
POS_LBL = 2
###

Model = namedtuple('Model', ('c', 'score', ))

def _f_score(gold_path, pred_path):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    with open(gold_path, 'r') as gold:
        with open(pred_path, 'r') as pred:
            for gold_val, pred_val in izip_longest(
                    (int(l.split(' ')[0]) for l in gold),
                    (int(l.rstrip('\n')) for l in pred)):
                assert gold_val is not None, 'gold shorter than pred data'
                assert pred_val is not None, 'pred shorter than gold data'

                # XXX: Not sure if these assumptions hold outside of eepura
                if gold_val == POS_LBL and pred_val == POS_LBL:
                    tp += 1
                elif gold_val == POS_LBL and pred_val == NEG_LBL:
                    fn += 1
                elif gold_val == NEG_LBL and pred_val == POS_LBL:
                    fp += 1
                elif gold_val == NEG_LBL and pred_val == NEG_LBL:
                    tn += 1
                else:
                    assert False, ('unknown label values, f-score only supports '
                            'binary classification')

    try:
        p = float(tp) / (tp + fp)
    except ZeroDivisionError:
        p = 0.0
    try:
        r = float(tp) / (tp + fn)
    except ZeroDivisionError:
        r = 0.0
    try:
        f = (2 * p * r) / (p + r)
    except ZeroDivisionError:
        f = 0.0

    return f

def _accuracy_score(gold_path, pred_path):
    tp = 0
    fp = 0
    with open(gold_path, 'r') as gold:
        with open(pred_path, 'r') as pred:
            for gold_val, pred_val in izip_longest(
                    (int(l.split(' ')[0]) for l in gold),
                    (int(l.rstrip('\n')) for l in pred)):
                assert gold_val is not None, 'gold shorter than pred data'
                assert pred_val is not None, 'pred shorter than gold data'

                if gold_val == pred_val:
                    tp += 1
                else:
                    fp += 1

    return tp / float(tp + fp)

SCORE_F_BY_LBL = {
        F_SCORE_LBL: _f_score,
        ACC_SCORE_LBL: _accuracy_score,
        }

def _fold_to_idx_mapping(data_len, k=10, seed=0x510f62ce):
    idx_pool = set(xrange(data_len + 1))
    idx_to_fold = {}
    with FixedSeed(seed):
        for fold in xrange(1, k + 1):
            if fold != k:
                fold_idxs = set(sample(idx_pool,
                    len(idx_pool) / (k + 1 - fold)))
                idx_pool = idx_pool - fold_idxs
            else:
                # Assign all remaining to this fold
                fold_idxs = idx_pool

            for fold_idx in fold_idxs:
                idx_to_fold[fold_idx] = fold
    return idx_to_fold

from subprocess import Popen
from shlex import split as shlex_split
from os.path import dirname

# XXX: TODO: Purge all bash usage!

def _train_model(c, train_path, model_path):
    train_cmd = ("'{0}/ext/liblinear/train"
            " -q -c {1} {2} {3}'").format(dirname(__file__), c, train_path,
                model_path)
    #print train_cmd
    train_p = Popen(
            shlex_split(train_cmd),
            shell=True, executable='/bin/bash') # XXX: Nasty bash path
    train_p.wait()

def _eval_fold_and_c(fold_path, train_paths, c,
        optimisation_target=F_SCORE_LBL):
    train_path = None
    model_path = None
    pred_path = None
    try:
        # XXX: Hack for now, liblinear doesn't like bash hacks, we could
        # really assemble these train files elsewhere instead
        with NamedTemporaryFile('w', delete=False) as train_file:
            for train_path in train_paths:
                with open(train_path, 'r') as train:
                    for line in train:
                        train_file.write(line)
            train_path = train_file.name

        with NamedTemporaryFile('w', delete=False) as model_file:
            model_path = model_file.name

        _train_model(c, train_path, model_path)

        with NamedTemporaryFile('w', delete=False) as pred_file:
            pred_path = pred_file.name

        pred_cmd = ("'{0}/ext/liblinear/predict"
                    " {1} {2} {3}'").format(dirname(__file__), fold_path,
                            model_path, pred_path)
        #print pred_cmd
        #raw_input()
        # liblinear won't shut-up...
        with open('/dev/null', 'w') as dev_null:
            pred_p = Popen(
                    shlex_split(pred_cmd),
                    shell=True, executable='/bin/bash', stdout=dev_null) # XXX: Nasty bash path
            pred_p.wait()

        score = SCORE_F_BY_LBL[optimisation_target](fold_path, pred_path)
        #print c, score
        #raw_input()
        return Model(c=c, score=score)
    finally:
        for path in (train_path, pred_path, model_path, ):
            if path is not None:
                remove(path)

def __eval_fold_and_c(args):
    return _eval_fold_and_c(*args)

def _find_optimal_model(data_path, folds=10, seed=0xc0236b36, pool=None,
        verbose=False, optimisation_target=F_SCORE_LBL):
    # Segment the data into folds
    # TODO: Could be a function
    fold_to_fold_fh = {}
    for fold in xrange(1, folds + 1):
        fold_to_fold_fh[fold] = NamedTemporaryFile('w', delete=False)
    @atexit_register
    def _fold_files_cleanup():
        for fh in fold_to_fold_fh.itervalues():
            remove(fh.name)
    
    with open(data_path, 'r') as data:
        for idx, _ in enumerate(_ for _ in data):
            pass
        try:
            data_len = idx
        except UnboundLocalError:
            assert False, 'no training data found'
    idx_to_fold = _fold_to_idx_mapping(data_len, k=folds, seed=seed)

    with open(data_path, 'r') as data:
        for idx, line in enumerate(data):
            fold_to_fold_fh[idx_to_fold[idx]].write(line)

    # Close all file-handles so that they are flushed to disc
    for fh in fold_to_fold_fh.itervalues():
        fh.close()
    fold_paths = [fh.name for fh in fold_to_fold_fh.itervalues()]
   
    # XXX: Hard-coded C;s
    #c_values = [2 ** c_pow for c_pow in xrange(17, -7, -2)]
    # tweaked after a bit of a look at curves for the "bow",
    # "comp" and "david" models.
    c_values = [2 ** c_pow for c_pow in xrange(5, -7, -1)]
    # Evaluate all C-values to find the optimal model
    def _eval_args():
        # Order motivated due to high c;s being likely to take longer, we thus
        #    want to ensure that they are started as early as possible
        for c_value in c_values:
            for fold_path in fold_paths:
                curr_fold = fold_path
                curr_train = [p for p in fold_paths if p != curr_fold]
                yield (curr_fold, curr_train, c_value, optimisation_target)

    if pool is not None:
        eval_results = pool.imap_unordered(__eval_fold_and_c, _eval_args())
    else:
        eval_results = (__eval_fold_and_c(a) for a in _eval_args())

    c_to_models = defaultdict(list)
    for model in eval_results:
        #print model
        c_to_models[model.c].append(model)

    # Summarise the models for each fold into a single "model"
    avg_models = []
    for c, models in c_to_models.iteritems():
        avg_score = fsum(m.score for m in models) / len(models)
        avg_models.append(Model(c=c, score=avg_score))
    if verbose:
        avg_models.sort(key=lambda x : x.c)
        for model in avg_models:
            print >> stderr, '{0}\t{1}'.format(model.c, model.score)
    avg_models.sort(key=lambda x : x.score)
    optimal_c = avg_models[-1].c
    if verbose:
        print >> stderr, 'Optimal C:', optimal_c

    # Small paranoid check
    if optimal_c == c_values[0] or optimal_c == c_values[-1]:
        print >> stderr, ('WARNING: Optimal C value {0} found on the boundary '
                'of tested values [{1}], we could potentially have missed '
                'the optimum').format(optimal_c,
                        ', '.join(str(c) for c in c_values[::-1]))
    return optimal_c

def train_optimal_model(model_path, data_path, folds=10, seed=0x994c00d8,
        pool=None, verbose=False, optimisation_target=F_SCORE_LBL):
    optimal_c = _find_optimal_model(data_path, folds=folds, seed=seed,
            pool=pool, verbose=verbose,
            optimisation_target=optimisation_target)
    _train_model(optimal_c, data_path, model_path)
    #print 'BEST C:', optimal_c
    # XXX: Train a new model on all the data!
    #move(best_model.path, model_path)

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    if argp.jobs > 1:
        from multiprocessing import Pool
        pool = Pool(argp.jobs)
    else:
        pool = None

    train_optimal_model(argp.model, argp.data, folds=argp.folds,
            seed=argp.seed, pool=pool, verbose=argp.verbose,
            optimisation_target=argp.optimisation)

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
