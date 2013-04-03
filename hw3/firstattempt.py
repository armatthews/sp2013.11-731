#!/usr/bin/env python
import argparse
import sys
import models
import heapq
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

def calc_phrase_lm_score( phrase ):
	score = 0.0
	state = tuple()
	for word in phrase:
		state, word_score = lm.score( state, word )
		score += word_score
	return score

def calc_tm_table( f ):
	tm_scores = defaultdict( lambda: tm_table_entry( [], float( "-inf" ) ) )

	# The score of any null span translating as null is 0.0, i.e. probability 1
	for i in range( len( f ) + 1 ):
		tm_scores[ i, i ] = tm_table_entry( [], 0.0 )

	# If a span [i, j) is in the TM, include that score in the table
	for i in range( len( f ) + 1 ):
		for j in range( i + 1, len( f ) + 1 ):
			phrase = f[ i : j ]
			if phrase in tm:
				best_translation = max( tm[ phrase ], key=lambda t: t.logprob )
				tm_scores[ i, j ] = tm_table_entry( [ best_translation ], best_translation.logprob )

	# For any span [i, j), the score is the max of the sum of the score of [i, k) and [k, j) over all k.
	for n in range( 1, len( f ) + 1 ):
		for i in range( 0, len( f ) + 1 - n ):
			j = i + n	
			k = max( range( i, j ), key=lambda k: tm_scores[ i, k ].logprob + tm_scores[ k, j ].logprob )
			new_translation = tm_scores[ i, k ].translation_array + tm_scores[ k, j ].translation_array
			new_logprob = tm_scores[ i, k ].logprob + tm_scores[ k, j ].logprob
			tm_scores[ i, j ] = tm_table_entry( new_translation, new_logprob )

	return tm_scores

def calc_future_cost_table( f, tm_table ):
	table = {}
	for (i, j), v in tm_table.iteritems():
		table[(i,j)] = v.logprob + calc_phrase_lm_score( v.translation_array )
	return table

def find_uncovered_spans( coverage ):
	i = 0
	L = len( coverage )
	while i < L:
		if coverage[ i ]:
			i += 1
			continue

		j = i + 1
		while j < len( coverage ) and coverage[ j ] == False:
			j += 1
		yield ( i, j )
		i = j
		

def estimate_future_cost( h, future_costs ):
	cost = 0.0
	for span in find_uncovered_spans( h.coverage ):
		cost += future_costs[ span ]
	return cost
		
def extract_english_recursive(h):
	return '' if h.predecessor is None else '%s%s ' % (extract_english_recursive(h.predecessor), h.phrase.english)

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

input_stream = open(opts.input) if opts.input != "-" else sys.stdin
input_sents = [tuple(line.strip().split()) for line in input_stream.readlines()[:opts.num_sents]]

hypothesis = namedtuple('hypothesis', 'logprob, lm_state, predecessor, phrase, coverage, prevj')
tm_table_entry = namedtuple('tm_table_entry', 'translation_array, logprob')
for f in input_sents:
	tm_scores = calc_tm_table( f )
	future_costs = calc_future_cost_table( f, tm_scores )

	initial_hypothesis = hypothesis(0.0, lm.begin(), None, None, [False for w in f], 0)
	initial_key = (tuple(initial_hypothesis.coverage), initial_hypothesis.lm_state)
	stacks = [{} for _ in f] + [{}]
	stacks[0][initial_key] = initial_hypothesis

	for n, stack in enumerate(stacks[:-1]):
		# extend the top s hypotheses in the current stack
		for h in heapq.nlargest(opts.s, stack.itervalues(), key=lambda h: h.logprob + estimate_future_cost( h, future_costs )): # prune
			for i, maxj in find_uncovered_spans( h.coverage ):
				for j in range( i + 1, maxj + 1 ):
					if f[i:j] not in tm:
						continue
					for phrase in tm[f[i:j]]:
						logprob = h.logprob + phrase.logprob
						lm_state = h.lm_state
						for word in phrase.english.split():
							(lm_state, word_logprob) = lm.score(lm_state, word)
							logprob += word_logprob
						logprob += lm.end(lm_state) if j == len(f) else 0.0
						new_coverage = list( h.coverage )
						for k in range( i, j ):
							new_coverage[ k ] = True
						new_hypothesis = hypothesis(logprob, lm_state, h, phrase, new_coverage, j)
						stack_index = n + j - i
						new_key = (tuple(new_coverage), lm_state)
						if new_key not in stacks[stack_index] or stacks[stack_index][new_key].logprob < logprob: # second case is recombination	
							stacks[stack_index][new_key] = new_hypothesis

	# find best translation by looking at the best scoring hypothesis
	# on the last stack
	#for n, stack in enumerate(stacks):
	#	print "Stack %d" % n
	#	for h in heapq.nlargest(1, stack.itervalues(), key=lambda h: h.logprob + estimate_future_cost( h )):
	#		print "\t%-128s\t\t%s" % ( extract_english_recursive( h ), "".join( [ "*" if c else "-" for c in h.coverage ] ) )
	#	print
	winner = max(stacks[-1].itervalues(), key=lambda h: h.logprob)
	print extract_english_recursive(winner)

	if opts.verbose:
		def extract_tm_logprob(h):
			return 0.0 if h.predecessor is None else h.phrase.logprob + extract_tm_logprob(h.predecessor)
		tm_logprob = extract_tm_logprob(winner)
		sys.stderr.write('LM = %f, TM = %f, Total = %f\n' %
			(winner.logprob - tm_logprob, tm_logprob, winner.logprob))
	
