import sys

for Line in sys.stdin:
	Line = Line.strip()
	Links = Line.split()
	Links = [ Link.split( "-" ) for Link in Links ]
	Links = [ "%s-%s" % ( Link[ 1 ], Link[ 0 ] ) for Link in Links ]
	print " ".join( Links )
