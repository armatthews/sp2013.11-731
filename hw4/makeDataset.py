#!/usr/bin/env python
import argparse
import sys
import pickle
import re
from collections import namedtuple

parser = argparse.ArgumentParser()
parser.add_argument('n_best_list')
parser.add_argument('source')
parser.add_argument('refs')
parser.add_argument('meteor_matrix_file')
args = parser.parse_args()

Sentence = namedtuple('Sentence', 'id, src, ref, hyps')
Hypothesis = namedtuple('Hypothesis', 'text, features, ref_score, hyp_scores')

n_best_list = open(args.n_best_list)
source_file = open(args.source)
ref_file = open(args.refs)

sentences = []

prev_id = None
ref = None
while True:
	hyp = n_best_list.readline().decode('utf-8')
	if not hyp:
		break

	hyp = hyp.strip()
	parts = hyp.split('|||')
	sent_id = parts[0].strip()
	text = parts[1].strip()
	feature_text = parts[2].strip()
	ref_score = float(parts[3].strip()) if len(parts) >= 4 else None

	features = {}
	for feature in feature_text.strip().split():
		key, value = feature.split('=')
		value = float(value)
		features[key] = value

	if sent_id != prev_id:
		_, source = source_file.readline().decode('utf-8').strip().split(" ||| ")
		assert source
		ref = ref_file.readline().decode('utf-8').strip()
		if not ref:
			ref = None
		#assert ref
	if sent_id != prev_id:
		sentences.append(Sentence(sent_id, source, ref, []))
	sentences[-1].hyps.append(Hypothesis(text, features, ref_score, []))
	
	prev_id = sent_id

meteor_matrix_file = open(args.meteor_matrix_file)

line_num = 0
while True:
        line = meteor_matrix_file.readline().decode('utf-8')
        if not line:
                break
        match = re.match(r'Segment.*score:(.*)', line)
        if not match:
                continue

        sent_num = line_num / 10000
        hyp_num = (line_num % 10000) / 100
        ref_num = (line_num % 100)

        score = float(match.group(1).strip())
        assert len(sentences[sent_num].hyps[hyp_num].hyp_scores) == ref_num
	sentences[sent_num].hyps[hyp_num].hyp_scores.append(score)

        line_num += 1

pickle.dump(sentences, sys.stdout)
