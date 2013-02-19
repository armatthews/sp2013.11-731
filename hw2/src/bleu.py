import math
from collections import defaultdict
from util import ReadData

class BLEUStats:
	def __init__( self, Attempts, Matches, RefLength ):
		self.Attempts = Attempts
		self.Matches = Matches
		self.RefLength = RefLength

def stats( Hyp, Ref, N ):
	RefNGrams = defaultdict(int)
	for Order in range( 1, N + 1 ):
		for i in range( len( Ref ) - Order + 1 ):
			Toks = tuple( Ref[ i : i + Order ] )
			RefNGrams[ Toks ] += 1

	Attempts = [ 0 for i in range( N + 1 ) ]
	Matches = [ 0 for i in range( N + 1 ) ]
	for Order in range( 1, N + 1 ):
		for i in range( len( Hyp ) - Order + 1 ):
			Toks = tuple( Hyp[ i : i + Order ] )
			Found = RefNGrams[ Toks ] > 0
			Attempts[ Order ] += 1
			if Found:
				Matches[ Order ] += 1
				RefNGrams[ Toks ] -= 1

	return BLEUStats( Attempts, Matches, len( Ref ) )		

def score( Stats, N ):
	refWords = 1.0 * Stats.RefLength
	hypWords = 1.0 * Stats.Attempts[ 1 ]
	if hypWords == 0.0:
		brevityPenalty = 0.0
	else:
		brevityPenalty = math.exp( 1.0 - refWords / hypWords ) if hypWords < refWords else 1.0

	Score = 0.0
	SmoothingFactor = 1.0

	for Order in range( 1, N + 1 ):
		Attempts = Stats.Attempts[ Order ]
		Matches = Stats.Matches[ Order ]
		if Attempts == 0:
			OrderScore = 0.0
		elif Matches == 0:
			SmoothingFactor *= 2
			SmoothedPrecision = 1.0 / ( SmoothingFactor * Attempts )
			OrderScore = math.log( SmoothedPrecision )
		else:
			Precision = 1.0 * Matches / Attempts
			OrderScore = math.log( Precision )	

		Weight = 1.0 / N
		Score += OrderScore * Weight
	
	Score = brevityPenalty * math.exp( Score )
	Score = min( Score, 1.0 )
	Score = max( Score, 0.0 )
	return Score

def Score( Hyp, Ref ):
	N = 4
	Stats = stats( Hyp, Ref, N )
	BLEU = score( Stats, N )
	return BLEU

if __name__ == "__main__":
	import sys
	for HypA, HypB, Ref in ReadData( sys.stdin ):
		Ref = " ".join( Ref )
		ScoreA = Score( HypA, Ref )
		ScoreB = Score( HypB, Ref )
		if ScoreA > ScoreB:
			print -1
		elif ScoreA == ScoreB:
			print 0
		else:
			print 1
