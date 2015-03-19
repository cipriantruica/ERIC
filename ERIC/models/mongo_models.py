from mongoengine import *
from datetime import datetime
from bson.objectid import ObjectId

def connectDB(dbname = 'ERICDB'):
	connect(dbname)

class Documents(Document):
	title = StringField(max_length = 255, required = True, unique=True)
	rawText = StringField()
	intText = StringField() #intermediate text without stopwords, punctuation, etc
	cleanText = StringField() #lemma text
	#the date the element was inserted in the database
	createdAt = DateTimeField(default=datetime.now)
	#createdAt = ComplexDateTimeField(default=datetime.now) 
	#the date inside the document if any
	date = DateTimeField()
	authors = ListField(EmbeddedDocumentField("Author"), required = False)
	tags = ListField()
	words = ListField(EmbeddedDocumentField("Word"))

	meta = {
		'ordering': ['+createdAt'],
		'indexes': [
			{
				'fields': ['+createdAt'],
				'unique': True,
				'sparse': False
			},
			{
				'fields': ['words']
			}
		]
	}

	"""
	,
	{
		'fields': ["$cleanText"],
		'default_language': 'english'
	},
	{
		'fields': ['words'],
		'unique': True,
		'sparse': False
	},
	{
		'fields': ['words.word'],
		'unique': True,
		'sparse': False
	}
	"""

class Author(EmbeddedDocument):
	_auto_id_field = False
	firstname = StringField(max_length = 255)
	lastname = StringField(max_length = 255)

class Word(EmbeddedDocument):
	_auto_id_field = False
	word = StringField(max_length = 255)
	wtype = StringField(max_length = 255)
	count = FloatField()
	tf = FloatField()
	idf = FloatField()
	tfidf = FloatField()

	meta = {
		'ordering': ['-word']
	}

class InvertedIndex(Document):
	word = StringField(max_length = 255, required = True, unique=True)
	docIDs = ListField()
	createdAt = DateTimeField(default=datetime.now) 

	meta = { 
			'ordering': ['+createdAt'], 
#			'indexes': [
#				{
#					'fields': ['+createdAt'],
#					'unique': True,
#					'sparse': False
#				}
#		]
	}

class Vocabulary(Document):
	word = StringField(max_length = 255, required = True, unique=True)
	idf = FloatField()
	#wtype = StringField(max_length = 255, required = True) #not yet implemented
	createdAt = DateTimeField(default=datetime.now)
	docIDs = ListField(EmbeddedDocumentField("Docs"))

	meta = {
			'indexes': [
				{
					'fields': ['+word'],
					'unique': True,
					'sparse': False
				}
		]
	}

class Docs(EmbeddedDocument):
	_auto_id_field = False
	#docId = ReferenceField("Documents", dbref=False)
	docID = ObjectIdField()
	count = FloatField()
	tf = FloatField()
	wtype = StringField(max_length = 255)

class NamedEntities(Document):
	docID = ObjectIdField()
	gpe = ListField()
	person = ListField()
	organization = ListField()
	facility = ListField()
	location = ListField()
