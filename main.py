import numpy as np
import sys
from scipy import sparse
from timeit import default_timer as timer
import itertools
import resource


def load_data(file_location):
    """
    Load in .npy file and creates a sparse matrix using scipy's sparse module. Every user movie combination in the file
    obtains a '1' the rest is '0'.
    """
    # load in data
    print("Loading the data..")

    # first column is user IDs, second column is movie IDs
    data = np.load(file_location)

    # Finding the total amount of users and total amount of movies rated
    user_array = data[:, 0]
    movie_array = data[:, 1]

    # find the largest user and movie ID
    max_user_id = np.max(user_array)
    max_movie_id = np.max(movie_array)

    # Create a sparse matrix of (movies by users) fill in 1's if user rated
    # the movie
    col = user_array  # user IDs
    row = movie_array  # movie IDs
    # python counts from 0; 1st user or 1st movie are 0th user and 0th movie
    # in python
    col -= 1
    row -= 1

    # if a user rated a movie put into the sparse matrix a '1'
    values = np.ones(len(row))

    # Creation of the sparse matrix by usage of scipy's sparse package
    # It is forced to be a boolean because we only have '0' and '1's more
    # information is not needed. Less memory usage
    sparse_data = sparse.csc_matrix(
        (values, (row, col)), shape=(max_movie_id, max_user_id), dtype='b')

    return sparse_data, max_user_id, max_movie_id


def minhashing(sparse_data, max_user_id, max_movie_id, user_seed):
    """
    create the signature matrix with minhashing. By usage of random permutations of the rows of the sparse
    data matrix
    """
    print('minhashing in progress..')

    total_permutation = 100

    # allocate memory, force to int32, will only need to maximally count up to
    # max user ID
    signature_matrix = np.zeros(
        (total_permutation, max_user_id)).astype('int32')
    for i in range(total_permutation):
        # set the random seed such that our results are repeatable, however we need to change each loop to obtain
        # different permutations
        random_seed = int(i * 242 / 2 + user_seed)
        np.random.seed(random_seed)

        # new row order according to the random permutation
        row_order = np.random.permutation(max_movie_id)
        row_order = tuple(row_order)  # Convert to a tuple for slicing action

        # Swap the sparse matrix rows with rowOrder
        new_sparse = sparse_data[row_order, :]

        # Finding the position of the first '1' in each column and put the
        # position values into the signature matrix
        for j in range(maxUserID):
            ar = new_sparse.indices[new_sparse.indptr[
                j]:new_sparse.indptr[j + 1]].min()
            signature_matrix[i, j] = ar

    return signature_matrix, total_permutation


def lsh_algorithm(signature_matrix, total_permutation):
    """
    create the buckets with local sensitive hashing with banding. Also immediately find the unique candidate pairs over
    all the created buckets with a similarity larger than 0.5 with the signature matrix.
    """
    print("Running LSH..")

    # LSH with banding
    n_bands = 20
    n_rows = total_permutation / n_bands

    if total_permutation % n_bands != 0:
        sys.exit('Set n_bands such that n_bands * nrows = totalPermutations (rows signature matrix)); now a band '
                 'contains less rows')

    # initialize bucket as a list, it is a list because of the different size
    # bucket tuples
    bucket = []

    # Iterator variable
    current_row = 0
    for itBands in range(n_bands):
        # creation band
        band = signature_matrix[current_row:int(n_rows) + current_row, :]
        current_row += int(n_rows)

        # obtain a bucket array in which duplicate vectors in the band are put
        # into the same bucket; the candidate pairs
        ids = np.ravel_multi_index(band.astype(
            int), band.max(1).astype(int) + 1)
        sidx = ids.argsort()
        sorted_ids = ids[sidx]
        bucket_array = np.array(np.split(sidx, np.nonzero(
            sorted_ids[1:] > sorted_ids[:-1])[0] + 1))

        # Only record the buckets with more than 1 user in it
        for position in range(len(bucket_array)):
            if len(bucket_array[position]) > 1:
                bucket.append(bucket_array[position])

    # Remove buckets with exactly the same tuples
    x = map(tuple, bucket)
    bucket = set(x)
    bucket = list(bucket)

    # finding the unique candidate pairs with a similarity larger than 0.5 in the signature matrix
    # note that this also counts (3,5) and (5,3) separately. This double counting
    # is removed later on during creation of the txt file
    unique_set = set()
    for i in range(len(bucket)):
        # generate a generator expression for the combinations of the pairs in
        # a bucket
        large_user_pair = set(
            pair for pair in itertools.combinations(bucket[i], 2))

        large_user_pair = large_user_pair.difference(unique_set)
        for j in large_user_pair:
            sim = signature_similarity(
                j[0], j[1], signature_matrix)
            if sim > 0.5:
                unique_set.add(j)

    return unique_set


def jaccards_similarity(user1, user2, sparse_matrix):
    """     Calculate and return the Jaccard similarity between two users (user1 and user2) with the sparse matrix   """
    sum_val = np.sum(sparse_matrix[:, user1] & sparse_matrix[:, user2])
    sim_val = np.sum(sparse_matrix[:, user1] | sparse_matrix[:, user2])
    jacard_sim = float(sum_val) / float(sim_val)
    return jacard_sim


def signature_similarity(user1, user2, signature_matrix):
    """    Calculate and return the similarity between two users (user1 and user2) with the signature matrix    """
    similar = float(np.count_nonzero(signature_matrix[:, user1] == signature_matrix[:, user2])) \
        / len(signature_matrix[:, user1])
    return similar


def output(original_sparse, unique_set):
    """
    Create the txt file with the candidate pairs that have a real jaccard similarity larger than 0.5
    :param original_sparse -- the original sparse matrix
    :param unique_set -- the unique set found with banding of which we calculate the jaccard similarity
    """
    print("Outputing results.. ")

    # make from the sparse array a real array, such that we now also put into
    # memory the '0's.
    sparse_array = original_sparse.toarray()

    # order the set on the first element of the tuples, iterating over a list is faster than over a set
    # However the in function is slower with a list, but this is done less
    # often than the iterations
    original_unique_set = unique_set
    unique_set = sorted(unique_set)

    # empty list which we append the found pairs, so that we can sort at the end again; needed because
    #  user2 can > user1
    user_pair_list = []
    # check if the similarity is really > 0.5 with the jaccard similarity and
    # add to the txt file if user1<user2
    for pair in unique_set:
        # if user1 < user2 and jaccard similarity > 0.5 add to txt file
        if pair[0] < pair[1]:
            sim = jaccards_similarity(pair[0], pair[1], sparse_array)
            if sim > 0.5:
                # add +1 to users because we started counting from 0 in python
                user_pair_list.append((pair[0] + 1, pair[1] + 1))

        # if user 2 is larger than user 1 and combine (user2, user1) is already in unique_set continue with loop
        # else calculate similarity
        elif pair[0] > pair[1]:
            # if pair is already in set skip it and go into next iteration for loop; E.g. (3,1) is same as (1,3) thus
            #  skip it
            if (pair[1], pair[0]) in original_unique_set:
                continue
            # if this is note the case add it with user 2 at position user 1, such that the txt file's user1 is always
            # smaller than user 2
            else:
                sim = jaccards_similarity(pair[0], pair[1], sparse_array)
                if sim > 0.5:
                    # add +1 to users because we started counting from 0 in
                    # python
                    user_pair_list.append((pair[1] + 1, pair[0] + 1))

    # sort user pair list on first user
    user_pair_list = sorted(user_pair_list)

    # write to txt file
    with open('results.txt', 'w') as f:
        f.write('\n'.join('%s,%s' % user_pair for user_pair in user_pair_list))
    f.close()
    print('User-Pair found: ', len(user_pair_list))


if __name__ == '__main__':

    start_time = timer()

    # read in via command line random seed and file
    if len(sys.argv) < 3:
        raise ValueError("incorrect arguments\n"
                         "  how to use: python %s RANDOM_SEED FILE_LOCATION_FILE_NAME" % sys.argv[0])
    userSeed = int(sys.argv[1])
    fileLocation = sys.argv[2]

    # load in data, obtain sparse matrix and the max user/movie ID in file
    sparseData, maxUserID, maxMovieID = load_data(fileLocation)

    # make a copy for later use; such that no magical python things happen
    originalSparse = sparseData

    # create the signature matrix
    signMatrix, totalPermutation = minhashing(
        sparseData, maxUserID, maxMovieID, userSeed)

    # calculate with Local sensitive hashing with banding the buckets and immediately calculate the unique candidate
    # pairs set that have a similarity larger than 0.5 by using the signature
    # matrix.
    uniqueSet = lsh_algorithm(signMatrix, totalPermutation)

    # check if the found candidate pairs in unique set really have a jaccard similarity > 0.5 by calculation with the
    #  sparse matrix. If it has a jaccard similarity > 0.5 write to txt file.
    output(originalSparse, uniqueSet)

    elapsed = timer()
    mem_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("Run time (Seconds): " + str(elapsed - start_time))
    print("Memory: " + str(mem_usage / 1000) + " MB")
