import pickle
import sys
from math import exp, sqrt
from collections import namedtuple
from operator import itemgetter
import random

def dot_dict(weights, feature_vector):
	return sum([weights[k] * v for k, v in feature_vector.iteritems()])

def dot(v, w):
	return sum([f * g for f, g in zip(v, w)])

def scale(v, d):
	return [f * d for f in v]

def normalize(v):
	L = sqrt(dot(v, v))
	return [f/L for f in v]

Sentence = namedtuple('Sentence', 'id, src, ref, hyps')
Hypothesis = namedtuple('Hypothesis', 'text, features, ref_score, hyp_scores')
sys.stderr.write("Loading pickled data... ")
dataset = pickle.load(open(sys.argv[1]))
sys.stderr.write("Done!\n")

def genHyps(weights):
	global dataset
	best_hyps = []
	for sentence in dataset:
		sent_scores = {}
		for hyp in sentence.hyps:
			hyp_scores = hyp.hyp_scores
			total_score = 0.0
			for i, score in enumerate(hyp_scores):
				other = sentence.hyps[i]
				try:
					other_prob = exp(-dot_dict(weights, other.features))	
				except:
					other_prob = 1.0
				total_score += hyp_scores[i] * other_prob	
			sent_scores[hyp.text, hyp.ref_score] = total_score

		best_hyp = max(sent_scores.iteritems(), key=itemgetter(1))
		best_hyps.append(best_hyp[0])
	return best_hyps

def score(hyps):
	meteor = 0.0
	total_length = 0
	for hyp_text, hyp_score in hyps:
		if hyp_score != None:
			total_length += len(hyp_text.split())
			meteor += hyp_score * len(hyp_text.split())
	return meteor / total_length

def line_search(func, start_weights, alpha=None, beta=None, direction=None, epsilon=0.1, step_size=1.0 ):
	if direction == None:
		direction = normalize([random.random() for _ in start_weights])
		direction = [step_size * d for d in direction]
	assert len(start_weights) == len(direction)

	if alpha == None:
		alpha = [f - g for f, g in zip(start_weights, direction)]
	assert len(alpha) == len(start_weights)

	if beta == None:
		beta = [f + g for f, g in zip(start_weights, direction)]
	assert len(beta) == len(start_weights)

	length = sqrt(sum([(b-a) ** 2 for a, b in zip(alpha, beta)]))
	if length < epsilon:
		return alpha

	lambda1 = [ a + 0.382 * (b - a) for a, b in zip(alpha, beta) ]
	lambda2 = [ a + 0.618 * (b - a) for a, b in zip(alpha, beta) ]
	flambda1 = func(lambda1)
	flambda2 = func(lambda2)

	if flambda1 > flambda2:
		return line_search(func, lambda1, alpha, lambda2, direction, epsilon, 0.618 * step_size)
	elif flambda1 == flambda2:
		midpoint = [l1 + 0.5 * (l2 - l1) for l1, l2 in zip(lambda1, lambda2)]
		return line_search(func, midpoint, lambda1, lambda2, direction, epsilon, 0.618 * step_size)
	elif flambda1 < flambda2:
		return line_search(func, lambda2, lambda1, beta, direction, epsilon, 0.618 * step_size)

def objective(weights):
	weights_dict = {}
	weights_dict[u'p(e)'] = weights[0]
	weights_dict[u'p(e|f)'] = weights[1]
	weights_dict[u'p_lex(f|e)'] = weights[2]
	hyps = genHyps(weights_dict)
	return score(hyps)

Tune = False
if True:
	best_weights = [0.0, 0.0, 0.0]
	best_score = objective(best_weights)
	step_size = 20.0
	i = 1
	while True:
		new_weights = line_search(objective, best_weights, step_size=step_size)
		new_score = objective(new_weights)
		step_size *= 0.618
		if new_score >= best_score:
			best_weights = new_weights
			best_score = new_score
		print >>sys.stderr, "Iteration %d weights:" % i
		print >>sys.stderr, new_weights
		print >>sys.stderr, "Approximate meteor score: %f" % new_score
		i += 1
else:
	weights = { u'p(e)': 0.0, u'p(e|f)': 0.0, u'p_lex(f|e)': 0.0 }
	# -0.0313291224018224, 0.30109472699444484, 0.06739491027847236 (test)
	# -0.2072799533957068, 0.1783074171714089, -0.1521789620169004	(dev)
	#weights = { u'p(e)': -0.264376817381104, u'p(e|f)': 0.0001921555630649517, u'p_lex(f|e)': -0.12154748113750564 }	
	hyps = genHyps(weights)
	for hyp, _ in hyps:
		print hyp.encode('utf-8')
	print >>sys.stderr, "Approximate meteor score: %f" % score(hyps)
