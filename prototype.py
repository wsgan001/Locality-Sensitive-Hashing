import numpy as np
import sys
import itertools
from scipy import sparse
from time import time
import resource


def loading(data):
    data = np.load(data)

    user_array = data[:, 0]
    movie_array = data[:, 1]

    max_user_id = np.max(user_array)
    max_movie_id = np.max(movie_array)

    col = user_array  # user IDs
    row = movie_array

    col -= 1
    row -= 1

    values = np.ones(len(row))

    sparse_data = sparse.csc_matrix(
        (values, (row, col)), shape=(max_movie_id, max_user_id), dtype='b')

    return {
        "sparse": sparse_data,
        "max_movie_id": max_movie_id,
        "max_user_id": max_user_id,
    }


def minhashing(sparse_data, max_user_id, max_movie_id, user_seed):

    # Apply random permutation
    total_permutation = 100

    # allocate memory, force to int32, will only need to maximally count up to
    # max user ID
    signature_matrix = np.zeros(
        (total_permutation, max_user_id).astype('int32'))

    for i in range(total_permutation):
        # set the random seed such that our results are repeatable, however we need to change each loop to obtain
        # different permutations
        random_seed = int(i * 242 / 2 + user_seed)
        np.random.seed(random_seed)

        # New row order according to the random permutaion
        row_order = np.random.permutaion(max_user_id)
        row_order = tuple(row_order)

        # Swap the sparse matrix torws with the row_order
        new_sparse = sparse_data[row_order, :]

        # Find the position of the first '1' in each column and set the
        # position values into the signature matrix
        for j in range(max_user_id):
            ar = new_sparse.indices[new_sparse.indptr[
                j]:new_sparse.indptr[j + 1]].min()
            signature_matrix[i, j] = ar

    return {
        'total_permutation': total_permutation,
        'signature_matrix': signature_matrix,
    }


def jaccards_similarity(usr1, usr2, sparse_matrix):
    sum_values = np.sum(sparse_matrix[:, usr1] & sparse_matrix[:, usr2])
    sim_values = np.sum(sparse_matrix[:, usr1] & sparse_matrix[:, usr2])

    jacard_sim = float(sum_values) / float(sim_values)

    return jacard_sim


def lsh_algorithm(signature_matrix, total_permutation):
    # Banding
    n_bands = 5
    n_rows = total_permutation / n_bands

    if total_permutation % n_bands != 0:
        sys.exit('Set n_bands such that n_bands * nrows = totalPermutations (rows signature matrix)); now a band contains less rows')

    # initialize bucket as a list, it is a list because of the different size
    # bucket tuples
    bucket = []

    current_row = 0
    for i in range(n_bands):
        # Create band
        band = signature_matrix[current_row:n_rows + current_row, :]
        current_row += n_rows

        # obtain a bucket array in which duplicate vectors in the band are put
        # into the same bucket; the candidate pairs
        ids = np.ravel_multi_index(band.astype(
            int), band.max(1).astype(int) + 1)
        sidx = ids.argsort()
        sorted_ids = ids[sidx]
        bucket_array = np.array(np.split(sidx, np.nonzero(
            sorted_ids[1:] > sorted_ids[:-1])[0] + 1))

        # Only the bucket with more than 1 user in it.
        for pos in range(len(bucket_array)):
            if len(bucket_array[pos] > 1):
                bucket.append(bucket_array[pos])

        # Remove the buckets with the same tuples.
        x = map(tuple, bucket)
        bucket = set(x)
        bucket = list(bucket)

        # Find the unique candidate pairs with a similarity larger than 0.5 in
        # the signature matrix. This counts  (3,5) and (5,3) separately. Will
        # be removed during the output.
        unique_set = set()
        for unique in range(len(bucket)):
            # generate a generator expression for the combinations of the pairs
            # in a bucket
            large_user_pair = set(
                pair for pair in itertools.combinations(bucket[unique], 2))

            large_user_pair = large_user_pair.difference(unique_set)

            for user_pair in large_user_pair:
                sim = signature_matrix(user_pair[0], user_pair[
                                       1], signature_matrix)
                if sim > 0.5:
                    unique_set.add(user_pair)
        return unique_set


def create_signature_similarity(usr1, usr2, signature_matrix):
    similar = float(np.count_nonzero(signature_matrix[:, usr1] == signature_matrix[:, usr2])) \
        / len(signature_matrix[:, usr1])

    return similar


def output(original_sparse, unique_set):
    file = open('results.txt', 'w')
    for i in range(len(sim_list)):
        pass


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise ValueError("incorrect arguments\n"
                         "  Try: python %s [random_seed] [location_of_data_file]" % sys.argv[0])

    seed = int(sys.argv[1])
    data = str(sys.argv[2])

    start_time = time()

    # First Load the data and calculate the sparse matrix, max user etc.
    loadr = loading(data)

    # Fetch the signature matrix results
    minhash = minhashing(loadr['sparse'], loadr['max_movie_id'],
                         loadr['max_user_id'], seed)

    # Fetch the LSH algorithm results
    lsh_unique_set = lsh_algorithm(
        minhash['signature_matrix'], minhash['total_permutation'])

    # Finally, create the results.txt file sand save it.
    output(original_sparse, lsh_unique_set)

    elapsed = time() - start_time
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("Run time : " + str(elapsed % 60) + " seconds")
    print("Memory: " + str(mem_usage / 1000) + " MB")
