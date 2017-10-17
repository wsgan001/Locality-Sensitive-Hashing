function sets=gen_sets(k)

%Generate all 2^k subsets of {1, ..., k}.
%Each subset is represented as a column vector of k bits.

%W. Kowalczyk, 21.02.2013
sets=zeros(k, 2^k-1);
for i=1:k
    sets(i, :)=bitget(1:2^k-1, i);
end

