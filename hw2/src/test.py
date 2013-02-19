import sys
import pickle
#from LogisticRegression import LogisticRegressionClassifier

#Weights = [ float( Line.strip() ) for Line in open( sys.argv[ 1 ] ) ]
#Classifier = LogisticRegressionClassifier()
#Classifier.Weights = Weights
#Classifier.NumFeatures = len( Weights )
#for Line in sys.stdin:
#	Features = [ float( f ) for f in Line.strip().split() ]
#	Classification = Classifier.Classify( Features )
#	print 2 * Classification - 1

from sklearn import svm
Classifier = pickle.load( open( "classifier.pkl" ) )
for Line in sys.stdin:
	Features = [ float( f ) for f in Line.strip().split() ]
	Classification = int( Classifier.predict( Features )[ 0 ] )
	print Classification
