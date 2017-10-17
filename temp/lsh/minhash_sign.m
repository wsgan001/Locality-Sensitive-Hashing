function y=minhash_sign(x,k)

%Calculate signatures of length k of all sets represented by x.

%W. Kowalczyk, 24.02.2013
[n_row, n_col]=size(x);
%allocate memory:
y=zeros(k, n_col);

for i=1:k
    p=randperm(n_row);
    y(i,:)=minhash(x,p);
end 
