import sys

def OpenFile( File ):
	Data = open( File ).read().split( "\n" )
	Data = [ Datum.strip() for Datum in Data if len( Datum.strip() ) > 0 ]
	return Data

Source = OpenFile( sys.argv[ 1 ] )
Target = OpenFile( sys.argv[ 2 ] )
Data = zip( Source, Target )

for Source, Target in Data:
	N = len( Source.split() )
	M = len( Target.split() ) 
	Alignment = []
	for q in range( M ):
		Best = None
		BestDistance = None
		for p in range( N ):
			slope = 1.0 * M/N
			d = abs( slope * p - q ) / ( slope ** 2 + 1 ) ** 0.5
			if BestDistance == None or d < BestDistance:
				Best = p
				BestDistance = d
			elif d > BestDistance:
				break

		Alignment.append( ( Best, q ) )
	print " ".join( [ "%d-%d" % Link for Link in Alignment ] )
