#!/usr/bin/env bash

# Run a few tests over feature sets and what-not.
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-05-29

### Configuration
# Maximum number of processes to use (you can enjoy quite a speed-up)
JOBS=4
# Note: Only set this one to true for the final experiments
USE_TEST=false
# Path to all data
# TODO: Should be separated into train, test and dev paths.
DATA_PATH=res/data/full
# Stratified on non-stratified
# TODO: Improve the functionality here
TRAIN_SET=conts.strat
# Models for the publication tables:
# 'bow'
# 'comp'
# 'comp brown-100'
# 'comp brown-320'
# 'comp brown-1000'
# 'comp brown-3200'
# 'comp pubmed_brown-100'
# 'comp pubmed_brown-320'
# 'comp pubmed_brown-1000'
# 'comp david'
# 'comp google'

# Models for the publication learning curves:
# 'comp'
# 'comp david pubmed_brown-1000'
# 'comp google'

# Feature set combinations to use for this run

# SETS_TO_RUN='comp
#     comp david pubmed_brown-1000
#     comp google
#     bow
#     comp brown-100
#     comp brown-320
#     comp brown-1000
#     comp brown-3200
#     comp pubmed_brown-100
#     comp pubmed_brown-320
#     comp pubmed_brown-1000
#     comp david
#     hlbl-pubmed-100k
#     hlbl-pubmed-500k
#     hlbl-pubmed-100k-minmaxcol-norm
#     hlbl-pubmed-500k-minmaxcol-norm
#     hlbl-pubmed-100k-veclength-norm
#     hlbl-pubmed-500k-veclength-norm
#     hlbl-news-100d
#     lspace-bio-170d
#     lspace-bio-170d-prob
#     lspace-bio-170d-exact
#     lspace-bio-preprocessed
#     speed-bio-50d

SETS_TO_RUN='comp google
comp pubmed_brown-100
comp david
comp hlbl-pubmed-100k'

###

# Exit on error
set -e

WRK_DIR=wrk
RESULTS_DIR=results
TRAIN_FEATS=${WRK_DIR}/train.feats
DEV_FEATS=${WRK_DIR}/dev.feats
TRAIN_VECS=${WRK_DIR}/train.vecs
DEV_VECS=${WRK_DIR}/dev.vecs
MODEL=${WRK_DIR}/train.model
C_POW=${WRK_DIR}/opt_c_pow
PREDS=${WRK_DIR}/dev.preds
ACC=${WRK_DIR}/accuracy
LEARNING=${WRK_DIR}/learning.tsv

CATID_TO_CATNAME_PICKLE=${WRK_DIR}/catid_to_catname.pickle
FID_TO_FNAME_PICKLE=${WRK_DIR}/fid_to_fname.pickle

mkdir -p ${WRK_DIR} ${RESULTS_DIR}

while read -r F_SETS
do
    # To be safe, erase any existing generated features
    rm -f ${TRAIN_FEATS} ${DEV_FEATS}

    # Generate the feature set arguments
    F_ARGS=''
    for F_SET in ${F_SETS}
    do
        F_ARGS="${F_ARGS} -f ${F_SET}"
    done

    if [ "${USE_TEST}" == 'true' ]
    then
        TRAIN_DATA=`eval echo ${DATA_PATH}/{train,dev}.${TRAIN_SET}`
        DEV_DATA=${DATA_PATH}/test.conts.strat
    else
        TRAIN_DATA=${DATA_PATH}/train.${TRAIN_SET}
        DEV_DATA=${DATA_PATH}/dev.conts.strat
    fi
    
    echo FSets ${F_SETS}
    echo Fargs ${F_ARGS}

    # Featurise for this feature
    cat ${TRAIN_DATA} | ./featurise.py ${F_ARGS} > ${TRAIN_FEATS}
    cat ${DEV_DATA} | ./featurise.py ${F_ARGS} > ${DEV_FEATS}

    # Vectorise
    cat ${TRAIN_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
        ${FID_TO_FNAME_PICKLE} > ${TRAIN_VECS}
    cat ${DEV_FEATS} | ./vectorise.py ${CATID_TO_CATNAME_PICKLE} \
        ${FID_TO_FNAME_PICKLE} > ${DEV_VECS}

    # Train
    ./optimisec.py -j ${JOBS} -p accuracy -c ${TRAIN_VECS} ${MODEL} \
        > ${C_POW}

    # Learning curve
    ./learning.py -j ${JOBS} -c `cat ${C_POW}` ${TRAIN_VECS} ${DEV_VECS} \
        > ${LEARNING}

    # Evaluate
    echo "Features: '${F_SETS}' trained on '${TRAIN_SET}'"
    ext/liblinear/predict ${DEV_VECS} ${MODEL} ${PREDS} > ${ACC}
    cat ${ACC}

    # Copy the results into the results directory
    FNAME=`echo ${F_SETS} | sed -e 's| |_|g'`
    cp ${LEARNING} ${RESULTS_DIR}/${FNAME}_learning.tsv
    cp ${ACC} ${RESULTS_DIR}/${FNAME}_accuracy
done <<< "${SETS_TO_RUN}"
