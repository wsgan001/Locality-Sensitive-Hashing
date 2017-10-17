import numpy as np
import sys
import itertools


def min_hashing():
    return None


def lsh_algorithm():
    return None


def output(results):
    """
    Checking the real similarity and outputing the results
    """
    file = open('results.txt', 'w')
    for i in range(len(results)):
        results[i] = list(set(results[i]))
        for j in results:
            col1 = matrix[:, i].nonzero()
            col2 = mtrix[:, j].nonzero()
            intersect = len(np.intersect1d(col1, col2))
            total = intersect + len(np.setxor1d(col1, col2))
            sim = float(intersect) / total

            if sim > 0.5:
                count += 1
                file.write(str(i + 1) + ", " + str(j + 1) + "\n")
    file.close()


def main():
    seed = sys.argv[1]
    route = sys.argv[2]

    np.random.seed(seed=int(seed))
    input_data = np.load(route)


if __name__ == '__main__':
    main()
