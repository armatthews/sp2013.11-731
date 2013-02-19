import sys

def Tokenize( String ):
	return String

for Line in sys.stdin:
	Line = Line.strip()
	Parts = [ Part.strip() for Part in Line.split( "|||" ) ]
	for i, Part in enumerate( Parts ):
		Words = [ Word.strip() for Word in Part.split() ]
		String = " ".join( Words )
		Parts[ i ] = Tokenize( String )
	print " ||| ".join( Parts )
