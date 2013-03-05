import bleu
from util import ReadData

def Score( Hyp, Ref, N ):
	Hyp = " ".join( Hyp ) 
	Ref = " ".join( Ref )
        Stats = bleu.stats( Hyp, Ref, N )
        BLEU = bleu.score( Stats, N )
        return BLEU

if __name__ == "__main__":
        import sys
	N = int( sys.argv[ 1 ] )
        for HypA, HypB, Ref in ReadData( sys.stdin ):
                ScoreA = Score( HypA, Ref, N )
                ScoreB = Score( HypB, Ref, N )
		print "%f\t%f" % ( ScoreA, ScoreB )
		sys.stdout.flush()
