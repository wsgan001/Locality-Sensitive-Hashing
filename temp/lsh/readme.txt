This folder contains several functions and scripts for experimenting with LSH:

demo_minhashing:
a script that demonstrates and application of LSH to a collection of all non-empty subsets of {1, 2, ..., 10},

========LSH functions========

minhash
a function that takes a binary matrix x that represents some sets (one set per column) and a permutation of rows of x, p,  and returns a vector of minhashes.

minhash_sig 
a function that creates signatures of length k for a data matrix x

banding
the main function that, given a matrix of signatures, the number of bands and rows, calculates corresponding buckets

jsim
calculates the Jaccard similarity between two vectors


plot_sim_prob
plots the similarity vs. probability curve for various values of n and b

=====Additional functions=========
gen_sets
generates all non-empty subsets of {1, 2, ..., k}

