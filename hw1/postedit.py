import sys
from collections import defaultdict

def isNumeric( s ):
	try:
		float( s )
		return True
	except:
		try:
			# Catch Euro-style numbers
			float( s.replace( ",", "." ) )
			return True
		except:
			return False

Source = open( "data/train-source-stemmed.txt" ).read().split( "\n" )
Target = open( "data/train-target-stemmed.txt" ).read().split( "\n" )
Align = open( "output.raw" ).read().split( "\n" ) + [ "" for i in range( 99000 ) ]
Data = zip( Source, Target, Align )[ : -1 ]

for i in range( len( Data ) ):
	Source, Target, Align = Data[ i ]
	Source = Source.strip().split()
	Target = Target.strip().split()
	Align = [ tuple( [ int( Side ) for Side in Link.split( "-" ) ] ) for Link in Align.split() ]
	Data[ i ] = Source, Target, Align

SourceVocab = defaultdict( int )
TargetVocab = defaultdict( int )
for Source, Target, _ in Data:
	for Word in Source:
		SourceVocab[ Word ] += 1
	for Word in Target:
		TargetVocab[ Word ] += 1

for Source, Target, Align in Data[ : 1000 ]:
	NewAlign = []
	for i, j in Align:
		s = Source[ i ]
		t = Target[ j ]

		sFertility = len( [ 1 for p, q in Align if p == i ] )

		# Remove links if they're pooling on one source word
		if sFertility > 6:
			continue

		# Remove links between punctuation and non punctuation
		Punctuation = ":,./?'\"[]{}\|;<>()*&^%$#@!-_+="
		if ( s in Punctuation and t not in Punctuation ) or ( t in Punctuation and s not in Punctuation ):
			continue

		# Remove links between numeric tokens and non numeric tokens
		if ( isNumeric( s ) and not isNumeric( t ) ) or ( isNumeric( t ) and not isNumeric( s ) ):
			# This condition accounts for cases like s=2013year t=2013
			if t not in s:
				continue

		# Remove links between singletons and non-singletons, if they're not linked only to each other
		if ( SourceVocab[ s ] == 1 and TargetVocab[ t ] != 1 ):
			if sFertility > 1:
					continue

		NewAlign.append( (i, j) )
	print " ".join( [ "%d-%d" % Link for Link in NewAlign ] )
