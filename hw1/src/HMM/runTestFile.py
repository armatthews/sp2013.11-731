import pickle
import sys
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

        SourceSentences = open( SourceSentenceFile ).read().split( "\n" )
        TargetSentences = open( TargetSentenceFile ).read().split( "\n" )

        print >>sys.stderr, "Loading model..."
        Model = pickle.load( open( ModelFile, "r" ) )

        print >>sys.stderr, "Finding optimal alignments for test set..."
        for ( SourceSentence, TargetSentence ) in zip( SourceSentences, TargetSentences ):
                SourceWords = SourceSentence.strip().split()
                TargetWords = TargetSentence.strip().split()

		if len( SourceWords ) == 0 or len( TargetWords ) == 0:
			continue

                #SourceWordsWithNull = [ "NULL" ] + SourceWords
                SourceWordsWithNull = SourceWords

                Alignment, Probability = Model.GetBestAlignment( SourceWordsWithNull, TargetWords )
                AlignmentOutput = [ (j,i) for i,j in enumerate( Alignment ) ]
                print " ".join( [ "%d-%d" % (i,j) for (i,j) in AlignmentOutput ] )
	print >>sys.stderr, "Done!"
