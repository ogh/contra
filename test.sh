#!/bin/sh

# Run a few tests over feature sets and what-not
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-05-29

# TODO: Use a work-dir
# XXX: Featurisation should be a part of the script

WRK_DIR=wrk
TRAIN_FEATS=${WRK_DIR}/train.feats
DEV_FEATS=${WRK_DIR}/dev.feats
TRAIN_VECS=${WRK_DIR}/train.vecs
DEV_VECS=${WRK_DIR}/dev.vecs
MODEL=${WRK_DIR}/train.model

CATID_TO_CATNAME_PICKLE=${WRK_DIR}/catid_to_catname.pickle
FID_TO_FNAME_PICKLE=${WRK_DIR}/fid_to_fname.pickle

for F_SET in BOW
do
    # Featurise
    cat res/data/full/train.conts.strat | ./featurise.py -f ${F_SET} \
        > ${TRAIN_FEATS}
    cat res/data/full/dev.conts.strat | ./featurise.py -f ${F_SET} \
        > ${DEV_FEATS}

    # Vectorise
    cat ${TRAIN_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
        ${FID_TO_FNAME_PICKLE} > ${TRAIN_VECS}
    cat ${DEV_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
        ${FID_TO_FNAME_PICKLE} > ${DEV_VECS}

    # Train
    ./optimisec.py -j 64 -p accuracy ${TRAIN_VECS} ${MODEL}

    # Evaluate
    ext/liblinear/predict ${DEV_VECS} ${MODEL} /dev/null
done
