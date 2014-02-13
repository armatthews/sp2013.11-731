import pickle
import sys
import math
from HMM import TM, DefaultDictZero, Zero


if __name__ == "__main__":
        if len( sys.argv ) < 4:
                print >>sys.stderr, "Usage: python %s Model Source Target" % sys.argv[ 0 ]
                print >>sys.stderr, "Where Model is S2T"
                sys.exit( 1 )

        # Prepare arguments
        ModelFile = sys.argv[ 1 ]
        SourceSentenceFile = sys.argv[ 2 ]
        TargetSentenceFile = sys.argv[ 3 ]

        SourceSentences = open( SourceSentenceFile ).read().decode('utf-8').split( "\n" )
        TargetSentences = open( TargetSentenceFile ).read().decode('utf-8').split( "\n" )

        print >>sys.stderr, "Loading model..."
        Model = TM()
	Model.Input( open( ModelFile ) )

        print >>sys.stderr, "Finding optimal alignments for test set..."
	TestSetLogProb = 0.0
        for ( SourceSentence, TargetSentence ) in zip( SourceSentences, TargetSentences ):
                SourceWords = SourceSentence.strip().split()
                TargetWords = TargetSentence.strip().split()

		if len( SourceWords ) == 0 or len( TargetWords ) == 0:
			continue

                #SourceWordsWithNull = [ "NULL" ] + SourceWords
                SourceWordsWithNull = SourceWords

                Alignment, Probability = Model.GetBestAlignment( SourceWordsWithNull, TargetWords )
		LogProb = math.log( Probability ) if Probability != 0.0 else float( "-inf" )
		TestSetLogProb += LogProb
                AlignmentOutput = [ (j,i) for i,j in enumerate( Alignment ) ]
                AlignmentString =  " ".join( [ "%d-%d" % (i,j) for (i,j) in AlignmentOutput ] )
		print "\t".join( [ SourceSentence, TargetSentence, AlignmentString, str( LogProb ) ] ).encode('utf-8')
	print "Test set log prob:", TestSetLogProb
	print >>sys.stderr, "Done!"
