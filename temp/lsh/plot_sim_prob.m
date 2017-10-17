function [s, p]=plot_sim_prob(n, b)

%plots the s-shaped curve that expresses the relation between the "true"
%similarity s and the chance of being detected (found in the same bucket)
%by LSH b-bands techinque.

%W. Kowalczyk

r=round(n/b);
if n~=r*b
    warning('adjust the number of bands!')
end
s=0:0.01:1;
p=1-(1-s.^r).^b;
plot(s,p)
xlabel('Similarity s')
ylabel('Probability of detection')
title(['n=' num2str(n) '; b=' num2str(b) '; r=' num2str(r)])
