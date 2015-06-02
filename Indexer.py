'''
Created on May 12, 2015
Kyle Vonderwerth, Jenny Tang, Stephen Em
INF 141: Search Engine Milestone 1
Python 3.4
'''
import time
from math import log2, log, sqrt
from collections import defaultdict
import json, os

class Indexer(object):
     version = '0.1'
     
     def __init__(self,directory):
          if os.listdir(directory): #check is dir is empty
               self.directory = directory #directory holding json objects
               self.index = defaultdict(lambda:defaultdict(int)) #{termID : {docID : frequencyOfTermInDoc}}
               self.docID = 0 #increment for every json object parsed
               self.termToID = {} # {term : termID}
               self.docIDToLength = defaultdict(list)
               self.termIDtoTerm = {}
               self.totalCorpus = 0
     
     def generateIndex(self):
          '''
          for each json object in a directory, parse json objects to create term listings, accumulating in index, then write index to disk 
          '''
          #counter = 0
          for doc in os.listdir(self.directory):
               #counter+=1
               self.indexBlock(self.parseText(doc))
               #if counter == 50:
                    #break
          self.generateTFIDF()
          self.writeIndex()
          print('Index has been generate')
          
     def parseText(self, doc):
          '''
          parse text from json object and tokneize to create terms
          '''
          def tokenizeFile(text) -> [str]:
               '''
               This function takes a string argument and uses a map/filter transform on it, returning a alphanumeric, all lower case tokenized list. 
               '''
               ALPHANUMERICS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'#0123456789';
               def alphaNumericMapping(token: str) -> str:
                    '''
                    This function utilizes lambda to check if a char in a token is alphanumeric, filtering the token and returning a list of tokens
                     that is only alphanumeric and normalized to lowercase.
                    '''
                    return ''.join(filter(lambda x: x in ALPHANUMERICS, token)).lower() 
               with open("stopWords.txt") as sWF:
                    stopWords = sWF.read().split("\n")
               return list(filter(lambda x: x != '',filter(lambda x: x not in stopWords,map(alphaNumericMapping,filter(lambda x: 2<=len(x)<50,text.split(' '))))))
          
          with open('FileDump'+'/'+doc) as jsonDoc:
               self.docID = doc.replace('.txt','')
               print(self.docID)
               parsedJson = json.loads(jsonDoc.read())
     
          return (tokenizeFile(parsedJson['text']), parsedJson['_id'])
     
     def indexBlock(self, parsedJson):
          '''
          for data parsed from json object, update terms -> id mapping, update URL -> docID mapping, and update index with block data 
          '''
          self.totalCorpus += 1
          terms = set()
          for term in parsedJson[0]:
               if term not in self.termToID.keys():
                    self.termIDtoTerm[len(self.termToID) + 1] = term # termID -> term
                    self.termToID[term] = [len(self.termToID) + 1,0] # term -> [termID, termFreq]
               self.index[self.termToID[term][0]][self.docID] += 1
               terms.add(term)
               self.docIDToLength[self.docID].append(self.termToID[term][0])
          '''
          get term frequency
          '''
          for term in terms:
               self.termToID[term][1] += 1
               self.index[self.termToID[term][0]][self.docID] = self.index[self.termToID[term][0]][self.docID]/len(parsedJson[0])
               
     def generateTFIDF(self):
          for k,v in self.index.items():
               for doc,termFreq in v.items():
                    try:
                         idf = log2(self.totalCorpus/self.termToID[self.termIDtoTerm[k]][1])
                         self.index[k][doc] = termFreq * idf
                         self.termToID[self.termIDtoTerm[k]][1] = idf
                         
                    except:
                         pass
          '''
          get lengths for cosine normalization
          '''          
          for doc, terms in self.docIDToLength.items():
               for term in range(len(terms)):
                    self.docIDToLength[doc][term] = self.index[self.docIDToLength[doc][term]][doc]**2
          
          for doc in self.docIDToLength.keys():
               self.docIDToLength[doc] = sqrt(sum(self.docIDToLength[doc])) 
               
     def writeIndex(self):
          '''
          write index, and ID mappings to disk
          '''
          with open('index.txt','a') as index: # write index
               index.write(json.dumps(sorted([(k,v) for k,v in self.index.items()],key = lambda x: x[0])))
              
          with open('termID_mapping.txt','a') as index: # write term -> termID mapping  
               for term, termID in sorted([(k,v) for k,v in self.termToID.items()],key = lambda x: x[0]): # sorted alphabetically by term
                    index.write(str(term) + ' : ' + str(termID[0]) + ' : '+ str(termID[1]) + '\n')
          
          with open('docID_mapping.txt','a') as index: # write term -> termID mapping  
               for doc, length in sorted([(k,v) for k,v in self.docIDToLength.items()],key = lambda x: x[0]): # sorted alphabetically by term
                    index.write(str(doc) + ' : ' + str(length)  + '\n')
                    
if __name__ == "__main__":
     START_TIME = time.time()
     Indexer('FileDump').generateIndex()
     print("--- %s seconds ---" % (time.time() - START_TIME))
