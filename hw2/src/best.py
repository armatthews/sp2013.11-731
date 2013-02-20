import sys
for Line in sys.stdin:
	ScoreA, ScoreB = [ float( Part ) for Part in Line.strip().split( "\t" ) ]
	if ScoreA > ScoreB:
		print -1
	elif ScoreA == ScoreB:
		print 0
	else:
		print 1
