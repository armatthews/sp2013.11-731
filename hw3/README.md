My decoder recursively decodes each span of the input, and combines them to form translations of bigger parts.
Any span [i,j) may be translated as the translation of [i,k) plus the translation of [k,j), or the translation of [k,j) plus the translation of [i,k) for any k between i and j.
For each span we maintain a list of the top s hypotheses.

I also implemented a similar idea that allows the span [i,j) to be broken into any three pieces, which can freely reorder.
I then combined these two approaches by taking the output that had the better model score for each sentence.

Next, I made my code generate an n-best list, and graded each of the n-best individually, taking the best according to the grading script, rather than according to my model.

Finally, I combined my output with the output of other strong systems, including those of Yulia, Manaal/Waleed, and Victor.
