import sys
from math import sqrt

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

def ReadData( stream ):
        for Line in stream:
                Parts = [ Part.strip() for Part in Line.strip().split( "|||" ) ]
                HypA, HypB, Ref = [ [ Word.strip() for Word in Part.split() ] for Part in Parts ]
                yield ( HypA, HypB, Ref )

for HypA, HypB, Ref in ReadData( sys.stdin ):
	HypAScore = ssk2( HypA, Ref, 0.91, 4 )
	HypBScore = ssk2( HypB, Ref, 0.91, 4 )
	if abs( HypAScore - HypBScore ) < 0.000001:
		print 0
	elif HypAScore > HypBScore:
		print -1
	else:
		print 1
	sys.stdout.flush()
