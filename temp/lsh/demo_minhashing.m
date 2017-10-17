%This script demonstrates the process of finding similar sets with help 
%of the LSH banding technique. It generates all non-empty subsets of {1, ..., k},
%then calculates their minhashes and creates bins.

%W. Kowalczyk, 24.02.2013

clear all
close all

%Generate all non-empty subsets of {1, 2, ..., k}
k=10;
sets=gen_sets(k);
n_sets=size(sets,2) %number of subsets; should be 2^k-1

disp('Calculating the Jaccard similarities between sets...')
tic
S=zeros(n_sets);
for i=1:n_sets
    for j=1:n_sets
        S(i,j)=jsim(sets(:,i), sets(:,j));
    end
end
toc
%Visualize the distribution of S in several ways:

figure
plot(sort(S(:)));
xlabel('Sorted pairs of sets')
ylabel('Jaccard Similarity')

figure
hist(S(:))
xlabel('Histogram of Jaccaard Similarity')

figure
values=unique(S(:));
counts=histc(S(:), values);
bar(values, counts)
xlabel(['All ' num2str(length(values)) ' possible values of the Jaccard Similarity'] )
ylabel('Counts')

figure
imagesc(S);
colorbar;
axis square
title('Image of matrix S')

disp('Generating minhash signatures of length 100')
n_sig=100;
signatures=minhash_sign(sets, n_sig);

disp('Calculating an approximate similarity between sets')
disp('with help of signatures...')
tic
S_approx=zeros(n_sets);
for i=1:n_sets
    for j=1:n_sets
        S_approx(i,j)=mean(signatures(:,i)==signatures(:,j));
    end
end
toc

%Analyze the differences between S and S_approx
figure,
d=S(:)-S_approx(:);
hist(d,50)
xlabel('Differences between true and approx. similarity')
title(['Number of minhashes=' num2str(n_sig) '; Mean=' num2str(mean(d),4) '; Std=' num2str(std(d),4)]);

%Do the same, setting n_sig to 1000:
disp('Calculating an approximate similarity between sets')
disp('with help of signatures of length 1000...')

n_sig=1000;
signatures=minhash_sign(sets, n_sig);
tic
for i=1:n_sets
    for j=1:n_sets
        S_approx(i,j)=mean(signatures(:,i)==signatures(:,j));
    end
end
toc

figure,
d=S(:)-S_approx(:);
hist(d,50)
xlabel('Differences between true and approx. similarity')
title(['Number of minhashes=' num2str(n_sig) '; Mean=' num2str(mean(d),4) '; Std=' num2str(std(d),4)]);

%%===========
%Now the most tricky part: we calculate buckets and look at their stats...
n_sig=100;
signatures=minhash_sign(sets, n_sig);

disp(['Calculating all buckets and pointers to buckets'])
[bucket_id, bucket, sizes]=banding(signatures, 20, 5);

%Let's look at the sizes of buckets in band 1
figure, plot(sort(sizes{1}));
xlabel('Buckets sorted by size')
ylabel('Bucket size')

%Now the same, but with b=25, r=4 (to make the biggest bucket bigger).
[bucket_id, bucket, sizes]=banding(signatures, 25, 4);

%Let's look at the sizes of buckets in band 1
figure, plot(sort(sizes{1}));
xlabel('Buckets sorted by size')
ylabel('Bucket size')


%Find a bucket with most elements and look at the distribution of
%similarities of elements from this bucket


figure
xlabel('Jaccard Similarity')
ylabel('Signature Similarity')
axis square
hold on
BiggestBuckets=[];
for band=1:25
[bkt_size, bkt_id]=max(sizes{band});
disp(['Band ' num2str(band) '; biggest bucket size=' num2str(bkt_size)]);
sel=bucket{band}{bkt_id}; %elements from the biggest bucket from band 1
BiggestBuckets=union(BiggestBuckets, sel);
JS=zeros(bkt_size); %Jaccard similarity matrix
SS=zeros(bkt_size); %Similarity of Signatures
for i=1:bkt_size, 
    for j=1:bkt_size, 
        JS(i,j)=jsim(sets(:,sel(i)),sets(:, sel(j)));
        SS(i,j)=mean(signatures(:,sel(i))==signatures(:, sel(j)));
    end, 
end
plot(JS(:), SS(:), '.');
end
BiggestBuckets_size=length(BiggestBuckets)

