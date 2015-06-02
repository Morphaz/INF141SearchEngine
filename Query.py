'''
Created on May 17, 2015
Kyle Vonderwerth, Jenny Tang, Stephen Em
INF 141: Search Engine Milestone 1
Python 3.4
'''
from collections import namedtuple, defaultdict
from sys import exit
import time, json
from math import sqrt

class Search(object):
     '''
     Search.returnSearchResults() -> {rankingNumber:{url:'www.place', snippet:'context from the doc', title:'title of page'}}
     version = "0.1"
     '''
     Initialize the index
     '''
     _Result = namedtuple('Result','score url textSource')
     def __init__(self, query):
          START_TIME = time.time()
          self.query = query.lower().split()
          '''
          Initialize the index
          '''
          with open('index.txt') as indexFile:
               self._index = json.loads(indexFile.read())
          
     def getTermIDsFromQuery(self):
          matchedTermIDs = {} # term -> [termID,IDF]
          matchedIndicies = {}
          with open('termID_mapping.txt') as termToTermIDFile:
               for line in termToTermIDFile:
                    for term in self.query:
                         if term + ' ' in line[:len(term + ' ')]:
                              matched = line.replace(' ','').replace('\n','').split(':')
                              matchedTermIDs[matched[1]] = [matched[0],float(matched[2])*(1/len(self.query))]
          for term in matchedTermIDs.keys():
               for i in range(len(self._index)):
                    if str(self._index[i][0]) == term:
                         matchedIndicies[str(self._index[i][0])] = self._index[i][1]
          print("--- %s seconds --- Got terms" % (time.time() - START_TIME))
          return (matchedIndicies,matchedTermIDs)
     
     def cosineSimilarityOfPostings(self,matches):
          '''
          Assume simple queries where query terms are either 1(in corpus) or 0(not in corpus)
          '''
          matchedDocIDs = matches[0]
          matchedTermIDs = matches[1]
          scores = defaultdict(float)
          docLengths = {}
          queryLength = 0
               
          '''
          get query length
          '''
          termSqr = []
          for term in matchedTermIDs.keys():
               termSqr.append(matchedTermIDs[term][1]**2)
          queryLength = sqrt(sum(termSqr))
               
          '''
          Accumulate scores
          '''
          for term, postings in matchedDocIDs.items():
               for doc, TFIDF in postings.items():
                    matchedTermIDs[term][1]
                    scores[doc] += matchedTermIDs[term][1]*TFIDF
          '''
          get lengths
          '''
          with open('docID_mapping.txt') as termToTermIDFile:
               for line in termToTermIDFile:
                    line = line.replace(' ','').replace('\n','').split(':')
                    docLengths[line[0]] = line[1]
          
          '''
          length normalize scores
          '''
          for doc in scores.keys():
               scores[doc] = scores[doc]/(float(docLengths[doc])*queryLength)
          
          return sorted([(k,v) for k,v in scores.items()],key = lambda x: x[1], reverse = True)[:10]
          
     def getContextFromResults(self, results):
          '''
          get doc context for top 10 results
          '''
          print(results)
          def parseText(doc):
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
               
                    return list(filter(lambda x: x != '',text.split(' ')))
               with open('FileDump'+'/'+doc+'.txt') as jsonDoc:
                    parsedJson = json.loads(jsonDoc.read())
               return (tokenizeFile(parsedJson['text']), parsedJson['_id'], parsedJson['title'])
               
          resultsWithContext = dict()
          i = 0
          for doc in results:
               i+=1
               docContext = parseText(doc[0])
               resultsWithContext[i] = dict()
               resultsWithContext[i]['title'] = docContext[2]
               resultsWithContext[i]['url'] = docContext[1] 
               '''
               Accumulate text context
               '''
               snippet = ''
               j = 0
               hitQ = False
               hitA = False
               for query in self.query:
                    for cterm in docContext[0]:
                         if query == cterm:
                              if hitA == False:
                                   hitQ = True
                              hitA = True
                         if hitQ:
                              if j == 0:
                                   snippet += cterm
                              else:
                                   snippet += ' ' + cterm
                              j+=1
                              if j == 10:
                                   hitQ = False
                                   snippet += '...'
               gotP = False                   
               for query in self.query:
                    try:
                         if gotP == False:
                              position = docContext[0].index(query)
                              gotP = True
                    except:
                         continue
               if position < 9:
                    resultsWithContext[i]['snippet'] = '"'+' '.join(docContext[0][:position-1]) + ' ' + snippet + '"'
               else:
                    resultsWithContext[i]['snippet'] = '"...'+' '.join(docContext[0][position-10:position-1]) + ' ' + snippet + '"'
          return resultsWithContext
     
     def returnSearchResults(self):
          '''
          execute search
          '''
          return self.getContextFromResults(self.cosineSimilarityOfPostings(self.getTermIDsFromQuery()))
     
if __name__ == "__main__":
     START_TIME = time.time()
     print(Search("machine learning").returnSearchResults())
     
     print("--- %s seconds ---" % (time.time() - START_TIME))
