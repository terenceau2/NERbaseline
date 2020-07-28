#creating the training set

with open("eng.train") as myfile:
    traindata = myfile.readlines()

traindata=[i.split() for i in traindata]
traindata= [i for i in traindata if i != []] #delete the empty lists
for i in traindata:
    del i[1]
    del i[1]   #delete the middle 2 columns from the data




#=================================================================================================================================================================================
#creating the test set (both annotated and unannotated)

with open("eng.testa") as myfile:
    testdata=myfile.readlines()

testdata=[i.split() for i in testdata]
testdata= [i for i in testdata if i != []] #delete the empty lists
for i in testdata:
    del i[1]
    del i[1]   #delete the middle 2 columns from the data

testdataours= []
testdataours= [i[0] for i in testdata]



#=================================================================================================================================================================================
#identifying the NE. construct a list with all the NE
NE=""
for i in range(1,len(traindata)):
    if traindata[i][1] != 'O':
        NE = NE + traindata[i][0]+' '

        if traindata[i+1][1] == 'O' or traindata[i+1][1]!= traindata[i][1]:
            NE=NE+','+traindata[i][1]
            NE=NE+'±'   #i tried using . as the splitter. but words Like U.S. can cause problems


#convert the string into a list
NE=NE.split('±')
#eliminating the space before the comma
NE=[i.replace(" ,",",") for i in NE]
NE=list(dict.fromkeys(NE)) #remove duplicates from the list

NE=[i.split(',') for i in NE]



#=================================================================================================================================================================================

#setting up the baseline : only umambiguously tag those that have appeared in the training set
#if a word/phrase is part of more than 1 type of entity, then we choose the one with longest length (of word)

NEbaseline= ""
for i in range(1,len(traindata)):
    if traindata[i][1] != 'O':
        NEbaseline=NEbaseline+traindata[i][0]+','+traindata[i][1]+'±'
#nebaseline is the list of only the named entities

NEbaseline=NEbaseline.split('±')
NEbaseline=list(dict.fromkeys(NEbaseline)) #remove duplicates from the list

NEbaseline = [i.split(',') for i in NEbaseline]


#identify those which 1 word (key) may match to different NER tags (ambiguous ones)
#tiebreaking method: the longest phrase in the trainset is the dominating one. follow that tag
newdict={}
for i in range(0,len(NEbaseline)-1):
    if NEbaseline[i][0] in newdict:
        if newdict[NEbaseline[i][0]] != NEbaseline[i][1]: #if an ambiguity situation comes up... (ie. same word, different tag)

            candidates=[a for a,x in enumerate(traindata) if x[0]==NEbaseline[i][0]] #locate all such words in the training set
            length=[] #an empty string that records the lengths of the phrases

            for c in candidates: #we look at each phrase in the train set
                l=0  #l counts the length of this phrase
                k=c #k marks the position we are at
                while traindata[k][1]!='O':  #look at the words in front of the ambigious words
                    l+=1
                    k-=1
                k=c
                while traindata[k][1]!='O': #look at the words after of the ambigious words
                    l+=1
                    k+=1

                l=l-1 #because at position c we double counted, we deduct 1.
                length.append(l)

            longest=length.index(max(length)) #if multiple phrases have the same length and is the longest ones, then just choose the first one to appear
            # (the conll paper didnt specify other tiebreaking methods)
            position=candidates[longest]
            word=traindata[position]
            newdict[NEbaseline[i][0]] = word[1]

    else:
        newdict[NEbaseline[i][0]] = NEbaseline[i][1]



#tag the test set according to the baseline method
for i in range(0, len(testdataours)):
    if testdataours[i] in newdict:
        testdataours[i]= testdataours[i] + ',' + newdict[testdataours[i]]
    else:
        testdataours[i]= testdataours[i] + ',O'


testdataours=[i.split(',') for i in testdataours]

#check precision
total=len(testdata)
tp=0 #tp stands for true positive. the word is a NE, and correctly tagged

retrieved=0 #count for the ones that is tagged as NE by the baseline
relevant=0 #count for the ones that is actualy a NE (by the ground truth)
correct=0


for i in range(0,total-1):
    if testdata[i][1]!='O' and testdataours[i]== testdata[i]:
        tp= tp+1
    if testdataours[i][1]!= 'O':
        retrieved=retrieved+1

    if testdata[i][1]!='O':
        relevant=relevant+1
    if testdata[i][1]!='O' and testdataours[i][1]!= 'O':
        correct+=1



precision=tp/retrieved
recall=tp/relevant
fscore=2*precision*recall/(precision+recall)

#for this set, the precision is about 44%. recall is 48%. fscore is 46%
#don't know why this is different with the one on conference website

#=================================================================================================================================================================================

