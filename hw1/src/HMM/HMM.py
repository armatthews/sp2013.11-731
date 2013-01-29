from collections import defaultdict
from operator import itemgetter
import sys
import pickle
import ParallelCorpus

def Zero():
	return 0.0

def DefaultDictZero():
	return defaultdict( Zero )

def LoadIBM1TM( InputFileName ):
        p = defaultdict( DefaultDictZero )
        for Line in open( InputFileName, "r" ):
                Line = Line.decode( "utf-8" ).strip()
		Source, Target, Probability = Line.split()
                p[ Target ][ Source ] = float( Probability )
        return p

class TM:
	def __init__( self ):
		self.TranslationTable = defaultdict( DefaultDictZero ) # TranslationTable[ Target ][ Source ]
		self.TransitionTable = defaultdict( DefaultDictZero ) # TransitionTable[ len( Target ) ][ a_j - a_j-1 ]

	def InitializeUniformly( self, Data ):
		MaxSourceLen = max( map( len, map( itemgetter(0), Data ) ) ) + 1 # +1 for NULL
		MaxTargetLen = max( map( len, map( itemgetter(1), Data ) ) )
		for i in range( MaxSourceLen + 1 ):
			val = 1.0 / ( 2 * MaxSourceLen - 1 )
			for d in range( -MaxSourceLen + 1, MaxSourceLen ):
				self.TransitionTable[ i ][ d ] = 1.0 / ( abs( d - 1.0 ) + 1 )
		self.NormalizeTransitionTable()

		for SourceSentence, TargetSentence in Data:
			for SourceWord in [ "NULL" ] + SourceSentence:
				for TargetWord in TargetSentence:
					self.TranslationTable[ TargetWord ][ SourceWord ] += ( 1.0 if SourceWord is not "NULL" else 0.01 )
		self.NormalizeTranslationTable()

	def NormalizeTranslationTable( self ):
		p = self.TranslationTable
		for TargetWord in p.keys():
			Total = 0.0
			for SourceWord in p[ TargetWord ].keys():
				Total += p[ TargetWord ][ SourceWord ]
			for SourceWord in p[ TargetWord ].keys():
				if Total != 0.0:
					p[ TargetWord ][ SourceWord ] /= Total
				else:
					p[ TargetWord ][ SourceWord ] = 0.0
		return p

	def NormalizeTransitionTable( self ):
		p = self.TransitionTable
		for Length in p.keys():
			Total = 0.0
			for Delta in p[ Length ].keys():
				Total += p[ Length ][ Delta ]
			for Delta in p[ Length ].keys():
				if Total != 0.0:
					p[ Length ][ Delta ] /= Total
				else:
					p[ Length ][ Delta ] = 0.0
		return p

	def __repr__( self ):
		r = u""
		for I in self.TransitionTable.keys():
			r += u"%d: %s\n" % ( I, str( dict( self.TransitionTable[ I ] ) ) )

		if len( self.TransitionTable.keys() ) > 0:
			r += u"\n"

		for TargetWord in sorted( self.TranslationTable.keys() ):
			r += u"%s\n" % TargetWord
			for SourceWord in sorted( self.TranslationTable[ TargetWord ].keys(), key = lambda k: self.TranslationTable[ TargetWord ][ k ], reverse = True ):
				if self.TranslationTable[ TargetWord ][ SourceWord ] > 10.0 ** -6:
					r += u"\t%s: %f\n" % ( SourceWord, self.TranslationTable[ TargetWord ][ SourceWord ] )
	
		return r.encode( "utf-8" )

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
		Table = [ [ 0 for j in range( J ) ] for i in range( I ) ]
		Path = [ [ -1 for j in range( J ) ] for i in range( I ) ]

		for i in range( I ):
			j = 0
			Table[ i ][ j ] = self.TranslationTable[ Target[ j ] ][ Source[ i ] ]
			if Table[ i ][ j ] == 0.0:
				Table[ i ][ j ] = 10.0 ** -7

		for j in range( 1, J ):
			for i in range( I ):
				Best = None
				for ip in range( I ):
					if self.TransitionTable[ I ][ i - ip ] > 0.0:
						Score = self.TransitionTable[ I ][ i - ip ] * Table[ ip ][ j - 1 ]
					else:
						Score = 10.0 ** -7 * Table[ ip ][ j - 1]
					if Best == None or Score > Best:
						Best = Score
						Path[ i ][ j ] = ip
				TranslationProbability = self.TranslationTable[ Target[ j ] ][ Source[ i ] ]
				if TranslationProbability == 0.0:
					TranslationProbability = 10.0 ** -7
				Table[ i ][ j ] = TranslationProbability * Best

		# Table computations complete.
		# Now we find the best probability, which is the highest
		# number in the last column. Then we backtrack
		# to find the actual alignment.

		Best = None
		for i in range( I ):
			if Best == None or Table[ i ][ -1 ] > Table[ Best ][ -1 ]:
				Best = i

		Probability = Table[ Best ][ -1 ]
		Alignment = [ None for j in range( J ) ]

		Prev = Best
		for j in range( J - 1, -1, -1 ):
			Alignment[ j ] = Prev
			Prev = Path[ Prev ][ j ]

		return ( Alignment, Probability )

# Initialize uniformly
# To do this we set every entry in p[ t ][ s ] to 1
# and then normalize at the end
def InitializeUniformly( Data ):
	p = defaultdict( lambda: defaultdict( lambda: 0.0 ) )

	for SourceSentence, TargetSentence in Data:
		for TargetWord in TargetSentence:
			for SourceWord in SourceSentence + [ "NULL" ]:
				p[ TargetWord ][ SourceWord ] = 1.0
	p = Normalize( p )
	return p

# Every target word maps to exactly one source word
def IterateTables( TranslationTable, TransitionTable, Data ):
	q = defaultdict( DefaultDictZero )
	r = defaultdict( DefaultDictZero )
        SourceCounts = defaultdict( Zero )
        JointCounts = defaultdict( DefaultDictZero )
	TargetCounts = defaultdict( Zero )
	TransitionCounts = defaultdict( DefaultDictZero )
	DeltaCounts = defaultdict( Zero )

	for i, SentencePair in enumerate( Data ):
		if i % 1000 == 0:
			sys.stdout.write( "Examined %d/%d sentences.\r" % ( i, len( Data ) ) )
		SourceSentence, TargetSentence = SentencePair
		SourceSentence = [ "NULL" ] + SourceSentence
		
		# Update the counts
		Alignment, AlignmentProbability = Model.GetBestAlignment( SourceSentence, TargetSentence )
		#AlignmentProbability /= AlignmentProbability
		for j in range( len( TargetSentence ) ):
			SourceWord = SourceSentence[ Alignment[ j ] ]
			TargetWord = TargetSentence[ j ]
			JointCounts[ TargetWord ][ SourceWord ] += AlignmentProbability
			SourceCounts[ SourceWord ] += AlignmentProbability
			if j > 0:
				TransitionCounts[ len( SourceSentence ) ][ Alignment[ j ] - Alignment[ j - 1 ] ] += AlignmentProbability
				DeltaCounts[ Alignment[ j ] - Alignment[ j - 1 ] ] += AlignmentProbability

	for Length in TransitionCounts.keys():
		for Delta in TransitionCounts[ Length ].keys():
			if DeltaCounts[ Delta ] > 0.0:
				r[ Length ][ Delta ] = TransitionCounts[ Length ][ Delta ] / DeltaCounts[ Delta ]
			else:
				if TransitionCounts[ Length ][ Delta ] == 0.0:
					r[ Length ][ Delta ] = 0.0
				else:
					raise Exception()

        for gwar, TargetWord in enumerate( JointCounts.keys() ):
		#print gwar, TargetWord
                for SourceWord in JointCounts[ TargetWord ].keys():
			if SourceCounts[ SourceWord ] > 0.0:
				q[ TargetWord ][ SourceWord ] = JointCounts[ TargetWord ][ SourceWord ] / SourceCounts[ SourceWord ]
			else:
				if JointCounts[ TargetWord ][ SourceWord ] == 0.0:
					q[ TargetWord ][ SourceWord ] = 0.0
				else:
					raise Exception()

	return q, r

def Iterate( Model, Data ):
	NewTranslationTable, NewTransitionTable = IterateTables( Model.TranslationTable, Model.TransitionTable, Data )

	NewModel = TM()
	NewModel.TranslationTable = NewTranslationTable
	NewModel.TransitionTable = NewTransitionTable
	NewModel.TranslationTable = NewModel.NormalizeTranslationTable()
	NewModel.TransitionTable = NewModel.NormalizeTransitionTable()

	return NewModel

# Entry Point
if __name__ == "__main__":
	if len( sys.argv ) < 3:
		print "Usage: %s SourceFile TargetFile [Iterations] [SeedLexProbs]" % sys.argv[ 0 ]
		exit()

	IterationCount = int( sys.argv[ 3 ] ) if len( sys.argv ) >= 4 else 0

	Data = ParallelCorpus.LoadParallelCorpus( sys.argv[ 1 ], sys.argv[ 2 ] )
	#Data = [ ( Source + [ "NULL" ], Target ) for ( Source, Target ) in Data ]
	print "Initializing..."
	Model = TM()
	Model.InitializeUniformly( Data )
	if len( sys.argv ) >= 5:
		print "Loading IBM1 TM..."
		Model.TranslationTable = LoadIBM1TM( sys.argv[ 4 ] )
	ExpectedTargetWordCount = len( Model.TranslationTable )

	print "Dumping output..."
	pickle.dump( Model, open( "output/HMM0.pkl", "w" ) )

	i = 0
	while i < IterationCount or IterationCount == 0:
		print "Beginning iteration %d" % ( i + 1 )
		Model = Iterate( Model, Data )
		i += 1
		print "Dumping output..."
		pickle.dump( Model, open( "output/HMM%d.pkl" % i, "w" ) )

		if len( Model.TranslationTable ) != ExpectedTargetWordCount:
			raise Exception( "Target word dropped from model during iteration %d!" % i )	
