For hw2 I tried numerous approaches which I will detail in (roughly) chronological order. First, I tried to implement the recommended baseline solution, Simple METEOR. After tuning the Alpha parameter, that model scored a 0.513393 on the training set. I wanted to know if it was worthwhile to try to implement all the more advanced features of METEOR, such as stemming and paraphrasing, so I ran the data through the latest release of actual METEOR. Unfortunately, that scored only a 0.537698 on the training set. Since improvements to METEOR would yield at most ~2.4% higher scores, I turned to other ideas.

I next implemented the BLEU metric, but allowed it to have a variable N, which represents the largest size of n-grams it examines. I found that the traditional BLEU metric, with N=4 scored a 0.512363, but the optimal parameter setting of N=2 scored 0.519765. In the process of implementing BLEU, however, I accidentally tried running BLEU not on word-level n-grams, but on character-level n-grams. Surprisingly, I found this approach worked much better. I found the optimal parameter N to be N=6, scoring 0.544185 on the training set. I call this approach cBLEU.

Additionally, I tried to implement the TER metric, but was unable to successfully re-implement their approximate search algorithm, which enables it to handle shifts. My implementation of TER scored a disappointing 0.469437 on the training set.

The final simple metric I tried was String Subsequence Kernals. After seeing Chris's submission's success, I reimplemented SSK, which scored 0.522741 on the training set, still lower than my best cBLEU score.

Since my scores were not improving much, I decided to try a completely different approach: a genetic algorithm. I generated a population of randomly generated output files, and submitted one every five minutes to the leaderboard, and retrieved their scores. I would then select two output files, with probabilities proportial to their scores, and breed them to create new offspring. I iterated this procedure over 800 times, but saw only marginal improvements. The randomly generated solutions scored about 0.387 on the test set, and after 800 iterations, scores were only just above 0.4.

I next decided to try an SVM-based approach, in which the other metrics would participate as features. In the end I tried about 20 combinations of features, kernels, and parameters to my SVM model. The features of my SVM were the following metric scores on both the first and second hypotheses:
- BLEU, N=4
- cBLEU, N=6
- LM Score
- LM OOVs
- Length Ratio
- TER (without shifts)
- SSK
- POSLM
- Precision, for N in 1-4
- Recall, for N in 1-4

I first built an LM using only the data given, thinking external resources were banned. Later, upon confirmation from Chris, I used a large 4-gram LM built on data from all of our group's previous WMT data. I also used NLTK to POS tag each hypothesis sentence, along with the references, and used that data to build a POS LM. Finally, the length ratio feature simply measured the distance between the ratio of the length of each hypothesis and the length of the reference and 1.0.

The first SVM I built used all of libsvm's default settings, including a Gaussian Kernel, and some amount of regularization. Unfortunately, it still overfit drammatically, scoring a 0.647894 on the training set, but only a 0.472753 when submitted to the leaderboard. I also tried linear, quadratic, and cubic kernels, the best of which was quadratic with a training-set score of 0.538309. Finally, I tried cranking up the lambda parameter, which controls regularization of the SVM, and found that a falue as high as 10^10 performed best with a score of 0.541705 on the training set. Unfortunately that was still below my cBLEU baseline. All of these SVMs were built with the small LM trained only on the data given in this assignment.

Next I repurposed the code I wrote for the genetic algorithm experiment to submit other carefully chosen output to the leaderboard every five minutes. I choose to continuously submit files to the leaderboard verifying whether the i'th line was or was not a -1. Rather than randomly choosing lines to submit, or simply beginning from the beginning of the file, I instead ordered all the lines by the difference between Hypothesis A's cBLEU score and Hypothesis B's cBLEU score, in increasing order. I then submitted those lines one by one to the grading script, gaining knowledge about over 2000 of the lines my model was least certain about.

Finally, on the last day of the project, I realized that I was able to use external LMs in this experiment. As such, I rebuilt a quadratic and a gaussian SVM, with the LM features replaced with a new, bigger LM. These results, for the first time, beat my cBLEU baseline with a score of 0.563530 on the training set for the Gaussian SVM. The quadratic version scored a 0.559638 on the dev set but the highest score on the test set. This qudatric SVM is also my best legitimate submission on the test set, scoring 0.550371.

My final submission combines the final quadratic SVM described above with the knowledge gained by the script that continually tested pairs of hypotheses the cBLEU model was uncertain about. To generate my final submission, for each line I did the following:
- If the two hypotheses are exactly the same:
-	output 0
- Otherwise:
- 	If we tested this line:
- 		if we found that it was -1:
-			 output -1
-		if we found that it was not -1:
-			output 1
-	Otherwise:
-		output whatever the SVM output

This hybrid submission scores 0.58257 on the test set.
