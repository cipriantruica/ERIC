# coding: utf-8
from __future__ import division
from gensim.utils import lemmatize
from nlplib.clean_text import CleanText
from nltk.corpus import wordnet


#TO_DO modify this class to accept french also
class LemmatizeText:
	class Word():
		word = ""
		wtype = ""
		count = 0
		tf = 0.0

	def __init__(self, rawText, language='EN'):
		self.wordList = []
		self.rawText = rawText
		self.cleanText = ""	
		self.words = []
		self.language = language

	def createLemmaText(self):
		ct = CleanText()
		if self.language == 'EN':
			self.words = lemmatize(ct.removeStopWords(self.rawText))
			self.cleanText = ' '.join(word[:-3] for word in self.words)
		if self.language == 'FR':
			#To DO
			self.words = []
			self.cleanText = ct.removeStopWords(self.rawText, self.language)


	def createLemmas(self):
		if self.cleanText:
			for word in self.words:
				self.append(word[:-3], word[-2:])
				#sort wordList by word count
				self.wordList = sorted(self.wordList, key=lambda word: word.count)
				#calculate TF
				maxF = self.wordList[-1].count
				for idx in xrange(0,len(self.wordList), 1):
					self.wordList[idx].tf = 0.5 + (0.5 * self.wordList[idx].count)/maxF

	def append(self, word, wtype):
		if word:
			if not self.wordList:
				newWord = self.Word()
				newWord.count = 1
				newWord.word = word
				newWord.wtype = wtype
				self.wordList.append(newWord)
			else:
				notInList = True
				for idx in xrange(0,len(self.wordList), 1):
					if word == self.wordList[idx].word and wtype == self.wordList[idx].wtype:
						self.wordList[idx].count += 1
						notInList = False
						break
				if notInList:
					newWord = self.Word()
					newWord.count = 1
					newWord.word = word
					newWord.wtype = wtype
					self.wordList.append(newWord)
	#testing
	def printList(self):
		for words in self.wordList:
			print words.word, "pos", words.wtype, "count:", words.count, "TF:", words.tf
