import sys
from math import sqrt
from util import ReadData

def Score( Hyp, Ref ):
	return 1.0 - abs( 1.0 - 1.0 * len( Hyp ) / len( Ref ) )

for HypA, HypB, Ref in ReadData( sys.stdin ):
	ScoreA = Score( HypA, Ref )
	ScoreB = Score( HypB, Ref )
	print "%f\t%f" % ( ScoreA, ScoreB )
	sys.stdout.flush()
