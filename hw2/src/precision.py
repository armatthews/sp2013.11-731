from util import Precision, ReadData

if __name__ == "__main__":
	import sys

	N = int( sys.argv[ 1 ] )
	for HypA, HypB, Ref in ReadData( sys.stdin ):	
		ScoreA = Precision( HypA, Ref, N )
		ScoreB = Precision( HypB, Ref, N ) 
		print "%f\t%f" % ( ScoreA, ScoreB )
		sys.stdout.flush()
