import sys
import pickle
from sklearn import svm

Data = []
Labels = []
for Line in sys.stdin:
	Features = Line.strip().split( "\t" )
	Datum = [ float( f ) for f in Features[ : -1 ] ]
	Label = int( Features[ -1 ] )
	Data.append( Datum )
	Labels.append( Label )

svc = svm.SVC( kernel='rbf', gamma=0.0001, C=1000000.0 )
svc.fit( Data, Labels )
pickle.dump( svc, open( "classifier.pkl", "w" ) )
