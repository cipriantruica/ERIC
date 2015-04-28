import sys
from models.mongo_models import *
from nlplib.clean_text import CleanText
import utils
from gensim.utils import lemmatize
from itertools import combinations
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from collections import OrderedDict

cleanText = CleanText()
#rethink this search engine
#do only 5 queries and then combine them based on combination
#search for top k related articles
class Search:
	class ScoreDocs:
		docID = ObjectIdField()
		score = FloatField()

	def subQueries(self, searchPhrase):
		words = [word.split('/')[0] for word in lemmatize(cleanText.removeStopWords(cleanText.cleanText(searchPhrase)))]
		searchWords = []
		for L in range(len(words) + 1, 0, -1):
			for subset in combinations(words, L):
				searchWords.append(list(subset))
		return words, searchWords

	def score(self, word):
		listScore = {}
		documents = Vocabulary.objects(word = word).only("idf", "docIDs").timeout(False)
		for document in documents:
			scoreDoc = self.ScoreDocs()
			idf = document.idf
			for elem in document.docIDs:
				listScore[elem.docID] = idf * elem.tf
		return listScore

	def rank(self, searchPhrase):
		keys = []
		scorePhrase = {}
		for word in searchPhrase:
			if not keys:				
				keys = self.listSearch[word].keys()
			else:
				keys = list(set(keys) & set(self.listSearch[word].keys()))
		for key in keys:
			score = 0
			for word in searchPhrase:
				score += self.listSearch[word][key]
			scorePhrase[key] = round(score, 2)
		#print searchPhrase, scorePhrase
		return scorePhrase, keys


	def __init__(self, searchPhrase, k):
		self.listSearch = {}
		self.words, subSearch = self.subQueries(searchPhrase)
		
		no_threads = cpu_count()

		with ThreadPoolExecutor(max_workers = no_threads) as e:
			for word in self.words:
				result = e.submit(self.score, word)
				self.listSearch[word] = result.result()

		keys = {}
		rankedPhrase = {}
		with ThreadPoolExecutor(max_workers = no_threads) as e:
			for phrase in subSearch:
				result = e.submit(self.rank, phrase)
				rankedPhrase[' '.join(word for word in phrase)], keys[' '.join(word for word in phrase)]= result.result()
		
		distinctKeys = []
		for key in keys:			
			distinctKeys += keys[key]
		distinctKeys =list(set(distinctKeys))


		answer = {}
		for key in distinctKeys:
			for phrase in subSearch:
				if rankedPhrase[' '.join(word for word in phrase)].get(key, -1) != -1:
					answer[key] = max(rankedPhrase[' '.join(word for word in phrase)][key], answer.get(key, -1))

		#print answer.values()
		answer = sorted(answer.items(), key=lambda x: x[1], reverse=True)

		idx = 0
		for key in answer:
			print key
			idx += 1
			if idx == k:
				break

if __name__ == "__main__":
	connect("ERICDB")
	#searchPhrase = sys.argv[1]
	searchPhrase = "absurd ability action back go"
	start = time.time() 
	search = Search(searchPhrase, 20)
	end = time.time() 
	print (end -start)
