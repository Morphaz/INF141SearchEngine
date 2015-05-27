'''
Created on May 12, 2015
Kyle Vonderwerth, Jenny Tang, Stephen Em
INF 141: Search Engine Milestone 1
Python 3.4
'''
import time
from math import log10, log
from collections import defaultdict
import json, os

class Indexer(object):
     version = '0.1'
     
     def __init__(self,directory):
          if os.listdir(directory): #check is dir is empty
               self.directory = directory #directory holding json objects
               self.index = defaultdict(lambda:defaultdict(int)) #{termID : {docID : frequencyOfTermInDoc}}
               self.docID = 0 #increment for every json object parsed
               self.docToID = {} # {URL : docID}
               self.termToID = {} # {term : termID}
               self.termIDtoTerm = {}
               self.totalCorpus = 0
     
     def generateIndex(self):
          '''
          for each json object in a directory, parse json objects to create term listings, accumulating in index, then write index to disk 
          '''
          for doc in os.listdir(self.directory):
               self.docID+=1
               self.indexBlock(self.parseText(doc))
               print(self.docID)
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
               parsedJson = json.loads(jsonDoc.read())
     
          return (tokenizeFile(parsedJson['text']), parsedJson['_id'])
     
     def indexBlock(self, parsedJson):
          '''
          for data parsed from json object, update terms -> id mapping, update URL -> docID mapping, and update index with block data 
          '''
          self.docToID[parsedJson[1]] = self.docID
          terms = set()
          for term in parsedJson[0]:
               if term not in self.termToID.keys():
                    self.termIDtoTerm[len(self.termToID) + 1] = term
                    self.termToID[term] = [len(self.termToID) + 1,0]
               self.index[self.termToID[term][0]][self.docID] += 1
               self.totalCorpus += 1
               terms.add(term)
          
          '''
          get log(tf) for terms in doc
          '''
          for term in terms:
               self.termToID[term][1] += 1
               self.index[self.termToID[term][0]][self.docID] = 1+log(self.index[self.termToID[term][0]][self.docID])
                    
     def generateTFIDF(self):
          for k,v in self.index.items():
               for doc,termFreq in v.items():
                    try:
                         self.index[k][doc] = termFreq * log10(self.totalCorpus/self.termToID[self.termIDtoTerm[k]][1])
                    except:
                         pass
     def writeIndex(self):
          '''
          write index, and ID mappings to disk
          '''
          with open('index.txt','a') as index: # write index
               for term, docIDListings in sorted([(k,v) for k,v in self.index.items()],key = lambda x: x[0]):
                    index.write(str(term) + ' : ' + str(dict(docIDListings))+'\n')
               '''
               json.dump(sorted([(str(k),str(dict(v))) for k,v in self.index.items()],key = lambda x: x[0]), index)
               '''
          with open('termID_mapping.txt','a') as index: # write term -> termID mapping  
               for term, termID in sorted([(k,v) for k,v in self.termToID.items()],key = lambda x: x[0]): # sorted alphabetically by term
                    index.write(str(term) + ' : ' + str(termID[0]) +'\n')
               '''
               json.dump(sorted([(str(k),str(v)) for k,v in self.termToID.items()],key = lambda x: x[0])[:1], index)
               '''
          with open('docID_mapping.txt','a') as index: # write URL -> docID mapping  
               for url, docID in sorted([(k,v) for k,v in self.docToID.items()],key = lambda x: x[1]): # sorted numerically by docID
                    index.write(str(url) + ' : ' + str(docID) + '\n')
               '''
               json.dump(sorted([(str(k),str(v)) for k,v in self.docToID.items()],key = lambda x: x[1]), index)
               '''
          print("Number of Documents: " + str(len(self.docToID.items())))
          print("Number of Unique Word: " + str(len(self.termToID.items())))
                    
if __name__ == "__main__":
     START_TIME = time.time()
     Indexer('FileDump').generateIndex()
     print("--- %s seconds ---" % (time.time() - START_TIME))
