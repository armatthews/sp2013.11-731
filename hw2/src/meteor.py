from math import exp
from util import Overlap, FScore, ReadData

def CountChunks( Hyp, Ref ):
        Chunks = 0
        LastWordInRef = False
        for Word in Hyp:
                WordInRef = Word in Ref
                if WordInRef and not LastWordInRef:
                        Chunks += 1
                elif LastWordInRef and not WordInRef:
                        Chunks += 1
                LastWordInRef = WordInRef
        return Chunks

def Fragmentation( Hyp, Ref ):
        Chunks = CountChunks( Hyp, Ref )
        WordMatches = len( Overlap( Hyp, Ref, 1 ) )
        return 1.0 * Chunks / WordMatches if WordMatches is not 0 else 0.0

def Score( Hyp, Ref, Alpha=0.5, Beta=1.0, Gamma=1.0 ):
	Frag = Fragmentation( Hyp, Ref )
	FragPenalty = Gamma * Frag ** Beta
	return FScore( Hyp, Ref, 1, Alpha ) * ( 1.0 - FragPenalty )

if __name__ == "__main__":
	import sys

	Alpha = 0.85
	Beta = 0.2
	Gamma = 0.6
	Delta = 0.75

	for HypA, HypB, Ref in ReadData( sys.stdin ):
		ScoreA = Score( HypA, Ref, Alpha, Beta, Gamma )
		ScoreB = Score( HypB, Ref, Alpha, Beta, Gamma )
		print "%f\t%f" % ( ScoreA, ScoreB )
		sys.stdout.flush()
