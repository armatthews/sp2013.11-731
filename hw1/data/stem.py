import sys
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
#stemmer = SnowballStemmer( "german" )

for Line in sys.stdin:
	Line = Line.decode( "utf-8" ).strip()
	Words = Line.split()
	Words = [ stemmer.stem( Word.strip() ) for Word in Words ]
	Line = " ".join( Words )
	print Line.encode( "utf-8" )
