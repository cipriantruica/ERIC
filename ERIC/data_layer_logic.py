# coding: utf-8
import sys  
import utils
from models.mongo_models import *
from nlplib.lemmatize_text import LemmatizeText
from nlplib.named_entities import NamedEntitiesRegonizer
from nlplib.clean_text import CleanText

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

def populateDatabase(elem, language='EN'):
	cleanText = CleanText()
	title = cleanText.cleanText(elem[0], language)
	#verify if document exists
	document = Documents.objects(title=title).timeout(False)
	#document does not exist in the database, add new document
	if not document:
		document = Documents()
		document.title = title
		document.rawText = elem[1]
		document.intText = cleanText.cleanText(elem[1], language)
		document.date =elem[2]
		document.language = language
		#authors 
		#verify list's length - maybe it does not have the author field
		if len(elem) > 4:
			document.authors = [Author(name[0], name[1]) for name in utils.getAuthorName(elem[4])]
	else: #document exists in the datanase
		document = document[0]
		#add tags
	for c in cleanText.splitString(elem[3]):
		if c not in document.tags: #verify if tag exists
			document.tags.append(c)
	
	try:
		document.save()
	except Exception as e:
		print "Insert Error!!!", e


#this functions adds to the documents collection the cleanText and words labels
def createCleanTextField(startDate, endDate, language):
	documents = Documents.objects(Q(createdAt__gte = startDate) & Q(createdAt__lt = endDate)).only("id", "intText").timeout(False)
	for document in documents:		
		if document.intText and document.intText != " ":
			lemmas = LemmatizeText(document.intText, language)
			lemmas.createLemmaText()
			if lemmas.cleanText and lemmas.cleanText != " ":
				lemmas.createLemmas()
				words = [Word(word=word.word, tf=word.tf, count=word.count, wtype=word.wtype) for word in lemmas.wordList]
				try:
					#update document
					document.update(set__cleanText=lemmas.cleanText, set__words=words)
				except Exception as e:
					print "Update Error!!!", e

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
