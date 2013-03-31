#!/usr/bin/env python
import argparse
import sys
import math
import models

# Three little utility functions:
def coverage(sequence):
    # Generate a coverage for a sequence of indexes #
    # You can do things like:
    #   c1 | c2 to "add" coverages
    #   c1 & c2 will return 0 if c1 and c2 do NOT overlap
    #   c1 & c2 will be != 0 if c1 and c2 DO overlap
    return reduce(lambda x,y: x|y, map(lambda i: long(1) << i, sequence), 0)

def coverage2str(c, n, on='o', off='.'):
    # Generate a length-n string representation of coverage c #
    return '' if n==0 else (on if c&1==1 else off) + coverage2str(c>>1, n-1, on, off)

def logadd(x,y):
    # Addition in logspace: if x=log(a) and y=log(b), return log(a+b) #
    return x + math.log(1 + math.exp(y-x)) if y < x else y + math.log(1 + math.exp(x-y))

def grade_sentence(tm, lm, f, e):
    total_logprob = 0.0
    # compute p(e) under the LM
    lm_state = lm.begin()
    lm_logprob = 0.0
    for word in e + ("</s>",):
        (lm_state, word_logprob) = lm.score(lm_state, word)
        lm_logprob += word_logprob
    total_logprob += lm_logprob

    # alignments[i] is a list of all the phrases in f that could have
    # generated phrases starting at position i in e
    alignments = [[] for _ in e]
    for fi in xrange(len(f)):
        for fj in xrange(fi+1,len(f)+1):
            if f[fi:fj] in tm:
                for phrase in tm[f[fi:fj]]:
                    ephrase = tuple(phrase.english.split())
                    for ei in xrange(len(e)+1-len(ephrase)):
                        ej = ei+len(ephrase)
                        if ephrase == e[ei:ej]:
                            alignments[ei].append((ej, phrase.logprob, fi, fj))

    # Compute sum of probability of all possible alignments by dynamic programming.
    # To do this, recursively compute the sum over all possible alignments for each
    # each pair of English prefix (indexed by ei) and French coverage (indexed by 
    # coverage v), working upwards from the base case (ei=0, v=0) [i.e. forward chaining]. 
    # The final sum is the one obtained for the pair (ei=len(e), v=range(len(f))
    chart = [{} for _ in e] + [{}]
    chart[0][0] = 0.0
    for ei, sums in enumerate(chart[:-1]):
        for v in sums:
            for ej, logprob, fi, fj in alignments[ei]:
                if coverage(range(fi,fj)) & v == 0:
                    new_v = coverage(range(fi,fj)) | v
                    if new_v in chart[ej]:
                        chart[ej][new_v] = logadd(chart[ej][new_v], sums[v]+logprob)
                    else:
                        chart[ej][new_v] = sums[v]+logprob
    goal = coverage(range(len(f)))
    if goal in chart[len(e)]:
        total_logprob += chart[len(e)][goal]
        return total_logprob
    elif len(e) == 0:
        return float("-inf")
    else:
        raise Exception("ERROR: COULD NOT ALIGN SENTENCE PAIR:\n%s\n%s" % (f,e))

def grade_stream(tm, lm, french_sents, num_sents, stream):
	english_sents = [tuple(line.strip().split()) for line in stream]
	english_sents = english_sents[:num_sents] if num_sents != 0 else english_sents
	#assert len(french_sents) == len(english_sents), "ERROR: French and English files are not the same length! Only complete output can be graded!"
	grades = [ grade_sentence(tm, lm, f, e) for (f,e) in zip(french_sents, english_sents) ]
	return grades

parser = argparse.ArgumentParser(description='Compute unnormalized translation probability by marginalizing over alignments.')
parser.add_argument('-i', '--input', dest='input', default='data/input', help='File containing sentences to translate (default=data/input)')
parser.add_argument('-t', '--translation-model', dest='tm', default='data/tm', help='File containing translation model (default=data/tm)')
parser.add_argument('-l', '--language-model', dest='lm', default='data/lm', help='File containing ARPA-format language model (default=data/lm)')
parser.add_argument('-n', '--num-sents', dest='num_sents', default='0', help='The number of sentences to grade against, or 0 for all (default=0)')
parser.add_argument('-e', '--english', dest='english_files', default='output.txt', nargs='+', help='The English file(s) to be graded')
opts = parser.parse_args()

tm = models.TM(opts.tm,sys.maxint)
lm = models.LM(opts.lm)
num_sents = int(opts.num_sents)

french_sents = [tuple(line.strip().split()) for line in open(opts.input).readlines()]
french_sents = french_sents[:num_sents] if num_sents != 0 else french_sents

file_grades = {}
for file_name in opts.english_files:
	file_stream = open(file_name) if file_name != "-" else sys.stdin
	file_grades[file_name] = grade_stream(tm, lm, french_sents, num_sents, file_stream)
	total_logprob = sum(file_grades[file_name])
	sys.stderr.write("%s\t%f\n" % (file_name, total_logprob))

num_sents = max([len(grades) for grades in file_grades.itervalues()])
best_grades = {}
best_files = {}
for i in range(num_sents):
	choices = {}
	for file_name, grades in file_grades.iteritems():
		if len(grades) > i:
			choices[file_name] = grades[i]
	best_grades[i] = max(choices.values())
	best_files[i] = [file_name for file_name in file_grades.keys() if file_name in choices and choices[file_name] == best_grades[i]]

for i in range(num_sents):
	print "%d\t%s" % (i + 1, " ".join(best_files[i]))
print >>sys.stderr, "Combined score: %f" % sum(best_grades.values())

#total_logprob = sum(grade_stream(tm, lm, french_sents, num_sents, sys.stdin))
#sys.stdout.write("%f\n" % total_logprob)
