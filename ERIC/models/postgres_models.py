from pony.orm import *
from datetime import datetime

db = Database()
db.bind('postgres', user='postgres', password='123456', host='localhost', database='ERICDB')

class Documents(db.Entity):
	id = PrimaryKey(int, auto=True)
	title = Required(unicode, unique=True)
	rawText = Optional(unicode)
	intText = Optional(unicode) #intermediate text without stopwords, punctuation, etc
	cleanText = Optional(unicode) #lemma text
	#the date the element was inserted in the database
	createdAt = Required(datetime, sql_default='CURRENT_TIMESTAMP')
	#the date inside the document if any
	date = Optional(datetime)
	language = Optional(unicode)
	authorID = Set('Authors')
	tagID = Set('Tags')
	vocabularyID = Set('Vocabulary')
	posIndexID = Set('POSIndex')
	

class Authors(db.Entity):
	id = PrimaryKey(int, auto=True)	
	firstname = Optional(unicode)
	lastname = Optional(unicode)
	documentID = Set('Documents')
	composite_key(firstname, lastname)

class Tags(db.Entity):
	id = PrimaryKey(int, auto=True)	
	tag = Required(unicode)	
	documentID = Set('Documents')

class Words(db.Entity):
	id = PrimaryKey(int, auto=True)	
	word = Required(unicode, unique=True)
	vocabularyID = Set('Vocabulary')
	posIndexID = Set('POSIndex')
	poswordID = Set('Pos_Words')
	

class Vocabulary(db.Entity):
	count = Optional(float)
	tf = Optional(float)
	idf = Optional(float)	
	documentID = Required('Documents')
	wordID = Required('Words')
	#PrimaryKey(documents,)

class POS(db.Entity):
	pos = Required(unicode)	
	posIndexID = Set('POSIndex')
	poswordID = Set('Pos_Words')

class POSIndex(db.Entity):
	wordID = Required('Words')
	documentID = Required('Documents')
	posID = Required('POS')	

class Pos_Words(db.Entity):
	wordID = Required('Words')
	posID = Required('POS')

db.generate_mapping(check_tables=False)

def dropAllTables():	
	db.drop_all_tables(with_all_data=True)

def createAllTables():
	db.create_tables()