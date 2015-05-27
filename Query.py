'''
Created on May 17, 2015
Kyle Vonderwerth, Jenny Tang, Stephen Em
INF 141: Search Engine Milestone 1
Python 3.4
'''
from collections import namedtuple, defaultdict
from sys import exit
import time, json

class SearchInterface(object):
     version = "0.1"
     '''
     Initialize the index
     '''
     with open('termID_mapping.txt') as termToTermIDFile:
          _termToTermID = termToTermIDFile.read().replace(' ','').replace('\n',':').split(':')
     with open('docID_mapping.txt') as docIDToDocFile:     
          _docIDToDoc = docIDToDocFile.read().replace(' ','').replace('\n',':').split(':')
     with open('index.txt') as indexFile:
          _index = indexFile.read().replace(' ','').replace('\n',':').split(':')
     '''
     initialize the data structure the represents 
     '''
     _Result = namedtuple('Result','score url textSource')
     def __init__(self, query):
          self.query = query.split()
     
     def getTermIDs(self):
          matchedTermIDs = []
          for term in self.query:
               try:
                    matchedTermIDs.append((term,self._termToTermID[self._termToTermID.index(term)+1]))
               except:
                    continue
          if not matchedTermIDs:
               print('No documents match search query.')
               exit()
          return(matchedTermIDs)
     
     def getDocs(self,matchedTermIDs):
          matchedDocIDs = []
          for term in matchedTermIDs:
               traverse = self._index.index(term[1])
               doc=''
               while term:
                    traverse += 1
                    if '}' not in self._index[traverse]:
                         doc = doc + ';'
                         doc = doc + self._index[traverse]
                         continue
                    doc = doc + ';'
                    doc = doc + self._index[traverse]
                    break
               matchedDocIDs.append( (term[0],dict([(docID.split(';')) for docID in doc[2:-1].split(',')])) )
          return matchedDocIDs
     
     def cosineNormalization(self,matchedTerms):
          '''
          Assume simple queries where query terms are either 1(in corpus) or 0(not in corpus)
          '''
          scores = defaultdict(float)
          results = defaultdict(list)
          docSnips = defaultdict(str)
          
          for term in matchedTerms:
               for docID, TFIDF in term[1].items():
                    scores[docID] += float(TFIDF)
          print('totaled scores')
          
          for docID, score in scores.items():
               docText = self.parseText(int(docID))
               #append URL to results
               results[docID].append(docText[1])
               #append length normalized score to results
               try:
                    results[docID].append(scores[docID]/len(docText[0]))
               except:
                    results[docID].append(0)
          
          for doc in scores.keys():
               '''
               Increase scores for 
               '''
               if doc in self.intersection(matchedTerms):
                    scores[doc] += 1 
                    
          return sorted([(k,v) for k,v in results.items()], key = lambda x: x[1][1], reverse = True)
     
     def intersection(self, matchedTerms):
          '''
          return docIDs that have every query term present
          '''
          intersect = set()
          for term in matchedTerms:
               for doc in term[1].keys:
                    intersect.add(doc)
          return intersect
          
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
                    This function utilizes lambda to check if a char in a token is alphanumeric, filtering the token and returning a token that is 
                    only alphanumeric and normalized to lowercase.
                    '''
                    return ''.join(filter(lambda x: x in ALPHANUMERICS, token)).lower() 
               with open("stopWords.txt") as sWF:
                    stopWords = sWF.read().split("\n")
               return list(filter(lambda x: x not in stopWords,map(alphaNumericMapping,filter(lambda x: 2<=len(x)<50,text.split(' ')))))
          
          with open('FileDump' + '/' + str(doc) + '.txt') as jsonDoc:
               parsedJson = json.loads(jsonDoc.read())
               return (tokenizeFile(parsedJson['text']), parsedJson['_id'])
          
     def returnSearchResults(self):
          return self.cosineNormalization(self.getDocs(self.getTermIDs()))
     
if __name__ == "__main__":
     START_TIME = time.time()
     search = SearchInterface("machine learning")
     print(search.returnSearchResults())
     print("--- %s seconds ---" % (time.time() - START_TIME))
