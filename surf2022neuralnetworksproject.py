# -*- coding: utf-8 -*-
"""SURF2022NeuralNetworksProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14LFWV2IDqEMu6nVYVUgYKscAPrXOB0HM
"""

import json
import pandas as pd
import numpy as np
from functools import reduce
from itertools import combinations
from pprint import pprint


from google.colab import drive
drive.mount('/content/drive')

!pip install requests
import requests
# Save datagenerators as file to colab working directory
# If you are using GitHub, make sure you get the "Raw" version of the code
url = 'https://raw.githubusercontent.com/dlukes/rbo/master/rbo.py'
r = requests.get(url)

# make sure your filename is the same as how you want to import 
with open('rbo.py', 'w') as f:
    f.write(r.text)

# now we can import
import rbo as r

#list all the runs/topics I will be using 
topics=['447']
runNames=['bm25','att99atde','apl8p','bm25+rm3','monobert_maxp.msmarcov1-0shot','ok8alx','orcl99man','READWARE2','tct_v2','unicoil-d2q']

DocumentNamesForEachRun=[]

#Creates a 2d identity matrix
Matrix = np.identity(10)

#Creates an empty RBO matrix
RBOMatrix= pd.DataFrame(Matrix);
RBOMatrix.columns = ['bm25','att99atde','apl8p','bm25+rm3','monobert_maxp.msmarcov1-0shot','ok8alx','orcl99man','READWARE2','tct_v2','unicoil-d2q']
RBOMatrix.index = ['bm25','att99atde','apl8p','bm25+rm3','monobert_maxp.msmarcov1-0shot','ok8alx','orcl99man','READWARE2','tct_v2','unicoil-d2q']

relevance=pd.read_csv('/content/drive/MyDrive/josh/qrels/trec8redux/qrels-expanded', delim_whitespace=True, names=['topic', '0', 'docid','relevance'],usecols = ['topic', 'docid','relevance'])
#stores all documents that are relevant 
relevant=relevance.loc[relevance['relevance'] == 1]
#print("relevant")
#print(relevant)

apsForTopics=[]
allScores=[]
topicsAps = pd.DataFrame(columns=['Run', 'Score'])
listOfAveragePrecisionScores=[]
listofP10=[]
listofrecall1000=[]

#loops through and recieves all the precision scores for each of the runs which are located in the trec8redux folder
for run in runNames:
  averagePrecisionScores=pd.read_csv('/content/drive/MyDrive/josh/evals/trec8redux/'+run, delim_whitespace=True, names=['Characteristics', 'Topics', run])
  averagePrecisionScores=averagePrecisionScores.loc[averagePrecisionScores['Characteristics'] == 'map']
  allScores.append(averagePrecisionScores[averagePrecisionScores['Topics'] == 'all'][run].tolist()[0])
  listOfAveragePrecisionScores.append(averagePrecisionScores.drop(columns=['Characteristics']))

  P_10=pd.read_csv('/content/drive/MyDrive/josh/evals/trec8redux/'+run, delim_whitespace=True, names=['Characteristics', 'Topics', run])
  P_10=P_10.loc[P_10['Characteristics']=='P_10']
  listofP10.append(P_10.drop(columns=['Characteristics']))
  recall_1000=pd.read_csv('/content/drive/MyDrive/josh/evals/trec8redux/'+run, delim_whitespace=True, names=['Characteristics', 'Topics', run])
  recall_1000=recall_1000.loc[recall_1000['Characteristics']=='recall_1000']
  listofrecall1000.append(recall_1000.drop(columns=['Characteristics']))


p10=reduce(lambda x, y: pd.merge(x, y, on = 'Topics'), listofP10)
recall1000=reduce(lambda x, y: pd.merge(x, y, on = 'Topics'), listofrecall1000)
aps=reduce(lambda x, y: pd.merge(x, y, on = 'Topics'), listOfAveragePrecisionScores)
print("aps")
print((aps.loc[[46]]))
print("p10")
print((p10.loc[[46]]))
print("recall1000")
print((recall1000.loc[[46]]))
#print("average precision scores")
#print(reduce(lambda x, y: pd.merge(x, y, on = 'Topics'), listOfAveragePrecisionScores))
  
#print("average precision scores for each run ")
ScorePerTopic = pd.DataFrame(list(zip(runNames, allScores)), columns=['Run','Score'])
#print(ScorePerTopic)



for topic in topics:
  dfContent=[]
  for runs in runNames:
    dfContent.append(pd.read_csv('/content/drive/MyDrive/josh/runs/trec8redux/'+runs+'/t'+topic, delim_whitespace=True, names=["Topic_"+runs, "BoilerPlate_"+runs, "DocumentName_", "Ranking_"+runs, "Score_"+runs, "Type_"+runs], usecols = ["DocumentName_", "Ranking_"+runs, "Score_"+runs]).head(20))

  for run, df in zip(runNames, dfContent):
    DocumentNamesForEachRun.append((run, df.iloc[:, 0].tolist()))

  print("RBO Matrix for "+topic)
  for a,b in (list(combinations(DocumentNamesForEachRun, 2))):
    #print(a[0],b[0])
    min,res,ext=r.rbo(a[1], b[1], p=.9)
    #print(min)
    if(min>=0.4):
      RBOMatrix.loc[a[0],b[0]]=min
      RBOMatrix.loc[b[0],a[0]]=min

  #sets RBO matrix diagonal to one
  RBOMatrix.values[[np.arange(RBOMatrix.shape[0])]*2] = 1
  print(RBOMatrix)

  df_merged = reduce(lambda  left,right: pd.merge(left,right,on='DocumentName_',how='outer'), dfContent).dropna()
  print("Common Retrieved for "+topic)
  print(df_merged)
  df_merged.drop([col for col in df_merged.columns if 'Score' in col],axis=1,inplace=True)



  unique=[]
  #only in one but not others-set difference-(relevance in one run-union relevance in all other runs)
  for i in range(len(runNames)):
    #create copy to not work with original list and gets the relevance for all the runs except the run on
    df_relevance_union= pd.concat(dfContent[:i].copy() + dfContent[i+1:].copy(),ignore_index=True).drop_duplicates()
    #gets relevance from the run on
    df_relevance_in_one_run=dfContent[i]
    #Computes the set difference (relevance in one run-union relevance in all other runs). This only drops the duplicates in the column
    #documentNames_ using subset instead of the entire row
    set_diff_df = pd.concat([df_relevance_in_one_run, df_relevance_union, df_relevance_union]).drop_duplicates(subset='DocumentName_', keep=False)
    #appends dataframes and drops all nan columns
    unique.append(set_diff_df.dropna(axis=1, how='all'))


  uniqueNonRelevanceRetrieved=[]
  uniqueRelevanceRetrieved=[]
  relevantGroupedBasedOnTopic = relevant.groupby(relevant.topic)
  for dataframe in unique:
    #check if dataframe is not empty because empty dataframes do not have DocumentName_ attribute
     if not dataframe.empty:
      #if the document's docid is not one then append it to uniqueNonRelevanceRetrieved else append it to uniqueRelevanceRetrieved
      uniqueNonRelevanceRetrieved.append(dataframe.drop(dataframe[dataframe.DocumentName_.isin(relevantGroupedBasedOnTopic.get_group(int(topic))['docid'])].index))
      uniqueRelevanceRetrieved.append(dataframe.drop(dataframe[~dataframe.DocumentName_.isin(relevantGroupedBasedOnTopic.get_group(int(topic))['docid'])].index))

  print("Unique Relevance Retrieved for topic "+topic)
  #removes empty dataframe
  pprint(list(filter(lambda df: not df.empty, uniqueRelevanceRetrieved)))
  print("Unique NonRelevance Retrieved for topic "+topic)
  #removes empty dataframes
  pprint(list(filter(lambda df: not df.empty, uniqueNonRelevanceRetrieved)))

  
  
  #aps -how well the system did

