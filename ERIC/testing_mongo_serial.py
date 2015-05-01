import sys
import threading
import time
import gc
import shutil
from datetime import timedelta, datetime
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from ddl_mongo import *
from models.mongo_models import *
from indexing.vocabulary_index import VocabularyIndex as VI
from indexing.inverted_index import InvertedIndex as IV
from indexing.pos_index import POSIndex as PI

#this script receives 5 parameters
# 1 - filename
# 2 - the csv delimiter: t - tab, c - coma, s - semicolon
# 3 - integer: 1 csv has header, 0 csv does not have hearer
# 4 - integer - nr of threads
# 5 - lematizer/stemmer

def getDates():
	documents = Documents.objects.only("createdAt").order_by("-createdAt").first()
	last_docDate = None
	last_wordDate = None
	if documents:
		last_docDate = documents.createdAt
	words = Words.objects.only("createdAt").order_by("-createdAt").first()
	if words:
		last_wordDate = words.createdAt
	return last_docDate, last_wordDate

def populateDB(filename, csv_delimiter, header, language):
	start = time.time() 
	h, lines = utils.readCSV(filename, csv_delimiter, header)
	for line in lines:
		populateDatabase(line, language)
	end = time.time() 
	print "time_populate.append(", (end - start), ")"

def clean(language, last_docDate=None):
	if not last_docDate:
		documents = Documents.objects.only("createdAt")
	else:
		documents = Documents.objects(Q(createdAt__gte = last_docDate)).only("createdAt")
	no_docs = documents.count()
	
	list_of_dates = []
	idx = 0
	for document in documents:		
		if idx%100 == 0 or idx + 1 == no_docs:
			list_of_dates.append(document.createdAt)
		idx += 1
	#add one second to the last date
	list_of_dates[-1] += timedelta(0,1)
	
	start = time.time() 
	for idx in xrange(0, len(list_of_dates)-1, 1) :
		createCleanTextField(list_of_dates[idx], list_of_dates[idx+1], language)
	
	end = time.time() 
	print "time_cleantext.append(", (end - start), ")"

	#TO_DO this is just a test, remove this line
	#createCleanTextField(list_of_dates[0], list_of_dates[1], language)
	#createCleanTextField(list_of_dates[1], list_of_dates[2], language)

	#delete documents without cleanText
	Documents.objects(cleanText__exists = False).delete();

def buildNamedEntities():
	print "sunt in build entities"

	documents = Documents.objects.only("createdAt")
	no_docs = documents.count()
	
	list_of_dates = []
	idx = 0

	for document in documents:		
		if idx%100 == 0 or idx + 1 == no_docs:
			list_of_dates.append(document.createdAt)
		idx += 1
	#add one second to the last date
	list_of_dates[-1] += timedelta(0,1)
	
	no_threads = cpu_count()
		
	start = time.time()
	with ThreadPoolExecutor(max_workers = no_threads) as e:
		for idx in xrange(0, len(list_of_dates)-1, 1) :
			 e.submit(createNamedEntitiesCollection, list_of_dates[idx], list_of_dates[idx+1])
	end = time.time() 
	
	print "time build named entities:", (end - start) 

def constructIndexes(dbname):
	start = time.time()
	vocab = VI(dbname)
	vocab.createIndex()
	end = time.time()
	print "vocabulary_build.append(", (end - start) , ")"
	start = time.time()
	iv = IV(dbname)
	iv.createIndex()
	end = time.time()
	print "inverted_build.append(", (end - start) , ")"
	start = time.time()
	pi = PI(dbname)
	pi.createIndex()
	end = time.time()
	print "pos_build.append(", (end - start) , ")"

def updateIndexes(dbname, startDate):
	start = time.time()
	vocab = VI(dbname)
	vocab.updateIndex(startDate)
	end = time.time()	
	print "vocabulary_update.append(", (end - start) , ")"
	start = time.time()
	iv = IV(dbname)
	iv.updateIndex(startDate)
	end = time.time()
	print "inverted_update.append(", (end - start) , ")"
	start = time.time()
	pi = PI(dbname)
	pi.updateIndex(startDate)
	end = time.time()
	print "pos_update.append(", (end - start) , ")"
	
def deleteFromIndexes(dbname, docIDs):
	start = time.time()
	vocab = VI(dbname)
	vocab.deleteIndex(docIDs)
	end = time.time()
	print "vocabulary_delete.append(", (end - start) , ")"
	start = time.time()
	iv = IV(dbname)
	iv.deleteIndex(docIDs)
	end = time.time()
	print "inverted_delete.append(", (end - start) , ")"
	start = time.time()
	pi = PI(dbname)
	pi.deleteIndex()
	end = time.time()
	print "pos_delete.append(", (end - start) , ")"

def deleteDocuments(startDate):
	docIDs = []
	documents = Documents.objects(Q(createdAt__gt = startDate)).only("id")
	for document in documents:
		docIDs.append(document.id)
		document.delete()
	for docID in docIDs:
		Words.objects(docID=docID).delete()
	#print docIDs
	return docIDs

def main(filename, csv_delimiter = '\t', header = True, dbname = 'ERICDB', language='EN', initialize=0):
	connectDB(dbname)
	#initialize everything from the stat
	if initialize == 0:
		Documents.drop_collection() 
		Words.drop_collection()	
		populateDB(filename, csv_delimiter, header, language)
		Documents.objects(intText__exists = False).delete()
		clean(language)
		constructIndexes(dbname)
	elif initialize == 1: #update the database with new information not tested, should work
		print 'Update'
		last_docDate, last_wordDate = getDates()
		populateDB(filename, csv_delimiter, header, language)
		Documents.objects(intText__exists = False).delete()
		clean(language, last_docDate)
		updateIndexes(dbname, last_wordDate)
		print 'Update Create indexes'
		constructIndexes(dbname)
		#print 'last date words:', last_wordDate
		#print 'last date documents:', last_docDate		
	#elif initialize == 2: #update indexes after documents where deleted
		print 'Delete'
		docIDs = deleteDocuments(last_docDate)
		deleteFromIndexes(dbname, docIDs)
		print 'Delete Create Indexes'
		constructIndexes(dbname)
	#NamedEntities.drop_collection()
	#buildNamedEntities()
	

if __name__ == "__main__":
	filename = sys.argv[1]
	csv_delimiter = utils.determineDelimiter(sys.argv[2])
	header = bool(sys.argv[3])
	dbname = sys.argv[4]
	language = sys.argv[5]
	initialize = int(sys.argv[6])
	main(filename, csv_delimiter, header, dbname, language, initialize)
