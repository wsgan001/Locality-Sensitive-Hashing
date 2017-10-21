import numpy as np
import sys
import itertools
from scipy import sparse 
from time import time

start_time = time()





# users = 103703
# matrix = np.empty([100, users], dtype=int)

for m in range(len(input_data)):
    matrix[input_data[m][1]][input_data[m][0] - 1] = 1
    # print(matrix[input_data][m][1])

num_hash = 25

h = np.empty([num_hash, 17770], dtype=int)
for i in range(num_hash):
    h[i] = np.random.permutation(17770)


sig = np.empty([num_hash, 17770], dtype=int)
for i in range(num_hash):
    counting = 0
    for j in range(17770):
        if counting < (users - 20):
            for u in range(users):
                if matrix[h[i][j][u]]:
                    if not sig[i][u]:
                        sig[i][u] = j + 1
                        counting += 1
        else:
            break


def jsim(sig1, sig2, u1, u2):
    com = np.sum(sig1 == sig2)
    sim = float(com) / (2 * num_hash - com)
    if sim > 0.5:
        sim_list[u1].append(u2)


sim_list = [[] for x in range(users)]
band = 5
row = 5
buckets = 5000
sim_count = 0

for i in range(band):
    table = [[] for x in range(buckets)]
    for j in range(users):
        sigs = 0
        for r in range(row):
            sigs += sig[r + i * row][j]
        bucket = sigs
        table[bucket].append(j)
    for b in range(buckets):
        lb = len(table[b])
        if lb > 1:
            for c, d in itertools.combinations(table[b], 2):
                jsim(sig[:, c], sig[:, d], c, d)
real_count = 0


"""
Checking the real similarity and outputing the results
"""
file = open('results.txt', 'w')
for i in range(len(sim_list)):
    sim_list[i] = list(set(sim_list[i]))
    for j in sim_list:
        col1 = matrix[:, i].nonzero()
        col2 = matrix[:, j].nonzero()
        intersect = len(np.intersect1d(col1, col2))
        total = intersect + len(np.setxor1d(col1, col2))
        sim = float(intersect) / total

        if sim > 0.5:
            real_count += 1
            file.write(str(i + 1) + ", " + str(j + 1) + "\n")
file.close()


print("Program took %s seconds to execute" % (time() - start_time))
