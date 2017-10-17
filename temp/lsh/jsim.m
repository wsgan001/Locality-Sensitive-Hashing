function s=jsim(x,y)
%Calculate the Jaccard Similarity between 0-1 vectors x and y

%W. Kowalczyk, 21.02.2013
s=sum(x&y)/sum(x|y);
