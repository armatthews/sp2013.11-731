Train:	cat data/train.hyp1-hyp2-ref | python tok.py | python getFeatures.py | paste -d ' ' - data/train.gold | python train.py
Test:	cat data/test.hyp1-hyp2-ref | python tok.py | python getFeatures.py | python test.py weights.txt
