from collections import defaultdict
from operator import itemgetter
import sys
import os
import pickle
import ParallelCorpus
import copy

def Zero():
	return 0.0

def DefaultDictZero():
	return defaultdict( Zero )

def LoadIBM1TM( InputFileName ):
        p = defaultdict( DefaultDictZero )
        for Line in open( InputFileName, "r" ):
                Line = Line.decode( "utf-8" ).strip()
		Source, Target, Probability = Line.split()
		if float( Probability ) != 0.0:
	                p[ Target ][ Source ] = float( Probability )
        return p

def Normalize( Table ):
	Total = 0.0
	for Key in Table.keys():
		Total += Table[ Key ]
		if Table[ Key ] == 0.0:
			del Table[ Key ]

	assert len( Table.keys() ) == 0 or Total > 0.0

	for Key in Table.keys():
		Table[ Key ] /= Total
		assert Table[ Key ] > 0.0 and Table[ Key ] <= 1.0

	return Table

class TM:
	def __init__( self ):
		self.TranslationTable = defaultdict( DefaultDictZero ) # TranslationTable[ Target ][ Source ]
		self.TransitionTable = defaultdict( Zero ) # TransitionTable[ a_j - a_(j-1) ]
		self.NullProbability = 0.99

	def InitializeUniformly( self, Data ):
		MaxSourceLen = max( map( len, map( itemgetter(0), Data ) ) )
		for d in range( -MaxSourceLen + 1, MaxSourceLen ):
			val = 1.0 / ( 2 * MaxSourceLen - 1 )
			self.TransitionTable[ d ] = val
		self.NormalizeTransitionTable()

		for SourceSentence, TargetSentence in Data:
			for SourceWord in [ "NULL" ] + SourceSentence:
			#for SourceWord in SourceSentence:
				for TargetWord in TargetSentence:
					self.TranslationTable[ TargetWord ][ SourceWord ] += 1.0
		self.NormalizeTranslationTable()

		self.NullProbability = 0.99
		self.UniformTranslationTable = copy.copy( self.TranslationTable )
		self.UniformTransitionTable = copy.copy( self.TransitionTable )

	def NormalizeTranslationTable( self ):
		SourceCounts = defaultdict( Zero )
		for TargetWord in self.TranslationTable.keys():
			for SourceWord, Value in self.TranslationTable[ TargetWord ].iteritems():
				SourceCounts[ SourceWord ] += Value

		for TargetWord in self.TranslationTable.keys():
			for SourceWord, Value in self.TranslationTable[ TargetWord ].iteritems():
				self.TranslationTable[ TargetWord ][ SourceWord ] = Value / SourceCounts[ SourceWord ]
 
		return self.TranslationTable

	def NormalizeTransitionTable( self ):
		self.TransitionTable = Normalize( self.TransitionTable )
		return self.TransitionTable

	def __repr__( self ):
		r = u""
		r += "%g\n\n" % self.NullProbability

		for d in sorted( self.TransitionTable.keys() ):
			r += u"%d %g\n" % ( d, self.TransitionTable[ d ] )

		if len( self.TransitionTable.keys() ) > 0:
			r += u"\n"

		for TargetWord in sorted( self.TranslationTable.keys() ):
			for SourceWord in sorted( self.TranslationTable[ TargetWord ].keys(), key = lambda k: self.TranslationTable[ TargetWord ][ k ], reverse = True ):
					r += u"%s %s %f\n" % ( SourceWord, TargetWord, self.TranslationTable[ TargetWord ][ SourceWord ] )
	
		return r.encode( "utf-8" )
	
	def Output( self, stream ):
		stream.write( u"%g\n\n" % self.NullProbability )

		for d in sorted( self.TransitionTable.keys() ):
			stream.write( u"%d %g\n" % ( d, self.TransitionTable[ d ] ) )

		if len( self.TransitionTable.keys() ) > 0:
			stream.write( u"\n" )

		for TargetWord in sorted( self.TranslationTable.keys() ):
			for SourceWord in sorted( self.TranslationTable[ TargetWord ].keys(), key = lambda k: self.TranslationTable[ TargetWord ][ k ], reverse = True ):
					stream.write( ( u"%s %s %g\n" % ( SourceWord, TargetWord, self.TranslationTable[ TargetWord ][ SourceWord ] ) ).encode( "utf-8" ) )

	def Input( self, stream ):
		self.NullProbability = float( stream.readline().strip() )
		stream.readline()
		Line = stream.readline()
		while Line != "":
			Parts = Line.strip().split()
			if len( Parts ) == 2:
				self.TransitionTable[ int( Parts[ 0 ] ) ] = float( Parts[ 1 ] )
			elif len( Parts ) == 3:
				self.TranslationTable[ Parts[ 1 ] ][ Parts[ 0 ] ] = float( Parts[ 2 ] )
			Line = stream.readline()

	def GetBestAlignment( self, Source, Target ):
		I = len( Source )
		J = len( Target )
		# i source j target
		# TranslationTable[ Target ][ Source ]
		# but Table[ Source ][ Target ]

		# Compute the table and path through the sentences
		# Table[ i ][ j ] represents the probability of the best
		# alignment given that Source[ i ] is aligned to Target[ j ]
		# Path is used to backtrack once we find the optimal path.
		Table = [ [ 0 for j in range( J ) ] for i in range( 2*I ) ]
		Path = [ [ -1 for j in range( J ) ] for i in range( 2*I ) ]

		# Since the full transition table may put probability mass on transitions
		# to words outside the bounds of the source sentence, we will create a copy
		# that disallows such transitions, and re-normalize.
		LocalTransitionTable = defaultdict( Zero )
		for i in range( -I + 1, I ):
			LocalTransitionTable[ i ] = self.TransitionTable[ i ]
		LocalTransitionTable = Normalize( LocalTransitionTable )

		for i in range( 2 * I ):
			j = 0
			Table[ i ][ j ] = self.TranslationTable[ Target[ j ] ][ Source[ i ] if i < I else "NULL" ]

		for j in range( 1, J ):
			for i in range( I ):
				Best = None
				for ip in range( I ):
					if i >= I and ip >= I:
						TransitionCost = self.NullProbability * LocalTransitionTable[ ( i - I ) - ( ip - I ) ]
					elif i >= I:
						TransitionCost = self.NullProbability * LocalTransitionTable[ ( i - I ) - ip ]
					elif ip >= I:
						TransitionCost = LocalTransitionTable[ i - ( ip - I ) ]
					else:
						TransitionCost = LocalTransitionTable[ i - ip ]

					#print "Transition cost i=%d j=%d ip=%d is %g" % ( i, j, ip, TransitionCost )
					Score = TransitionCost * Table[ ip ][ j - 1 ]
					if Best == None or Score > Best:
						Best = Score
						Path[ i ][ j ] = ip

				TranslationProbability = self.TranslationTable[ Target[ j ] ][ Source[ i ] if i < I else "NULL" ]
				#print "Translation cost of t=\"%s\" s=\"%s\" is %g" % ( Target[ j ], Source[ i ] if i < I else "NULL", TranslationProbability )
				Table[ i ][ j ] = TranslationProbability * Best

		# Table computations complete.
		# Now we find the best probability, which is the highest
		# number in the last column. Then we backtrack
		# to find the actual alignment.

		Best = None
		for i in range( 2 * I ):
			if Best == None or Table[ i ][ -1 ] > Table[ Best ][ -1 ]:
				Best = i

		Probability = Table[ Best ][ -1 ]
		Alignment = [ None for j in range( J ) ]

		Prev = Best
		for j in range( J - 1, -1, -1 ):
			Alignment[ j ] = Prev
			Prev = Path[ Prev ][ j ]

		return ( Alignment, Probability )

# Every target word maps to exactly one source word
def IterateTables( TranslationTable, TransitionTable, Data ):
	q = defaultdict( DefaultDictZero )
	r = defaultdict( DefaultDictZero )
        JointCounts = defaultdict( DefaultDictZero )
	SourceCounts = defaultdict( Zero )
	TargetCounts = defaultdict( Zero )
	TransitionCounts = defaultdict( Zero )
	NullTransitions = 0.0
	NonNullTransitions = 0.0

	for i, SentencePair in enumerate( Data ):
		sys.stdout.write( "Examined %d/%d sentences.\r" % ( i, len( Data ) ) )
		sys.stdout.flush()

		SourceSentence, TargetSentence = SentencePair
		I = len( SourceSentence )
		
		# Update the counts
		Alignment, AlignmentProbability = Model.GetBestAlignment( SourceSentence, TargetSentence )
		AlignmentProbability = 1.0
		assert AlignmentProbability >= 0.0 and AlignmentProbability <= 1.0
		#sys.stderr.write( "Best alignment of sentence %d: %s with p %g\n" % ( i, Alignment, AlignmentProbability ) )

		for j in range( len( TargetSentence ) ):
			SourceWord = SourceSentence[ Alignment[ j ] ] if Alignment[ j ] < I else "NULL"
			TargetWord = TargetSentence[ j ]
			JointCounts[ TargetWord ][ SourceWord ] += AlignmentProbability
			SourceCounts[ SourceWord ] += AlignmentProbability
			TargetCounts[ TargetWord ] += AlignmentProbability

			if Alignment[ j ] >= I:
				NullTransitions += AlignmentProbability
			else:
				NonNullTransitions += AlignmentProbability

			if Alignment[ j ] < I and j > 0:
				TransitionCounts[ Alignment[ j ] - Alignment[ j - 1 ] ] += AlignmentProbability

	sys.stdout.write( "Examined %d/%d sentences.\n" % ( len( Data ), len( Data ) ) )
	sys.stdout.flush()

	r = Normalize( TransitionCounts )
	for TargetWord in JointCounts.keys():
		for SourceWord in JointCounts[ TargetWord ].keys():
			if SourceCounts[ SourceWord ] != 0.0:
				q[ TargetWord ][ SourceWord ] = JointCounts[ TargetWord ][ SourceWord ] / SourceCounts[ SourceWord ]
			else:
				assert JointCounts[ TargetWord ][ SourceWord ] == 0.0
	NullProbability = NullTransitions / ( NullTransitions + NonNullTransitions )

	return q, r, NullProbability

def Iterate( Model, Data ):
	NewTranslationTable, NewTransitionTable, NewNullProbability = IterateTables( Model.TranslationTable, Model.TransitionTable, Data )

	NewModel = TM()
	NewModel.TranslationTable = NewTranslationTable
	NewModel.TransitionTable = NewTransitionTable
	NewModel.TranslationTable = NewModel.NormalizeTranslationTable()
	NewModel.TransitionTable = NewModel.NormalizeTransitionTable()
	NewModel.NullProbability = NewNullProbability
	NewModel.UniformTranslationTable = Model.UniformTranslationTable
	NewModel.UniformTransitionTable = Model.UniformTransitionTable

	print "Smoothing probability tables..."
	Alpha = 0.4
	#for SourceSentence, TargetSentence in Data:
	#	for TargetWord in TargetSentence:
	#		for SourceWord in [ "NULL" ] + SourceSentence:
	#			NewModel.TranslationTable[ TargetWord ][ SourceWord ] = ( 1.0 - Alpha ) * NewTranslationTable[ TargetWord ][ SourceWord ] + Alpha * NewModel.UniformTranslationTable[ TargetWord ][ SourceWord ]

	#for Delta in NewModel.UniformTransitionTable.keys():
	#	NewModel.TransitionTable[ Delta ] = ( 1.0 - Alpha ) * NewTransitionTable[ Delta ] + Alpha * NewModel.UniformTransitionTable[ Delta ]

	print "Doing final normalization pass..."
	NewModel.NormalizeTranslationTable()
	NewModel.NormalizeTransitionTable()

	return NewModel

def Output( Model, IterationNumber, OutputDir ):
	print "Dumping output for iteration %d..." % IterationNumber
	f = open( os.path.join( OutputDir, "%d.txt" % IterationNumber ), "w" )
	Model.Output( f )
	f.close()

# Entry Point
if __name__ == "__main__":
	if len( sys.argv ) < 4:
		print "Usage: python %s SourceFile TargetFile OutputDir [Iterations] [SeedLexProbs]" % sys.argv[ 0 ]
		exit()

	OutputDir = sys.argv[ 3 ]
	IterationCount = int( sys.argv[ 4 ] ) if len( sys.argv ) >= 5 else 0
	if not os.path.exists( OutputDir ):
		os.mkdir( OutputDir )

	Data = ParallelCorpus.LoadParallelCorpus( sys.argv[ 1 ], sys.argv[ 2 ] )	
	print "Initializing..."
	Model = TM()
	Model.InitializeUniformly( Data )
	if len( sys.argv ) >= 6:
		print "Loading IBM1 TM..."
		Model.TranslationTable = LoadIBM1TM( sys.argv[ 5 ] )
	ExpectedTargetWordCount = len( Model.TranslationTable )

	i = 0
	Output( Model, i, OutputDir )
	while i < IterationCount or IterationCount == 0:
		i += 1
		print "Beginning iteration %d" % i
		Model = Iterate( Model, Data )
		Output( Model, i, OutputDir )

		#if len( Model.TranslationTable ) != ExpectedTargetWordCount:
		#	raise Exception( "Target word dropped from model during iteration %d!" % i )
