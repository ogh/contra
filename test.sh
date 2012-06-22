#!/bin/sh

# Run a few tests over feature sets and what-not.
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-05-29

# Exit on error
set -e

# TODO: Leave a "run-directory" in the work directory for later analysis

JOBS=64

WRK_DIR=wrk
TRAIN_FEATS=${WRK_DIR}/train.feats
DEV_FEATS=${WRK_DIR}/dev.feats
TRAIN_VECS=${WRK_DIR}/train.vecs
DEV_VECS=${WRK_DIR}/dev.vecs
MODEL=${WRK_DIR}/train.model
C_POW=${WRK_DIR}/opt_c_pow
PREDS=${WRK_DIR}/dev.preds
LEARNING=${WRK_DIR}/learning.tsv

CATID_TO_CATNAME_PICKLE=${WRK_DIR}/catid_to_catname.pickle
FID_TO_FNAME_PICKLE=${WRK_DIR}/fid_to_fname.pickle

for TRAIN_SET in conts
#for TRAIN_SET in conts.strat
do
    # Results for conts.strat:
    #
    # 'bow'
    # Accuracy = 63.7027% (2966/4656)
    # 'comp'
    # Accuracy = 64.4545% (3001/4656)
    #
    # 'comp brown-100'
    # Accuracy = 63.5309% (2958/4656)
    # 'comp brown-320'
    # Accuracy = 63.3591% (2950/4656)
    # 'comp brown-1000'
    # Accuracy = 63.2517% (2945/4656)
    # 'comp brown-3200'
    # Accuracy = 64.2397% (2991/4656)
    # 'comp brown-100 brown-320 brown-1000 brown-3200'
    # Accuracy = 62.1778% (2895/4656)
    # 'comp brown-100 brown-3200'
    # Accuracy = 63.445% (2954/4656)
    #
    # 'comp pubmed_brown-150'
    # Accuracy = 64.6263% (3009/4656)
    # 'comp pubmed_brown-500'
    # Accuracy = 65.1847% (3035/4656)
    # 'comp pubmed_brown-1000'
    # Accuracy = 66.4948% (3096/4656)
    # 'comp pubmed_brown-150 pubmed_brown-500'
    # Accuracy = 64.8411% (3019/4656)
    # 'comp pubmed_brown-150 pubmed_brown-1000'
    # Accuracy = 65.4854% (3049/4656)
    # 'comp pubmed_brown-500 pubmed_brown-1000'
    # Accuracy = 66.2801% (3086/4656)
    # 'comp pubmed_brown-150 pubmed_brown-500 pubmed_brown-1000'
    # Accuracy = 65.4639% (3048/4656)
    #
    # 'comp google'
    # Accuracy = 69.1366% (3219/4656)
    #
    # 'comp david'
    # Accuracy = 65.5069% (3050/4656)
    #
    # 'comp google david'
    # Accuracy = 69.0077% (3213/4656)
    # 'comp google pubmed_brown-150'
    # Accuracy = 68.1271% (3172/4656)
    # 'comp google pubmed_brown-1000'
    # Accuracy = 68.4493% (3187/4656)
    # 'comp google david pubmed_brown-150'
    # Accuracy = 67.4828% (3142/4656)
    # 'comp google david pubmed_brown-1000'
    # Accuracy = 68.7285% (3200/4656)
    # 'comp david pubmed_brown-150'
    # Accuracy = 64.4759% (3002/4656)
    # 'comp david pubmed_brown-500'
    # Accuracy = 66.1727% (3081/4656)
    # 'comp david pubmed_brown-1000'
    # Accuracy = 66.9459% (3117/4656)
    #
    # "Unlexicalised":
    # 'google'
    # Accuracy = 59.3428% (2763/4656)
    # 'david'
    # Accuracy = 42.2036% (1965/4656)
    # 'pubmed_brown-150'
    # Accuracy = 45.9192% (2138/4656)
    # 'pubmed_brown-500'
    # Accuracy = 56.9802% (2653/4656)
    # 'pubmed_brown-1000'
    # Accuracy = 60.5885% (2821/4656)
    # 'google david pubmed_brown-1000'
    # Accuracy = 65.2277% (3037/4656)
    # 'david pubmed_brown-150'
    # Accuracy = 52.7277% (2455/4656)
    # 'david pubmed_brown-500'
    # Accuracy = 63.4665% (2955/4656)
    # 'david pubmed_brown-1000'
    # Accuracy = 62.3711% (2904/4656)
    # 'david pubmed_brown-150 pubmed_brown-500'
    # Accuracy = 58.9991% (2747/4656)
    # 'david pubmed_brown-150 pubmed_brown-500 pubmed_brown-1000'
    # Accuracy = 62.5644% (2913/4656)
    # 'google pubmed_brown-1000'
    # Accuracy = 64.39% (2998/4656)
    # 'google david pubmed_brown-150 pubmed_brown-500 pubmed_brown-1000'
    # Accuracy = 64.433% (3000/4656)

    for F_SETS in \
        'comp david pubmed_brown-1000'
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
        ./optimisec.py -j ${JOBS} -p accuracy -c ${TRAIN_VECS} ${MODEL} \
            > ${C_POW}

        # Learning curve
        ./learning.py -j ${JOBS} -c `cat ${C_POW}` ${TRAIN_VECS} ${DEV_VECS} \
            > ${LEARNING}

        # Evaluate
        echo "Features: '${F_SETS}' on '${TRAIN_SET}'"
        ext/liblinear/predict ${DEV_VECS} ${MODEL} ${PREDS}
    done
done
