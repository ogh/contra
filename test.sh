#!/bin/sh

# Run a few tests over feature sets and what-not.
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-05-29

# Exit on error
set -e

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

#for TRAIN_SET in conts.strat conts
for TRAIN_SET in conts.strat
do
    for F_SETS in 'comp pubmed_brown-150' 'comp pubmed_brown-500' \
        'comp pubmed_brown-1000' 'comp google' 'comp david' comp bow
    do
        # To be safe, erase any existing generated features
        rm -f ${TRAIN_FEATS} ${DEV_FEATS}

        # Generate the feature set arguments
        F_ARGS=''
        for F_SET in ${F_SETS}
        do
            F_ARGS="${F_ARGS} -f ${F_SET}"
        done

        # Featurise for this feature
        cat res/data/full/train.${TRAIN_SET} | ./featurise.py ${F_ARGS} \
            > ${TRAIN_FEATS}
        cat res/data/full/dev.conts.strat | ./featurise.py ${F_ARGS} \
            > ${DEV_FEATS}

        # Vectorise
        cat ${TRAIN_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
            ${FID_TO_FNAME_PICKLE} > ${TRAIN_VECS}
        cat ${DEV_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
            ${FID_TO_FNAME_PICKLE} > ${DEV_VECS}

        # Train
        ./optimisec.py -j 16 -p accuracy ${TRAIN_VECS} ${MODEL}

        # Evaluate
        echo "Features: '${F_SETS}' on '${TRAIN_SET}'"
        ext/liblinear/predict ${DEV_VECS} ${MODEL} ${PREDS}
    done
done
