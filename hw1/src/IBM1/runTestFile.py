import sys
import math
from collections import defaultdict

def LoadTM( InputFileName ):
        p = defaultdict( lambda: defaultdict( lambda: 0.0 ) )
        for Line in open( InputFileName, "r" ):
		Source, Target, Probability = Line.strip().split()
		Probability = float( Probability )
		p[ Target ][ Source ] = Probability
        return p

def GetBestAlignment( p, SourceWords, TargetWords ):
        Alignment = []
        Probability = 1.0
        for TargetWord in TargetWords:
                SourceProbs = [ p[ TargetWord ][ SourceWord ] for SourceWord in SourceWords ]
                Best = max( range( len( SourceProbs ) ), key=lambda k: SourceProbs[ k ] )
                Probability *= SourceProbs[ Best ]
                Alignment.append( Best )

        return ( Alignment, Probability )

if __name__ == "__main__":
	if len( sys.argv ) < 4:
		print >>sys.stderr, "Usage: python %s LexProbs Source Target" % sys.argv[ 0 ]
		print >>sys.stderr, "Where LexProbs is S2T"
		sys.exit( 1 )

        # Prepare arguments
        STLexProbsFile = sys.argv[ 1 ]
        SourceSentenceFile = sys.argv[ 2 ]
        TargetSentenceFile = sys.argv[ 3 ]

	SourceSentences = open( SourceSentenceFile ).read().split( "\n" )
	TargetSentences = open( TargetSentenceFile ).read().split( "\n" )

	print >>sys.stderr, "Loading model..."
        p = LoadTM( STLexProbsFile )

	print >>sys.stderr, "Finding optimal alignments for test set..."
	TestSetLogProb = 0.0
	for (SourceSentence, TargetSentence) in zip( SourceSentences, TargetSentences):
		SourceWords = SourceSentence.split()
		TargetWords = TargetSentence.split()
		SourceWordsWithNull = [ "NULL" ] + SourceWords
		#SourceWordsWithNull = SourceWords

		Alignment, Probability = GetBestAlignment( p, SourceWordsWithNull, TargetWords )
		TestSetLogProb += math.log( Probability )
		SourceOutput = " ".join( SourceWordsWithNull )
		TargetOutput = " ".join( TargetWords )
		AlignmentOutput = [ (j,i) for i,j in enumerate( Alignment ) ]
		print " ".join( [ "%d-%d" % (i - 1,j) for (i,j) in AlignmentOutput if i != 0 ] )

	print "Test set log prob:", TestSetLogProb
