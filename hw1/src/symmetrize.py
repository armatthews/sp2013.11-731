import sys
from operator import itemgetter

if len( sys.argv ) < 5:
	print >>sys.stderr, "Usage: python %s Source Target STAligns TSAligns" % sys.argv[ 0 ]
	sys.exit( 1 )

def ReadDataFile( FileName ):
	File = open( FileName )
	Data = File.read()
	File.close()

	Data = Data.split( "\n" )
	Data = [ Datum.strip() for Datum in Data ]
	while len( Data[ -1 ] ) == 0:
		Data = Data[ : -1 ]

	return Data

def ReadAlignFile( FileName ):
	Data = ReadDataFile( FileName )
	Links = [ Line.split( " " ) for Line in Data ]
	Links = [ [ Link.split( "-" ) for Link in Line ] for Line in Links ]
	Links = [ [ ( int( Link[ 0 ] ), int( Link[ 1 ] ) ) for Link in Line ] for Line in Links ]

	return Links

def Sort( Alignment ):
	Alignment = sorted( Alignment, key=itemgetter( 0 ) )
	Alignment = sorted( Alignment, key=itemgetter( 1 ) )
	return Alignment

def Reverse( Alignment ):
	return [ ( Link[ 1 ], Link[ 0 ] ) for Link in Alignment ]

def Intersection( A, B ):
	return [ Link for Link in A if Link in B ]

def Union( A, B ):
	return A + [ Link for Link in B if Link not in A ]

def GetNeighbors( Link, SourceLength, TargetLength ):
	Neighbors = []
	for x in [ -1, 0, 1 ]:
		for y in [ -1, 0, 1 ]:
			Neighbor = ( Link[ 0 ] + x, Link[ 1 ] + y )
			if Neighbor != Link:
				if Neighbor[ 0 ] >= 0 and Neighbor[ 0 ] < SourceLength:
					if Neighbor[ 1 ] >= 0 and Neighbor[ 1 ] < TargetLength:
						Neighbors.append( Neighbor )
	return Neighbors

def SourceAligned( Alignment, Index ):
	return len( [ Link for Link in Alignment if Link [ 0 ] == Index ] ) > 0

def TargetAligned( Alignment, Index ):
	return len( [ Link for Link in Alignment if Link [ 1 ] == Index ] ) > 0

def GrowDiag( AlignmentIntersection, STAligns, TSAligns, SourceLength, TargetLength ):
	NewAlignment = AlignmentIntersection
	AlignmentUnion = Union( STAligns, TSAligns )	
	while True:
		LinkAdded = False
		for TargetWord in range( 0, TargetLength ):
			for SourceWord in range( 0, SourceLength ):
				Link = (SourceWord, TargetWord)	
				if Link in NewAlignment:
					Neighbors = GetNeighbors( Link, SourceLength, TargetLength )
					Neighbors = [ Neighbor for Neighbor in Neighbors if Neighbor in AlignmentUnion ]
					for Neighbor in Neighbors:
						if not SourceAligned( NewAlignment, Neighbor[ 0 ] ) or not TargetAligned( NewAlignment, Neighbor[ 1 ] ):
								NewAlignment.append( Neighbor )
								LinkAdded = True
		if not LinkAdded:
			break

	return Sort( NewAlignment )

def Final( NewAlignment, MonoAlignment, SourceLength, TargetLength ):
	for TargetWord in range( 0, TargetLength ):
		for SourceWord in range( 0, SourceLength ):
			Link = ( SourceWord, TargetWord )
			if not SourceAligned( NewAlignment, SourceWord ) or not TargetAligned( NewAlignment, TargetWord ):
				if Link in MonoAlignment:
					NewAlignment.append( Link )
	return Sort( NewAlignment )

# Algorithm taken from Moses documentation.
# http://www.statmt.org/moses/?n=FactoredTraining.AlignWords

SourceSentences = ReadDataFile( sys.argv[ 1 ] )
TargetSentences = ReadDataFile( sys.argv[ 2 ] )
STAligns = ReadAlignFile( sys.argv[ 3 ] )
TSAligns = ReadAlignFile( sys.argv[ 4 ] )
TSAligns = [ Reverse( Alignment ) for Alignment in TSAligns ]

Data = zip( SourceSentences, TargetSentences, STAligns, TSAligns )
for Source, Target, STAlign, TSAlign in Data:
	SourceLength = len( Source.split() )
	TargetLength = len( Target.split() )
	Alignment = Intersection( STAlign, TSAlign )
	Alignment = GrowDiag( Alignment, STAlign, TSAlign, SourceLength, TargetLength )
	Alignment = Final( Alignment, STAlign, SourceLength, TargetLength )
	#Alignment = Final( Alignment, TSAlign, SourceLength, TargetLength )
	print " ".join( [ "%d-%d" % Link for Link in Alignment ] )
