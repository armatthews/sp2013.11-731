def LoadSentenceFile( FileName ):
        Data = []
        for Line in open( FileName, "r" ):
		Line = Line.decode( "utf-8" )
                Line = Line.strip()
                Data.append( Line.split() )
        return Data

def LoadParallelCorpus( SourceFile, TargetFile ):
	SourceData = LoadSentenceFile( SourceFile )
	TargetData = LoadSentenceFile( TargetFile )
	Corpus = zip( SourceData, TargetData )
	return Corpus
