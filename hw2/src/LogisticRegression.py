import sys
import random
from collections import defaultdict
from math import sqrt, pi, e
from operator import itemgetter

class LogisticRegressionClassifier:
	def __init__( self ):
		# self.Weights[ Feature ] is in [ 0, 1 ]
	        self.Weights = defaultdict( lambda: 1.0 ) 
		self.NumFeatures = 0

	# Data is to be an N-length array with each element
	# being a tuple of two values:
	# X - a tuple of length F.
	# Y - a label, either 0 or 1
	# F is the number of features.
	# N is the number of examples.
	def Train( self, Data ):

		# Dot product of two vectors
		def Dot( w, x ):
			return sum( map( lambda i: w[ i ] * x[ i ], range( len( w ) ) ) )

		# Derivative of the log likelihood function of our data with respect to w
		def Derivative( w, Data ):
			Sum = [ 0.0 for f in w ]
			for ( x, y ) in Data:
				m = y - ( 1 - g( w, x ) )
				for i in range( len( Sum ) ):
					Sum[ i ] += x[ i ] * m
			return Sum

		# The squared error of the classifier over the data.
		def SquaredError( w, Data ):
			Error = 0.0
			for ( x, y ) in Data:
				Error += ( y - ( 1 - g( x, w ) ) ) ** 2
			return Error

		# The logistic function of x parameterized by w
		def g( w, x ):
			return 1. / ( 1. + e ** Dot( w, x ) )

		# The squared standard deviation of a 1D vector.
		def SigmaSquared( w ):
			mu = 1.0 * sum( w ) / len( w )
			Sigma2 = 1.0 * sum( map( lambda x: ( x - mu ) ** 2, w ) ) / len( w )
			return Sigma2

		# Append a 1 to the end of every feature vector, allowing us to use an intercept
		Data = map( lambda Item: ( Item[ 0 ] + [ 1 ], Item[ 1 ] ), Data )

		self.NumFeatures = len( Data[ 0 ][ 0 ] )

		# Initialize the weight vector randomly
		w = [ random.random() for f in range( self.NumFeatures ) ]

		LearningRate = 0.001
		Epsilon = 0.001

		# Iteratively update until the difference between our old model
		# and our updated model's training error is less than Epsilon
		OldError = sys.float_info.max
		while True:
			Delta = Derivative( w, Data )
			Delta = map( lambda f: LearningRate * f, Delta )
	
			Sigma2 = SigmaSquared( w )
			#Regularizer = map( lambda f: LearningRate * f / Sigma2, w ) # Gaussian regulariation
			Regularizer = map( lambda f: LearningRate * 2 * f, w ) # L2 norm regularization
			#Regularizer = map( lambda f: 0.0, w ) # No regularization

			w = map( lambda i: w[ i ] + Delta[ i ] - Regularizer[ i ], range( len( w ) ) )	

			# Compute the new error, and break the loop if necessary
			NewError = SquaredError( w, Data )
			DeltaError = ( NewError - OldError )
			OldError = NewError
			if abs( DeltaError ) < Epsilon:
				break

		self.Weights = w

	# x is an self.Dimension length array to be classified
	def Probability( self, x ):
		# Add a 1 to the end of the feature vector for the bias term
		x = x + [ 1 ]

		if self.NumFeatures == 0:
		    raise Exception( "Attempt to classify using an untrained classifier." )
		if len( x ) != self.NumFeatures:
		    raise Exception( "Attempt to classify example with wrong number of features." )

		# Dot product of two vectors.
		def Dot( w, x ):
			return sum( map( lambda i: w[ i ] * x[ i ], range( len( w ) ) ) )

		return 1. / ( 1. + e ** -Dot( self.Weights, x ) )

	def Classify( self, x ):
		p = self.Probability( x )
		return 1 if p >= 0.5 else 0
