# Contra #

"Cont" is for context, we are as-of-yet undecided on the "ra" part and we are
in no way making a reference to [Iran-Contra][north_song]!

[north_song]: http://www.youtube.com/watch?v=lrW3K6e8Ju0

## Instructions ##

Run `make` to build all dependencies:

    make

If you want to replicate the experiments of Stenetorp et al. (2012) check
`res/data/README.md` for instructions on how to fetch it (it is available,
don't worry, no lawyers be here).

The word representations used can be found on [their own webpage][word_reprs],
their paths are configured in `config.py`.

Have a look at `test.sh` on how to use the various scripts, it is pretty
modular and \*nixy in nature.

[word_reprs]: http://wordreprs.nlplab.org/

## Citing ##

If you make use of this code and/or data for scientific research, please cite
the below publication:

    @inproceedings{stenetorp2012size,
    author      = {Stenetorp, Pontus and Soyer, Hubert and Pyysalo, Sampo
        and Ananiadou, Sophia and Chikayama, Takashi},
    title       = {Size (and Domain) Matters: Evaluating Semantic Word
        Space Representations for Biomedical Text},
    year        = {2012},
    booktitle   = {Proceedings of the 5th International Symposium on
        Semantic Mining in Biomedicine},
    }
