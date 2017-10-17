function m=minhash(x, p)
%Find minhash vector for data in x that corresponds to permutation p.

%permute rows of x:
y=x(p,:); 

%find positions of first 1's in each column:
[~, m]=max(y);

