# Locality Sensitive Hashing
LSH implmentation for Advances In Data Mining course at Leiden University.

# Motivation
- About 100.000 users that watched in total 17.770 movies;
- Each user watched between 300 and 3000 movies
- The file contains about 65.000.000 records (720 MB) in the form: <user_id, movie_id> : “user_id watched movie_id”
- Similarity between users: Jaccard similarity of sets of movies they watched:
- jsim(S1, S2) = intersect(S1, S2)/ union(S1, S2)
- find (with help of LSH) pairs of users whose jsim > 0.5 (brute-force search too expensive: 5.000.000.000 pairs)

# Task
* Implement the LSH algorithm with minhashing and apply it to the user_movie.npy (not included)
* The output of the algorithm should be written to a text file, as a list of records in the form u1,u2 (two integers separated by a comma), where u1<u2 and jsim(u1, u2)>0.5.
* Find pairs of users whose similarity is at least 0.5.
* Program will rely on random number generators, set explicitly in the code the random seed to a value that will make reproduction of your results possible.
* Tune it (signature length, number of bands, number of rows per band)
* Randomize, optimize, benchmark, polish the code, ...

# Grading
* A working code that produces valid results in < 30 min: 6.0.
⋅⋅* The total number of found pairs (over 5 different runs),
⋅⋅* The median run time (over 5 different runs),
⋅⋅* The average number of found pairs per minute,
..* code readability, elegance.

