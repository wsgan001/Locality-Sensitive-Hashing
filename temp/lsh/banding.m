function [bucket_id, bucket, sizes]=banding(signatures, n_bands, n_rows)

%This function takes as input a matrix of signatures (one signature per row)
%and two parameters: 
%
%   b: the number of bands, and
%   r: the number of rows per band.
%
%The product b*r must not exceed the length of signatures!
%
%
%

n_sets=size(signatures,2);
if n_bands*n_rows > n_sets 
    error('Number_of_bands x Number_of_rows is bigger than the length of signatures!')
end

%The array bucket_id will keep pointers to buckets; buckets will be stored
%in a cell array bucket. Thus: bucket_id(i,b) will be the pointer to a bucket 
%from band b which contains i and bucket{bucket_id(i,b)} will be a set of all 
%objects that belong to this bucket.

bucket_id=zeros(n_sets, n_bands); 
bucket=cell(n_bands, 1); 
sizes=cell(n_bands,1);
current_row=1; current_bucket=1;
bkts=cell(n_bands,1);
for b=1:n_bands
    block=signatures(current_row:current_row+n_rows-1,:)';
    current_row=current_row+n_rows;
    
    [sblock, pos]=sortrows(block);
    [ublock, last, POS]=unique(sblock,'rows');
    
    bkt=cell(length(last),1);
    bkt{1}=pos(1:last(1));
    for i=2:length(last)
        bkt{i}=pos(last(i-1)+1:last(i));
    end
    [ss, ind]=sort(pos);
    
    bucket_id(:,b)=POS(ind);
    bucket{b}=bkt;
    sizes{b}=diff([0; last]);
end

