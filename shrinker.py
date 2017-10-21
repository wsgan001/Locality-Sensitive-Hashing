import os, sys
import numpy as np
data = 'data/user_movie.npy'
small = 'data/small_user_movie.npy'

in_file = np.load(data)

# contents = in_file.read()
i = 0
with open(small, 'w') as f:
	while i < 500:
		# line = in_file.readline()

		# line = f.readline()
		f.write(str(in_file))
		i+=1
f.close()


	