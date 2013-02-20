import sys
from math import sqrt
from util import ReadData

def ssk( s, t, L, N ):
	kp = {}
	
	for i in range( N + 1 ):
		for j in range( len( s ) + 1 ):
			for k in range( len( t ) + 1 ):
				kp[ i, j, k ] = 0.0
	
	for j in range( len( s ) ):
		for k in range( len( t ) ):
			kp[ 0, j, k ] = 1.0

	for i in range( N ):
		for j in range( len( s ) ):
			kpp = 0.0
			for k in range( len( t ) ):
				if s[ j ] == t[ k ]:
					kpp = L * kpp + L * L * kp[ i, j, k ]
				else:
					kpp = L * kpp
				kp[ i+1, j+1, k+1 ] = L * kp[ i+1, j, k+1 ] + kpp

	kn = 0.0
	for i in range( N ):
		for j in range( len( s ) ):
			for k in range( len( t ) ):
				print i, j, k, kp[ i, j, k ], s[ j ] == t[ k ]
				kn += L ** 2 * ( s[ j ] == t[ k ] ) * kp[ i, j, k ]
	return kn

def ssk2( s, t, L, N ):
	kst = ssk( s, t, L, N )
	if kst == 0.0:
		return 0.0
	kss = ssk( s, s, L, N )
	ktt = ssk( t, t, L, N )
	return kst / sqrt( kss * ktt )

def Score( Hyp, Ref ):
	return ssk2( Hyp, Ref, 0.91, 4 )

for HypA, HypB, Ref in ReadData( sys.stdin ):
	ScoreA = Score( HypA, Ref )
	ScoreB = Score( HypB, Ref )
	print >>sys.stderr, "%f\t%f" % ( ScoreA, ScoreB )
	if ScoreA > ScoreB:
		print -1
	elif ScoreA == ScoreB:
		print 0
	else:
		print 1
	sys.stdout.flush()
