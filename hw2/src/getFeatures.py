import sys
import meteor
import bleu
from math import exp
from util import Overlap, Precision, Recall, FScore, ReadData

def Features( Hyp, Ref, Alpha ):
	Features = []
	for n in range( 1, 2 ):	
		Features += [ ( "Precision %d" % n, Precision( Hyp, Ref, n ) ) ]
		Features += [ (    "Recall %d" % n, Recall( Hyp, Ref, n ) ) ]
		Features += [ (    "FScore %d" % n, FScore( Hyp, Ref, n, Alpha ) ) ]
		Features += [ (   "Overlap %d" % n, len( Overlap( Hyp, Ref, n ) ) ) ]
	Features += [ ( "Fragmentation", Fragmentation( Hyp, Ref ) ) ]
	Features += [ ( "Length Ratio", 1.0 * len( Hyp ) / len( Ref ) ) ]
	return Features

def Score( Features, Weights ):
	Score = 0.0
	for ( ( Name, Value ), Weight ) in zip( Features, Weights ):	
		Score += Value * Weight
	return Score

def Comp( A, B ):
	return A - B
	if A == B:
		return 0
	elif A > B:
		return 1
	else:
		return -1

for HypA, HypB, Ref in ReadData( sys.stdin ):
	FeaturesA = Features( HypA, Ref, Alpha )
	FeaturesB = Features( HypB, Ref, Alpha )
	#F = [ Comp( FeaturesA[ i ][ 1 ], FeaturesB[ i ][ 1 ] ) for i in range( len( FeaturesA ) ) ]
	F = [ f[ 1 ] for f in FeaturesA ] + [ f[ 1 ] for f in FeaturesB ]
	print " ".join( [ "%g" % Value for Value in F ] )
