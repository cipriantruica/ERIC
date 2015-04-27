# coding: utf-8
import sys  
import utils
from datetime import datetime
from models.postgres_models import *
from nlplib.lemmatize_text import LemmatizeText
from nlplib.named_entities import NamedEntitiesRegonizer
from nlplib.clean_text import CleanText
import pony.orm as pny

reload(sys)  
sys.setdefaultencoding('utf8')

# params:
# list with the fallowing elemets:
# *elem[0] = title of the document
# *elem[1] = raw text of the document
# *elem[2] = the date inside the document
# *elem[3] = list of tags
# *elem[4] = list of authors
# language, default English
# TO_DO sould see if other fields are needed
@db_session
def populateDatabase(elem, language='EN'):
	cleanText = CleanText()
	title = cleanText.replaceUTF8Char(elem[0])
	#verify if document exists
	#print title
	document = Documents.get(title= title.decode("utf8"))
	authors = []
	tags = []
	#document does not exist in the database, add new document
	if not document:		
		title = title.decode("utf8")
		rawText = cleanText.replaceUTF8Char(elem[1])		
		intText = cleanText.cleanText(elem[1], language)
		
		if language == 'EN':
			if elem[2][3] == ',':
				date = datetime.strptime(elem[2][:-6], "%a, %d %b %Y %H:%M:%S")
			else:
				date = datetime.strptime(elem[2], "%Y/%m/%d")
		else:			
			date = datetime.strptime(elem[2], "%d/%m/%Y")
		
		language = language
		#authors 
		#verify list's length - maybe it does not have the author field
		if len(elem) > 4:
			for name in utils.getAuthorName(elem[4]):
				author = Authors.get(firstname=name[0].decode("utf8"), lastname=name[1].decode("utf8"))
				if not author:
					author = Authors(firstname=name[0].decode("utf8"), lastname=name[1].decode("utf8"))
				authors.append(author)
	
	for c in cleanText.splitString(elem[3]):
		tag = Tags.get(tag=c)
		if not tag:
			tag = Tags(tag=c)
		tags.append(tag)
	
	if not document:		
		try:
			if authors:
				document = Documents(title=title, rawText=rawText.decode("utf8"), intText=intText.decode("utf8"), date=date, language=language, authorID=authors, tagID=tags)
			else:
				document = Documents(title=title, rawText=rawText.decode("utf8"), intText=intText.decode("utf8"), date=date, language=language, tagID=tags)
		except Exception as e:
			print "Insert Error!!!", e
	else:
		document.tags = tags
	
	

#this functions adds to the documents collection the cleanText and words labels
@db_session
def createCleanTextField(startDate, endDate, language):
	#print startDate, endDate
	documents = pny.select(d for d in Documents if d.createdAt >= startDate and d.createdAt < endDate).for_update()
	for document in documents:
		if document.intText and document.intText != " ":
			lemmas = LemmatizeText(document.intText, language)
			lemmas.createLemmaText()
			if lemmas.cleanText and lemmas.cleanText != " ":
				document.cleanText = lemmas.cleanText.decode("utf8")
				commit()
				lemmas.createLemmas()				
				for word in lemmas.wordList:								
					w = Words.get_for_update(word=word.word.decode("utf8"))
					if not w:
						w = Words(word=word.word.decode("utf8"))
						commit()
					for wtype in word.wtype:
						p = POS.get_for_update(pos=wtype)
						if not p:
							p = POS(pos=wtype)	
							commit()
						pw = Pos_Words.get_for_update(posID = p, wordID = w)
						if not pw:
							pw = Pos_Words(posID = p, wordID = w)
							commit()
						pi = POSIndex.get_for_update(posID = p, wordID = w, documentID=document)
						if not pi:
							pi = POSIndex(posID = p, wordID = w, documentID=document)
							commit()
					v = Vocabulary.get_for_update(documentID=document, wordID=w, count=round(word.count,2), tf=round(word.tf,2))
					if not v:
						v = Vocabulary(documentID=document, wordID=w, count=round(word.count,2), tf=round(word.tf,2))
						commit()
					
					


"""
#this function will create the named_entities collection
def createNamedEntitiesCollection(startDate, endDate):
	documents = Documents.objects(Q(createdAt__gte = startDate) & Q(createdAt__lt = endDate)).only("id", "intText").timeout(False)	
	for document in documents:
		namedEntitiesProcess = NamedEntitiesRegonizer(document.intText)
		namedEntitiesProcess.createNamedEntities()
		namedEntity = NamedEntities()
		namedEntity.docID = document.id
		namedEntity.gpe = namedEntitiesProcess.gpe
		namedEntity.person = namedEntitiesProcess.person
		namedEntity.organization = namedEntitiesProcess.organization
		namedEntity.facility = namedEntitiesProcess.facility
		namedEntity.location = namedEntitiesProcess.location
		try:		
			namedEntity.save()
		except Exception as e:
			print "Update Error!!!", e
"""