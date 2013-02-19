import sys
import pickle

Data = []
for Line in sys.stdin:
	Features = Line.strip().split()
	Datum = ( [ float( f ) for f in Features[ : -1 ] ], int( Features[ -1 ] ) )
	Data.append( Datum )

#from LogisticRegression import LogisticRegressionClassifier
#Classifier = LogisticRegressionClassifier()
#Classifier.Train( Data )
#for Weight in Classifier.Weights:
#	print Weight

from sklearn import svm
svc = svm.SVC( kernel='rbf' )
svc.fit( [ Datum[ 0 ] for Datum in Data ], [ Datum[ 1 ] for Datum in Data ] )
pickle.dump( svc, open( "classifier.pkl", "w" ) )
