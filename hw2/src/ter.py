from math import exp
from util import Overlap, FScore, ReadData

# Number of edits to turn Hyp into Ref
def EditDistance( Hyp, Ref ):
	I = len( Hyp )
	J = len( Ref )

	Table = [ [ 0 for j in range( J + 1 ) ] for i in range( I + 1 ) ]
	Path = [ [ None for j in range( J + 1 ) ] for i in range( I + 1 ) ]

	for i in range( I + 1 ):
		Table[ i ][ 0 ] = i
	for j in range( J + 1 ):
		Table[ 0 ][ j ] = j

	for i in range( 1, I + 1 ):
		for j in range( 1, J + 1 ):
			Match = ( Hyp[ i - 1 ] == Ref[ j - 1 ] )
			Options = []
			Options.append( ( Table[ i - 1 ][ j - 1 ], ( i - 1, j - 1 ) ) ) # Edit
			Options.append( ( Table[ i - 1 ][ j ], ( i - 1, j ) ) ) # Deletion
			Options.append( ( Table[ i ][ j - 1 ], ( i, j - 1 ) ) ) # Insertion
			Min = min( Options )
			Table[ i ][ j ] = Min[ 0 ]
			Path[ i ][ j ] = Min[ 1 ]
			if not Match:
				Table[ i ][ j ] += 1

	Matches = []
	i, j = I, J
	while i != 0 and j != 0:
		ip, jp = Path[ i ][ j ]
		if Hyp[ i - 1 ] == Ref[ j - 1 ]:
			#assert i - ip == 1
			#assert j - jp == 1
			Matches.append( ( i - 1, j - 1 ) )
		i, j = ip, jp

	Matches.reverse()

	return Table[ I ][ J ], Matches

def FindShiftSpans( Hyp, Ref, Matches ):
	MaxShiftSpanSize = 10
	I = len( Hyp )
	J = len( Ref )

	ShiftSpans = []
	for Start in range( I ):
		if len( [ 1 for Match in Matches if Match[ 0 ] == Start ] ) > 0:
			continue
		for End in range( Start, min( Start + MaxShiftSpanSize, I ) ):
			if len( [ 1 for Match in Matches if Match[ 0 ] == End ] ) > 0:
				break
			ShiftSpans.append( ( Start, End + 1 ) )
	return ShiftSpans

def FindBestShift( Hyp, Ref, Edits, Matches ):
	BestHyp = Hyp
	BestEdits = Edits

	ShiftSpans = FindShiftSpans( Hyp, Ref, Matches )
	for Start, End in ShiftSpans:
		HypPrimeBase = Hyp[ : Start ] + Hyp[ End : ]
		Insert = Hyp[ Start : End ]
		print "".join( Insert )
		print "".join( HypPrimeBase )
		for i in range( len( HypPrimeBase ) + 1 ):
			if i == Start:
				continue
			HypPrime = HypPrimeBase[ : i ] + Insert + HypPrimeBase[ i : ]
			Edits, _ = EditDistance( HypPrime, Ref )
			Edits += 1 # Add one for the shift
			if Edits < BestEdits:
				BestHyp = HypPrime
				BestEdits = Edits
			print "\t", "".join( HypPrime ), Edits
	return BestHyp, BestEdits

def Score( Hyp, Ref ):
	Edits, Matches = EditDistance( Hyp, Ref )
	while False:
		NewHyp, Edits = FindBestShift( Hyp, Ref, Edits, Matches )
		if Hyp == NewHyp:
			break
		else:
			Hyp = NewHyp
	
	return 1.0 - 1.0 * Edits / len( Ref )

if __name__ == "__main__":
	import sys

	for HypA, HypB, Ref in ReadData( sys.stdin ):
		ScoreA = Score( HypA, Ref )
		ScoreB = Score( HypB, Ref )
		print "%f\t%f" % (ScoreA, ScoreB )
		sys.stdout.flush()
