import sys
from models.mongo_models import *
from nlplib.clean_text import CleanText
import utils
from gensim.utils import lemmatize
from itertools import chain, combinations
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

cleanText = CleanText()

#search for top k related articles
class Search:
	class ScoreDocs:
		docID = ObjectIdField()
		score = FloatField()
		searchPhrase = []
		

	def subQueries(self, searchPhrase):
		words = [word[:-3] for word in lemmatize(cleanText.removeStopWords(cleanText.cleanText(searchPhrase)))]
		searchWords = []
		for L in range(len(words) + 1, 0, -1):
			for subset in combinations(words, L):
				searchWords.append(list(subset))
		return searchWords

	def score(self, words):
		listDocs = []
		for word in words:
			documents = Vocabulary.objects(word = word).only("docIDs")
			l = []				
			for document in documents:
				for d in document.docIDs:
					l.append(d.docID)
			listDocs.append(l)
		
		#print listDocs

		intList = listDocs[0]

		for idx in range(1, len(listDocs)):
			intList = list(set(intList) & set(listDocs[idx]))

		listScore = []
		for docID in intList:
			scoreDoc = self.ScoreDocs()
			scoreDoc.docID = docID
			scoreDoc.score = 0
			scoreDoc.searchPhrase = words
			for word in words:			
				documents = Vocabulary._get_collection().find_one({"word": word, "docIDs.docID": docID}, {"_id": 0,"idf": 1,"docIDs.$": 1})
				if documents:
					scoreDoc.score += documents["docIDs"][0]["tf"] * documents["idf"]
			listScore.append(scoreDoc)

		listScore = sorted(listScore, key=lambda scoreDoc: scoreDoc.score, reverse=True)

		return listScore

	def __init__(self, searchPhrase, k):
		subSearch = self.subQueries(searchPhrase)
		listSearch = []

		#a paralel approach
		
		no_threads = cpu_count()

		with ThreadPoolExecutor(max_workers = no_threads) as e:
			for search in subSearch:
				result = e.submit(self.score, search)
				listSearch += result.result()

		"""
		#this is a seqvential approach
		for search in subSearch:
			#print search
			listSearch += self.score(search)
		"""

		#sort the list  by score
		listSearch = sorted(listSearch, key=lambda scoreDoc: scoreDoc.score, reverse=True)
		
		minList = []

		for elem in listSearch:
			if not minList:
				minList.append(elem)
			elif minList and len(minList)<k: #verify K
				ok = True
				for elem2 in minList:				
					if elem.docID == elem2.docID:
						ok = False
						break
				if ok:
					minList.append(elem)
			else:
				break

		#for elem in minList:
		#	print elem.score, elem.docID, elem.searchPhrase


if __name__ == "__main__":
	connect("ERICDB")
	searchPhrase = sys.argv[1]
	start = time.time() 
	search = Search(searchPhrase, 20)
	end = time.time() 
	print (end -start)

#example
#python search.py "ashton kutcher two charlie sheen"
