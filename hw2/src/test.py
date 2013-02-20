import sys
import pickle
from sklearn import svm

Classifier = pickle.load( open( "classifier.pkl" ) )
for Line in sys.stdin:
	Features = [ float( f ) for f in Line.strip().split( "\t" ) ]
	Classification = int( Classifier.predict( Features )[ 0 ] )
	print Classification
	sys.stdout.flush()
