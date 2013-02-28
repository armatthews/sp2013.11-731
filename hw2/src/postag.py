import nltk
import sys

def Tag( Toks ):
	ToksWithTags = nltk.pos_tag( Toks )
	POSTags = [ POS for Tok, POS in ToksWithTags ]
	return POSTags


for Line in sys.stdin:
	Parts = [ Part.strip() for Part in Line.strip().split( "|||" ) ]
	Parts = [ " ".join( Tag( Part.split() ) ) for Part in Parts ]
	print " ||| ".join( Parts )
	
