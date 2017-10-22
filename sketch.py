import sys
import numpy as np
import itertools


seed = sys.argv[1]
route = sys.argv[2]

np.random.seed(seed=int(seed))

input_data = np.load(route)

users = 103703
matrix = np.empty([17780, users], dtype=int)

# Generating the sparse matrix
for m in range(len(input_data)): 
    matrix[input_data[m][1]][input_data[m][0]-1] = 1 

# Generating hash functions by permuting
number_hash = 25
h = np.empty([number_hash,17770], dtype=int)
for i in range (number_hash):
    h[i] = np.random.permutation(17770)

# Converting sparse matrix to signature matrix：
# Here we use the trick of considering the permutated vector as the indexes of the sorted hash function.
sig = np.empty([number_hash, users], dtype=int)
for i in range (number_hash): 
    counting = 0
    for j in range (17770): # Looping through the hash signatures to find the smallest one
        if counting < (users-20): 
         # Because we consider the permutation to already be sorted, if all the users have a signature, we break the loop 
            for u in range (users): # Looping through the users
                if matrix[h[i][j]][u]:
                    if not sig[i][u]:                
                        sig[i][u] = j + 1
                        counting+=1
        else:
            break

# Function which tests the similarity of the pair of signatures and if it's >0.5 we store it in list sim_list
def similarity(sig1, sig2, u1, u2):
    com = np.sum(sig1 == sig2)
    sim =  float(com)/(2*number_hash - com)
    if sim>0.5:
        sim_list[u1].append(u2)

# LSH implementation
sim_list = [[] for x in range (users)]
band = 5
row = 5
buckets = 5000
sim_count = 0


for i in range (band):
    table = [[] for x in range(buckets)] 
    # Sum the signatures of each user in the band and use that as the bucket number   
    for j in range (users):
        sigs = 0
        for r in range (row):
            sigs += sig[r+i*row][j]
        bucket = sigs
        table[bucket].append(j)
    # For each bucket we check the similarities of all the pairs within that bucket
    for b in range (buckets):
        lb = len(table[b])
        if lb>1:
            for c, d in itertools.combinations(table[b], 2):
                similarity(sig[:,c],sig[:,d], c, d)
real_count = 0

# Checking the real similarity and outputing the results
f1 = open('results.txt','w')
for i in range (len(sim_list)):
    if len(sim_list[i])>0:
        sim_list[i] = list(set(sim_list[i]))
        for j in sim_list[i]:
            col1 = matrix[:,i].nonzero()
            col2 = matrix[:,j].nonzero()
            intersect = len(np.intersect1d(col1,col2))
            total = intersect + len(np.setxor1d(col1,col2))
        
            real_sim = float(intersect)/total
            if real_sim > 0.5:
                real_count += 1
                f1.write(str(i+1) + ", " + str(j+1) + "\n")
f1.close()