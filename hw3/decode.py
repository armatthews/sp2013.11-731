#!/usr/bin/env python
import argparse
import sys
import models
import heapq
import time
from collections import namedtuple, defaultdict

def abbreviate( word ):
	if len( word ) < 7:
		return word
	else:
		return word.decode('utf-8')[ : 6 ].encode('utf-8') + '.'

def print_table( f, table, key=lambda k: k ):
	sys.stdout.write( "From\\To\t" )
	for i in range( len( f ) ):
		sys.stdout.write( "%s\t" % abbreviate( f[ i ] ) )
	print
	for i in range( len( f ) ):
		sys.stdout.write( "%s\t" % abbreviate( f[ i ] ) )
		for j in range( 1, len( f ) + 1 ):
			if j > i:
				sys.stdout.write( "%0.2f\t" % key( table[ i , j ] ) )
			else:
				sys.stdout.write( "    \t" )
		print

def calc_phrase_lm_score( phrase, start, end ):
	score = 0.0
	state = tuple() if not start else lm.begin()
	for word in phrase:
		state, word_score = lm.score( state, word )
		score += word_score
	if end:
		score += lm.end( state )
	return score

		
def extract_english_recursive(h):
	return '' if h.predecessor is None else '%s%s ' % (extract_english_recursive(h.predecessor), h.phrase.english)

def get_best(score_element):
	best = heapq.nlargest(1, score_element, key = lambda s: s.tm_score + s.lm_score)
	if len(best) == 0:
		return score_table_entry("", float("-inf"), float("-inf"))
	else:
		return best[0]

parser = argparse.ArgumentParser(description='Simple phrase based decoder.')
parser.add_argument('-i', '--input', dest='input', default='data/input', help='File containing sentences to translate (default=data/input)')
parser.add_argument('-t', '--translation-model', dest='tm', default='data/tm', help='File containing translation model (default=data/tm)')
parser.add_argument('-s', '--stack-size', dest='s', default=1, type=int, help='Maximum stack size (default=1)')
parser.add_argument('-n', '--num_sentences', dest='num_sents', default=sys.maxint, type=int, help='Number of sentences to decode (default=no limit)')
parser.add_argument('-l', '--language-model', dest='lm', default='data/lm', help='File containing ARPA-format language model (default=data/lm)')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,  help='Verbose mode (default=off)')
opts = parser.parse_args()

tm = models.TM(opts.tm, sys.maxint)
lm = models.LM(opts.lm)
sys.stderr.write('Decoding %s...\n' % (opts.input,))

start_time = time.time()
input_stream = open(opts.input) if opts.input != "-" else sys.stdin
input_sents = [tuple(line.strip().split()) for line in input_stream.readlines()[:opts.num_sents]]

hypothesis = namedtuple('hypothesis', 'logprob, lm_state, predecessor, phrase, coverage, prevj')
score_table_entry = namedtuple('score_table_entry', 'translation, tm_score, lm_score')
for f in input_sents:
	# tm_scores[ i, j ] holds the best possible TM score for the span f[i:j]
	scores = {}

	for i in range(len( f )):
		for j in range(i + 1, len( f ) + 1):
			scores[i,j] = []

			phrase = f[i : j]
			if phrase not in tm:
				continue

			for phrase in tm[phrase]:
				lm_score = calc_phrase_lm_score( phrase.english.split(), i == 0, j == len( f ) )
				heapq.heappush(scores[i, j], score_table_entry(phrase.english.split(), phrase.logprob, lm_score))
			scores[i, j] = heapq.nlargest(opts.s, scores[i,j], key=lambda s: s.tm_score + s.lm_score)

	#print_table( f, scores, lambda s: get_best(s).lm_score + get_best(s).tm_score )

	for n in range( 1, len( f ) + 1 ):
		for i in range( 0, len( f ) + 1 - n ):
			j = i + n
			for k in range( i + 1 , j ):
				for lhs in scores[i,k]:
					for rhs in scores[k,j]:
						translation = lhs.translation + rhs.translation
						lm_score = calc_phrase_lm_score( translation, i == 0, j == len( f ) )
						heapq.heappush(scores[i, j], score_table_entry(translation, lhs.tm_score + rhs.tm_score, lm_score))

						translation = rhs.translation + lhs.translation
						lm_score = calc_phrase_lm_score( translation, i == 0, j == len( f ) )
						heapq.heappush(scores[i, j], score_table_entry(translation, lhs.tm_score + rhs.tm_score,  lm_score))

				scores[i, j] = heapq.nlargest(opts.s, scores[i,j], key=lambda s: s.tm_score + s.lm_score)

	#print_table( f, scores, lambda s: get_best(s).lm_score + get_best(s).tm_score )
	
	best = heapq.heappop( scores[0, len(f)] )
	print " ".join( best.translation )
	if opts.verbose:
		print >>sys.stderr, "LM Score:", best.lm_score, "TM Score:", best.tm_score
print >>sys.stderr, "Took %g seconds." % (time.time() - start_time)
