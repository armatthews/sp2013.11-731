from collections import defaultdict
from operator import itemgetter
from math import exp
#from scipy.special import digamma
import sys
import pickle
import os

# IO Functions
# Data files are simply one sentence per line.
def ReadDataFile( FileName ):
        Data = []
        for Line in open( FileName, "r" ):
                Line = Line.strip()
                Data.append( Line.split() )
        return Data

def ReadInData( SourceDataFile, TargetDataFile ):
	SourceData = ReadDataFile( SourceDataFile )
	TargetData = ReadDataFile( TargetDataFile )
	Data = zip( SourceData, TargetData )
	return Data

def Output( p, File ):
	Epsilon = 0.0
	for TargetWord in sorted( p.keys() ):
		for SourceWord, Probability in p[ TargetWord ].iteritems():
			if Probability < Epsilon:
				continue
			File.write( "%s %s %f\n" % ( SourceWord, TargetWord, Probability ) )

# Helper Functions
def Normalize( p ):
	for TargetWord in p.keys():
		Total = 0.0
		for SourceWord in p[ TargetWord ].keys():
			Total += p[ TargetWord ][ SourceWord ]
		for SourceWord in p[ TargetWord ].keys():
			p[ TargetWord ][ SourceWord ] /= Total
	return p

# Initialize uniformly
# To do this we set every entry in p[ t ][ s ] to 1
# and then normalize at the end
def InitializeUniformly( Data ):
	p = defaultdict( lambda: defaultdict( lambda: 0.0 ) )

	for SourceSentence, TargetSentence in Data:
		for TargetWord in TargetSentence:
			for SourceWord in SourceSentence:
				p[ TargetWord ][ SourceWord ] = 1.0
			p[ TargetWord ][ "NULL" ] = 0.01
	p = Normalize( p )
	return p

# Performs one (psuedo-)EM iteration, creating a (hopefully) better
# table of translation probabilities.
# The algorithm here involves a few tricks to optimize, but the idea is as follows:
# Let S and T be the source and target sentences
# Let s and t represent words in the source and target sentences
# p(t|s) = p(t,s) / p(s)
# To estimate these two probabilites, we introduce the concept of an alignment.
# An alignment is a mapping wherein every target word t maps to a single source word s, or to the NULL word.
# We will assume that S_i represents the ith word in the source, with S_0 = NULL.
# As such, an alignment can be thought of as a vector with one entry for each target word,
# and each entry representing one source word, but several target words may map to the same source word.

# The IBM Model 1 defines p(a,T|S) = PRODUCT( j, 1, |T| )[ p( T_j | S_(a_j) )
# to estimate p(t,s) we will loop over our entire corpus, and count the number of t-s pairings, weighted
# by the probability of each alignment containing such a pair. That is:
# p(t,s) = SUM( (T,S) in Corpus )[ SUM( a in A )[ p( a | T, S ) * Count( t-s links in a ) ] ]
# where A represents the set of all possible alignments for the sentence pair (T,S).

# To model p(s) we will loop over our entire corpus, and count how many times s aligns to anything, weighted
# by the probability of each alignment containg a link from s to anything. That is:
# p(s) = SUM( (T,S) in Corpus )[ SUM( a in A )[ p( a | T, S ) * Count( s-* links in a ) ] ]

# Now, to find p(a|T,S) we will use p(a|T,S) = p(a,T|S) / p(T|S)
# p(a,T|S) is defined by IBM Model 1 as above.
# To compute p(T|S) we use p(T|S) = SUM( a in A )[ p( a, T | S ) ]
# = SUM( a in A )[ PRODUCT( j, 1, |T| )[ p( T_j, S_(a_j) ) ] ]

# Now we use a trick. Since this loops over all possible mappings, we can factor it.
# Consider mapping the sentence 0ab to the sentence xy.
# We have nine possible alignments:
# 00 0a 0b a0 aa ab b0 ba bb
# Summing over them would give:
# p(0|x)*p(0|y) + p(0|x)*p(a|y) + p(0|x)*p(b|y) + p(a|x)*p(0|y) + p(a|x)*p(a|y) + p(a|x)*p(b|y) + p(b|x)*p(0|y) + p(b|x)*p(a|y) + p(b|x)*p(b|y)
# Now it's clear we can factor this: p(0|x) * [ p(0|y) + p(a|y) + p(b|y) ] + p(a|x) * [ p(0|y) + p(a|y) + p(b|y) ] + p(b|x) * [ p(0|y) + p(a|y) + p(b|y) ]
# And we can factor this again: [ p(0|x) + p(a|x) + p(b|x) ] * [ p(0|y) + p(a|y) + p(b|y) ]
# and we've changed our sum of products into a product of sums.
# This we can write p(T|S) = SUM( a in A ) p(a,T|S) = PRODUCT(j,1,|T|)[ SUM(i,0,|S|)[ p(T_j | S_i) ] ]

# Now we may write
# p(a|T,S) = p(a,T|S) / p(T/S) = PRODUCT(j,1,|T|)[ p(T_j|S_(a_j)) ] / PRODUCT(j,1,|T|)[ SUM(i,0,|S|)[ p(T_j|S_i) ] ]
# = PRODUCT(j,1,|T|)[ p(T_j|S_(a_j)) / SUM(i,0,|S|)[ p(T_j|S_i) ] ]

# Now we can combine these two parts to get p(a|T,S) = PRODUCT(j,1,|T|)[ p(T_j|S_(a_j)) / SUM(i,0,|S|)[ p(T_j|S_i) ] ]
# So now we may write that for a given sentence pair T,S, count(t|s;T,S) = SUM(a in A)[ p(a|T,S) * SUM(j,1,|T|)[ d(t,T_j) * d(s, S_(a_j)) ] ]
# Where d is the delta function, equal to 1 if the arguments are equal and 0 otherwise.
# Note that the sum over the product of the two delta functions is a formal way of saying Count( t-s links in a ).

# Plugging in what we had for p(a|T,S), we find count(t|s;S,T) = SUM(a in A)[ PRODUCT(j,1,|T|)[ p(T_j|S_(a_j)) / SUM(i,0,|S|)[ p(T_j|S_i) ] ] * SUM(j,1,|T|)[ d(t,T_j) * d(s,S_(a_j)) ] ]
# Next we will use a trick similar to the last one we used. We know that we can factor the sum of a in A as, using the same notation as the above example:
# [ p(0|x) + p(a|x) + p(b|x) ] * [ p(0|y) + p(a|y) + p(b|y) ]. Notice that the sum over j in [1,|T|] means that any alignment not containing a s-t link is given 0 weight.
# Suppose we're interested in alignments between a and x. In the factored version, the delta function has the effect of zeroing all non-(a-x) terms in the same factor as p(a|x).
# In the example, this would reduce to [ 0 + p(a|x) + 0 ] * [ p(0|y) + p(a|y) + p(b|y) ].
# Note that in the event that there were multiple a's or x's in the sentence pair, count(a)*count(x) terms would remain in that factor.

# With this simplification we now have count(t|s;S,T) = [ p(t|s) / SUM(i,0,|S|) p(t|S_i) ] * count(a) * count(x).
# Finally, p(t|s;Corpus) = SUM( (S,T) in Corpus )[ count(t|s;S,T) ] / SUM(s)[ SUM( (T,S) in Corpus)[ count(t|s;T,S) ] ] where the sum over s is over all source word in the corpus.

def h( i, j, m, n ):
	return -abs( 1.0 * i / m - 1.0 * j / n )

def Prior( i, j, m, n ):
	return 1.0
	l = 6.37607551
	return exp( l * h( i, j, m, n ) )

def Smooth( c ):
	return c
	#return exp( digamma( c + 0.5 ) )

def Iterate( p, Data ):
	q = defaultdict( lambda: defaultdict( lambda: 10 ** -15 ) )
	SourceCounts = defaultdict( lambda: 0.0 )
	JointCounts = defaultdict( lambda: defaultdict( lambda: 0.0 ) )

	for SentenceNum, SentencePair in enumerate( Data ):
		if SentenceNum % 1000 == 0:
			sys.stderr.write( "%d/%d sentences examined\r" % ( SentenceNum, len( Data ) ) )
			sys.stderr.flush()
		SourceSentence, TargetSentence = SentencePair
		SourceSentence = [ "NULL" ] + SourceSentence
		m = len( SourceSentence )
		n = len( TargetSentence )

		# TargetCounts[ t ] represents SUM( i, 0, S )[ p(t|S_i) ]
		TargetCounts = defaultdict( lambda: 0.0 )
	
		# Both JointCounts and SourceCounts are sums over the entire corpus.
		# Here we calculate the contribution of this sentence pair, and add it into those two variables.
		for j, TargetWord in enumerate( TargetSentence ):
			PriorSum = sum( [ Prior( i, j, m, n ) for i in range( len( SourceSentence ) ) ] )
			for i, SourceWord in enumerate( SourceSentence ):
				prior = Prior( i, j, m, n ) / PriorSum
				TargetCounts[ TargetWord ] += prior * p[ TargetWord ][ SourceWord ]
			for i, SourceWord in enumerate( SourceSentence ):
				prior = Prior( i, j, m, n ) / PriorSum
				Count = prior * p[ TargetWord ][ SourceWord ] / TargetCounts[ TargetWord ]
				JointCounts[ TargetWord ][ SourceWord ] += Count
				SourceCounts[ SourceWord ] += Count

	sys.stderr.write( "%d/%d sentences examined\n" % ( len( Data ), len( Data ) ) )
	sys.stderr.flush()
	
	print >>sys.stderr, "Collecting counts"
	for TargetWord in JointCounts.keys():
		for SourceWord in JointCounts[ TargetWord ].keys():
				q[ TargetWord ][ SourceWord ] = Smooth( JointCounts[ TargetWord ][ SourceWord ] ) / Smooth( SourceCounts[ SourceWord ] )

	print >>sys.stderr, "Normalizing counts"
	q = Normalize( q )
	return q

# Entry Point
if __name__ == "__main__":
	if len( sys.argv ) < 4:
		print >>sys.stdout, "Usage: python %s SourceFile TargetFile OutputDir [IterationCount]" % sys.argv[ 0 ]
		print >>sys.stdout, "If IterationCount is 0 or not specified, will run forever."
		exit( 1 )

	OutputDir = sys.argv[ 3 ]
	IterationCount = int( sys.argv[ 4 ] ) if len( sys.argv ) >= 5 else 0
	if not os.path.exists( OutputDir ):
		os.mkdir( OutputDir )

	print >>sys.stdout, "Reading in data..."
	Data = ReadInData( sys.argv[ 1 ], sys.argv[ 2 ] )

	print >>sys.stdout, "Initializing model..."
	p = InitializeUniformly( Data )
	Iteration = 0	

	print >>sys.stdout, "Outputting iteration #%d" % Iteration
	File = open( os.path.join( OutputDir, "Iteration%d.txt" % Iteration ), "w" )
	Output( p, File )
	File.close()
	Iteration += 1

	while Iteration <= IterationCount or IterationCount == 0:
		print >>sys.stderr, "Working on iteration #%d" % Iteration
		q = Iterate( p, Data )

		print >>sys.stderr, "Outputting interation #%d" % Iteration
		File = open( os.path.join( OutputDir, "Iteration%d.txt" % Iteration ), "w" )
		Output( q, File )
		File.close()

		p = q
		Iteration += 1
