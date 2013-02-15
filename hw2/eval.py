import sys

Alpha = 0.85 # 0.65 was tuned best
Beta = 0.2
Gamma = 0.6

def Precision( Hyp, Ref ):
	return 1.0 * len( [ Word for Word in Hyp if Word in Ref ] ) / len( Hyp )

def Recall( Hyp, Ref ):
	return 1.0 * len( [ Word for Word in Hyp if Word in Ref ] ) / len( Ref )

def FScore( Hyp, Ref, Alpha=0.5 ):
	P = Precision( Hyp, Ref )
	R = Recall( Hyp, Ref )
	if P == 0.0 and R == 0.0:
		return 0.0
	return P * R / ( ( 1 - Alpha ) * R + Alpha * P )

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
	WordMatches = len( [ Word for Word in Hyp if Word in Ref ] )
	return 1.0 * Chunks / WordMatches if WordMatches is not 0 else 0.0

def Meteor( Hyp, Ref, Alpha=0.5, Beta=1.0, Gamma=1.0 ):
	Frag = Fragmentation( Hyp, Ref )
	FragPenalty = Gamma * Frag ** Beta
	return FScore( Hyp, Ref, Alpha ) * ( 1.0 - FragPenalty )

for Line in sys.stdin:
	Parts = [ Part.strip() for Part in Line.strip().split( "|||" ) ]
	HypA, HypB, Ref = [ Part.split() for Part in Parts ]
	ScoreA = Meteor( HypA, Ref, Alpha, Beta, Gamma )
	ScoreB = Meteor( HypB, Ref, Alpha, Beta, Gamma )
	if ScoreA > ScoreB:
		print -1
	elif ScoreA == ScoreB:
		print 0
	else: 
		print 1
