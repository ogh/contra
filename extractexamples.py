#!/usr/bin/env python

# Extracts examples of given strings with context in a TAB-separated
# field format from given text documents.

from __future__ import with_statement

import sys
import re
from os import path

options = None

def argparser():
    import argparse
    ap=argparse.ArgumentParser(description="Extract examples of given strings with context from given texts")
    ap.add_argument("-c", "--context", metavar="LEN", default="3", help="Context length (space-separated words)")
    ap.add_argument("-s", "--strings", metavar="STR:LABEL", default=None, help="Strings to search for and labels to assign (format STR:LABEL[,STR:LABEL ...])")
    ap.add_argument("-f", "--stringfile", metavar="FILE", default=None, help="File containing strings to search for and labels to assign (format STR<TAB>LABEL, one per line)")
    ap.add_argument("-b", "--boundary", metavar="REGEX", default=r'\b', help="Regex string defining token boundaries for search")
    ap.add_argument("-r", "--regex", default=False, action="store_true", help="Interpret input strings as regular expressions")
    ap.add_argument("-i", "--ignorecase", default=False, action="store_true", help="Ignore case in string matching")
    ap.add_argument("-v", "--verbose", default=False, action="store_true", help="Verbose output")
    ap.add_argument("file", metavar="FILE", nargs='+', help="Source file(s)")
    return ap

def string_to_regex(s):
    global options

    if options.ignorecase:
        regex_flags = re.IGNORECASE
    else:
        regex_flags = 0
    
    if not options.regex:
        exp = options.boundary + re.escape(s) + options.boundary
    else:
        exp = options.boundary + s + options.boundary

    return re.compile(exp, regex_flags)

def process(f, fn, str_re_lab):
    text = f.read().rstrip('\n')
    docid = path.basename(fn)

    assert '\t' not in text, "ERROR: source text (%s) contains tab!" % fn
    assert '\n' not in text, "ERROR: source text (%s) contains newline!" % fn

    for s, re, label in str_re_lab:
        for m in re.finditer(text):
            # get contexts
            left, right  = text[:m.start()], text[m.end():]
            lwords, rwords = left.split(' '), right.split(' ')
            # cut, compensating for cases where the nearest "token" is empty
            if len(lwords) != 0 and lwords[-1] == '':
                loff = options.context+1
            else:
                loff = options.context
            if len(rwords) != 0 and rwords[0] == '':
                roff = options.context+1
            else:
                roff = options.context
            left  = ' '.join(lwords[-loff:])
            right = ' '.join(rwords[:roff])
                        
            print "%s[%d:%d]\t%s\t%s\t%s\t%s" % (docid, m.start(), m.end(),
                                                 label,
                                                 left, m.group(), right)

def main(argv):
    global options

    options = argparser().parse_args(argv[1:])

    # argument sanity check
    if options.strings is None and options.stringfile is None:
        print >> sys.stderr, "Please give either \"-s\" or \"-f\" argument."
        return 1
    if options.strings is not None and options.stringfile is not None:
        print >> sys.stderr, "Please give either \"-s\" or \"-f\" argument, but not both."
        return 1
    try:
        options.context = int(options.context)
        assert options.context > 0
    except Exception:
        print >> sys.stderr, "Please give a positive integer for context length"
        return 1

    # determine strings to search for, store as (string, label) pairs
    if options.strings is not None:
        try:            
            strings = []
            for string_label in options.strings.split(","):
                s, l = string_label.split(":")
                strings.append((s, l))
        except ValueError:
            print >> sys.stderr, "Failed to parse \"%s\" as a comma-separated list of STRING:LABEL pairs" % options.strings
            return 1
    else:
        try:
            strings = []
            with open(options.stringfile, 'rU') as f:
                for line in f:
                    try:
                        line = line.rstrip('\n')
                        s, l = line.split("\t")
                        strings.append((s, l))
                    except ValueError:
                        print >> sys.stderr, "Failed to parse \"%s\" in %s as a TAB-separated STRING:LABEL pair"
                        return 1
        except IOError, e:
            print >> sys.stderr, e
            return 1

    # check string and label sanity
    if len(strings) == 0:
        print >> sys.stderr, "No strings to search for defined."
        return 1
    seen = {}
    for s, l in strings:
        if s.strip() == "":
            print >> sys.stderr, "Error: empty search string."
            return 1
        if l.strip() == "":
            print >> sys.stderr, "Error: empty label."
            return 1
        if s.strip() != s:
            print >> sys.stderr, "Warning: space in search string \"%s\"." % s
        if s in seen:
            print >> sys.stderr, "Warning: duplicate search string \"%s\"." % s
        seen[s] = True

    # create regular expressions for search
    str_re_lab = []
    for s, l in strings:
        try:
            str_re_lab.append((s, string_to_regex(s), l))
        except Exception:
            print >> sys.stderr, "Failed to compile \"%s\" as regular expression" % s
            return 1

    # primary processing
    for fn in options.file:
        try:
            with open(fn, 'rU') as f:
                process(f, fn, str_re_lab)
        except IOError, e:
            print >> sys.stderr, e
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
