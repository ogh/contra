#!/bin/sh

# Run a few tests over feature sets and what-not.
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-05-29

# TODO: Leave a "run-directory" in the work directory for later analysis

WRK_DIR=wrk
TRAIN_FEATS=${WRK_DIR}/train.feats
DEV_FEATS=${WRK_DIR}/dev.feats
TRAIN_VECS=${WRK_DIR}/train.vecs
DEV_VECS=${WRK_DIR}/dev.vecs
MODEL=${WRK_DIR}/train.model
PREDS=${WRK_DIR}/dev.preds

CATID_TO_CATNAME_PICKLE=${WRK_DIR}/catid_to_catname.pickle
FID_TO_FNAME_PICKLE=${WRK_DIR}/fid_to_fname.pickle

for TRAIN_SET in conts.strat conts
do
    for F_SET in google comp brown bow
    do
        # Featurise
        cat res/data/full/train.${TRAIN_SET} | ./featurise.py -f ${F_SET} \
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
        echo ${F_SET} ${TRAIN_SET}
        ext/liblinear/predict ${DEV_VECS} ${MODEL} ${PREDS}
    done
done
