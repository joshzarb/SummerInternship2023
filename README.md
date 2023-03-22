# SURF2022 Neural Networks Project
The code in this repository is designed to calculate Ranked Biased Overlap (RBO) scores between different retrieval models for a given set of topics in the trec8redux collection. The code reads in data from different files (such as relevance judgements and retrieval results), performs various data manipulations, and outputs a matrix of RBO scores.

The code requires pandas, numpy, requests, and pprint python modules to run. The first step of the code is to mount a google drive, which allows the code to access necessary files. The code also downloads and imports the rbo.py file which contains the implementation of the RBO function. The code then specifies the set of topics to use, and lists the retrieval models that will be compared.

The code reads in relevance judgements from a file, and uses these to identify relevant documents. It then loops through each of the retrieval models and reads in precision scores for each topic. It calculates the RBO score for each pair of retrieval models and outputs the result in the form of a matrix.
