# coding: utf-8
from __future__ import division
from gensim.utils import lemmatize
from nlplib.clean_text import CleanText
from nltk.corpus import wordnet
from nltk.tag.stanford import POSTagger




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
			st = POSTagger('./nlplib/stanford_pos/french.tagger', './nlplib/stanford_pos/stanford-postagger.jar', encoding='utf-8') 
			text = self.rawText.encode("utf8")
			text = text.lower()
			text= ct.removePunctuation(ct.removeStopWords(text, self.language))
			self.words = st.tag(text.split(" "))
			self.cleanText = ' '.join(word[0].encode("utf8") for word in self.words)


	def createLemmas(self):
		if self.cleanText:
			if self.language == 'EN':
				for word in self.words:
					self.append(word[:-3], word[-2:])
			elif self.language == 'FR':
				for word in self.words:
					self.append(word[0].encode("utf8"), word[1].encode("ascii"))
			#sort wordList by word count
			self.wordList = sorted(self.wordList, key=lambda word: word.count)
			#calculate TF
			maxF = self.wordList[-1].count
			for idx in xrange(0,len(self.wordList), 1):
				self.wordList[idx].tf = round(0.5 + (0.5 * self.wordList[idx].count)/maxF, 2)

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
