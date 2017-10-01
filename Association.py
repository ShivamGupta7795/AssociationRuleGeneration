"""
course: 		CSE 601 - Data Mining
date: 			09/28/09
developed by:	Jay Bakshi
				Shivam Gupta
				Debanjan Paul
filename:		Association.py
version:		1.3
description: 	This program computes frequent itemsets from genetic data for diseases using Apriori algorithm with pruning for performance improvements.
dependencies:	Pandas version: 	0.20.1 or greater
				
"""

#############################################################
# Imports
import pandas as pd
import itertools
import sys

#############################################################
# Pandas dataframe options set for proper display of 
# results of the final rules when queried.

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)

#############################################################
# File name taken as a command line parameter. Must be tab
# delimited and provided as appropriate.
# File is loaded into a pandas dataframe.

filePath = sys.argv[1]
geneData = pd.read_csv(filePath, sep='\t', lineterminator='\n', header=None)

#############################################################
# Imported file items are converted to appropriate item 
# names based on required output as required in documentation.

for i in range(len(geneData.columns)-1):
    geneData[i] = 'G' + str(i+1) + "_" + geneData[i].astype(str)

#############################################################
# Minimum support and confidence scores for rules generation
# are taken as command line arguments.
	
support = int(sys.argv[2])/100*len(geneData)
minconf = int(sys.argv[3])/100

#############################################################
# Frequent itemsets of length 1 only are generated from 
# imported data for all columns.
frequent_itemsets = set()
for i in range(len(geneData.columns)):
    dat=geneData[i].groupby(geneData[i]).describe()
    for j in range(len(dat)):
        item=list(dat.iloc[j])[2:4]
        if(item[1] >= support):
            frequent_itemsets.add(item[0])

			
#############################################################
# All transactions are converted into a list of transaction 
# sets.
Transactions = []
for i in range(len(geneData)) :
    Transactions.append(set(geneData.iloc[i]))

#############################################################
# apriori_gen(itemsets,r)
# This function generates all possible combinations for a 
# given set of items
# inputs: Itemsets is a given set of items, r is the 
# 		  required combination set.	
# returns: A list of sets.

def apriori_gen(itemsets,r):
    combinations=itertools.combinations(itemsets,r)
    return [set(i) for i in list(combinations)]


#############################################################
# calcHypotenuse(a, b)
# This block of code creates dictionary of all the frequent 
# itemsets and their support count.
# inputs: 
# returns: the length of the hypotenuse.
	
print("Support is set to be "+str(support)+"%")
C_tj={}
for r in range(len(geneData.columns)-1):
    C_k=apriori_gen(frequent_itemsets,r+1)
    C_t=[]
    for i in C_k:
        support_count=0
        for t in Transactions:
            if(i.issubset(t)):
                support_count+=1
        if(support_count>=support):
            C_t.append(i)
            if(i!=None):
                x=list(i)
                x.sort()
                C_tj[str(set(x))]=support_count  
    if(len(C_t)==0):
        break
    else:
        print("number of length-"+str(r+1)," frequent itemsets: "+str(len(C_t)))
    frequent_itemsets=set.union(*C_t)
print("Total frequent itemsets: "+str(len(C_tj)))

#############################################################
# Creates an empty dataframe to store generated rules

RULES=pd.DataFrame(columns=['RULE','BODY','HEAD','CONFIDENCE'])

#############################################################
# This block of code generates rules based on the dictionary 
# of frequent itemsets.
# inputs: max length of itemsets
#		  dictionary of frequent itemsets
# returns: dataframe of generated rules from frequent itemsets.

for itemsets in range(r):
    f_k=[eval(i) for i in C_tj if(len(eval(i))==itemsets+1)]
    for fk in f_k:    
        for i in range(len(fk)):
            if(len(fk)>(i+1)):
                Hm=apriori_gen(fk,i+1)
                for hm in Hm:
                    x=list(fk)
                    x.sort()
                    y=list(fk.difference(hm))
                    y.sort()
                    conf=C_tj[str(set(x))]/C_tj[str(set(y))]
                    if(conf>minconf):
                        RULES.loc[len(RULES)]=pd.Series({'RULE': str(fk),'BODY': str(fk.difference(hm)), 'HEAD': str(hm), 'CONFIDENCE': conf})						
						
#############################################################
# Exports RULES dataframe into csv
RULES.to_csv('RULES.csv', sep=',')
print(str(len(RULES)) + " rules generated.")
#############################################################
# queryParser(query)
# Level 1 query parser
# Inputs:	query string
# Outputs:	final dataframe with required data
# Description: Parses query and calls required sub module(s) 
# 			   as queried.
def queryParser(query):
    if(query[:19]=='asso_rule.template1'):
        queryResult=queryParserT1(eval(query[19:]))
    elif(query[:19]=='asso_rule.template2'):
        queryResult=queryParserT2(eval(query[19:]))
    elif(query[:19]=='asso_rule.template3'):
        queryResult=queryParserT3(eval(query[19:]))
    return queryResult.drop_duplicates()

#############################################################
# queryParserT1(query)
# Inputs:	query string
# Outputs:	final dataframe with required data
# Description: Query sub module for template 1 

def queryParserT1(query):
    
    queryResult = pd.DataFrame(data=None, columns=RULES.columns)
    
    if(query[0]=="RULE"):
        if(query[1]=="ANY"):            
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['RULE'].str.contains(item)])
        elif(query[1]=="NONE"):
            queryResult = RULES.copy()
            for item in query[2]:
                queryResult = queryResult[~queryResult['RULE'].str.contains(item)]
        elif(query[1]==1):
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['RULE'].str.contains(item)])   
            rem=apriori_gen(set(query[2]),2)
            for rem_item in rem:
                queryResult = queryResult[~queryResult['RULE'].str.contains(str(rem_item)[1:-1])]
    
    elif(query[0]=="BODY"):
        if(query[1]=="ANY"):            
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['BODY'].str.contains(item)])
        elif(query[1]=="NONE"):
            queryResult = RULES.copy()
            for item in query[2]:
                queryResult = queryResult[~queryResult['BODY'].str.contains(item)]
        elif(query[1]==1):
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['BODY'].str.contains(item)])   
            rem=apriori_gen(set(query[2]),2)
            for rem_item in rem:
                queryResult = queryResult[~queryResult['BODY'].str.contains(str(rem_item)[1:-1])]
                
    elif(query[0]=="HEAD"):
        if(query[1]=="ANY"):            
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['HEAD'].str.contains(item)])        
        elif(query[1]=="NONE"):
            for item in query[2]:
                queryResult = RULES.copy()
                queryResult = queryResult[~queryResult['HEAD'].str.contains(item)]
        elif(query[1]==1):
            for item in query[2]:
                queryResult = queryResult.append(RULES[RULES['HEAD'].str.contains(item)])   
            rem=apriori_gen(set(query[2]),2)
            for rem_item in rem:
                queryResult = queryResult[~queryResult['HEAD'].str.contains(str(rem_item)[1:-1])]

    return queryResult.drop_duplicates()

#############################################################
# queryParserT2(query)
# Inputs:	query string
# Outputs:	final dataframe with required data
# Description: Query sub module for template 2 

def queryParserT2(query):
    queryResult = pd.DataFrame(data=None, columns=RULES.columns)
    if(query[0]=="RULE"):
        for i in range(len(RULES)):
            if((len(eval(RULES['BODY'].iloc[i]))+len(eval(RULES['HEAD'].iloc[i])))>=query[1]):
                queryResult=queryResult.append(RULES.iloc[i])
    elif(query[0]=="BODY"):
        for i in range(len(RULES)):
            if((len(eval(RULES['BODY'].iloc[i])))>=query[1]):
                queryResult=queryResult.append(RULES.iloc[i])
    elif(query[0]=="HEAD"):
        for i in range(len(RULES)):
            if((len(eval(RULES['HEAD'].iloc[i])))>=query[1]):
                queryResult=queryResult.append(RULES.iloc[i])
    return queryResult.drop_duplicates()

#############################################################
# queryParserT3(query)
# Inputs:	query string
# Outputs:	final dataframe with required data
# Description: Query sub module for template 3

def queryParserT3(query):
    queryResult = pd.DataFrame(data=None, columns=RULES.columns)
    if(query[0]=="1or1"):
        queryResult = queryParserT1(query[1:4]).append(queryParserT1(query[4:7]))
    elif(query[0]=="1and1"):
        queryResult = pd.merge(queryParserT1(query[1:4]), queryParserT1(query[4:7]), how='inner', on=['RULE','BODY','HEAD','CONFIDENCE'])
    elif(query[0]=="1or2"):
        queryResult = queryParserT1(query[1:4]).append(queryParserT2(query[4:6]))
    elif(query[0]=="1and2"):
        queryResult = pd.merge(queryParserT1(query[1:4]), queryParserT2(query[4:6]), how='inner', on=['RULE','BODY','HEAD','CONFIDENCE'])
    elif(query[0]=="2or2"):
        queryResult = queryParserT2(query[1:3]).append(queryParserT2(query[3:5]))
    elif(query[0]=="2and2"):
        queryResult = pd.merge(queryParserT2(query[1:3]), queryParserT2(query[3:5]), how='inner', on=['RULE','BODY','HEAD','CONFIDENCE'])
    return queryResult.drop_duplicates()


#############################################################
# Query execution module
# This block of code processes queries.
while(True):
    query = input("> ")
    try:
        if(query.lower() == "exit"):
            break
        else:
            r = queryParser(query)
            print(r[['BODY','HEAD']])
            print(str(len(r)) + " rows selected." + "\n")
    except:
        print("Invalid query.\n")
