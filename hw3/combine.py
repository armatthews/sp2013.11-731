import sys

for Line in sys.stdin:
	i, Winners = Line.strip().split('\t')
	i = int(i)
	Winners = Winners.split()

	f = open(Winners[0])
	for j, Line in enumerate(f):
		if i == j + 1:
			print Line.strip()
			break
	f.close()
