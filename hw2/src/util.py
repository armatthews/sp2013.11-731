def ReadData( stream ):
        for Line in stream:
                Parts = [ Part.strip() for Part in Line.strip().split( "|||" ) ]
                HypA, HypB, Ref = [ [ Word.strip() for Word in Part.split() ] for Part in Parts ]
                yield ( HypA, HypB, Ref )

def Overlap( Hyp, Ref, Order ):
        HypNGrams = [ Hyp[ i : i + Order ] for i in range( len( Hyp ) - Order + 1 ) ] if len( Hyp ) >= Order else []
        RefNGrams = [ Ref[ i : i + Order ] for i in range( len( Ref ) - Order + 1 ) ] if len( Ref ) >= Order else []
        return [ NGram for NGram in HypNGrams if NGram in RefNGrams ]

def Precision( Hyp, Ref, Order=1 ):
        Matches = Overlap( Hyp, Ref, Order )
        return 1.0 * len( Matches ) / len( Hyp )

def Recall( Hyp, Ref, Order=1 ):
        Matches = Overlap( Hyp, Ref, Order )
        return 1.0 * len( Matches ) / len( Ref )

def FScore( Hyp, Ref, Order=1, Alpha=0.5 ):
        P = Precision( Hyp, Ref, Order )
        R = Recall( Hyp, Ref, Order )
        if P == 0.0 and R == 0.0:
                return 0.0
        return P * R / ( ( 1 - Alpha ) * R + Alpha * P )
