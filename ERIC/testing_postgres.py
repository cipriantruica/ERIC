import sys
import threading
import time
import gc
import shutil
import math
from datetime import timedelta
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from ddl_postgres import *
from models.postgres_models import *
import pony.orm as pny





#this script receives 5 parameters
# 1 - filename
# 2 - the csv delimiter: t - tab, c - coma, s - semicolon
# 3 - integer: 1 csv has header, 0 csv does not have hearer
# 4 - integer - nr of threads
# 5 - lematizer/stemmer

def populateDB(filename, csv_delimiter, header, language):
	start = time.time() 
	h, lines = utils.readCSV(filename, csv_delimiter, header)
	for line in lines:
		populateDatabase(line, language)
	end = time.time() 
	print "time populate db:", (end - start)

@db_session
def updateVocabulary():
	documents = pny.select(d for d in Documents).order_by(Documents.createdAt)
	no_docs = len(documents)
	#update vocabulary with idf
	words = Words.select()
	for word in words:
		vocabulary = Vocabulary.select(lambda v: v.wordID == word)
		noDocWords = len(vocabulary)
		for v in vocabulary:
			v.idf = round(math.log(float(no_docs)/float(noDocWords)))

@db_session
def getListOfDates():
	documents = pny.select(d for d in Documents).order_by(Documents.createdAt)
	no_docs = len(documents)
	list_of_dates = []
	idx = 0

	for document in documents:		
		if idx%100 == 0 or idx + 1 == no_docs:
			list_of_dates.append(document.createdAt)
		idx += 1
	#add one second to the last date
	list_of_dates[-1] += timedelta(0,1)
	return list_of_dates

def clean(language):	
	list_of_dates = getListOfDates()

	no_threads = cpu_count()
	start = time.time()
	
	
	#method 2
	"""
	with ThreadPoolExecutor(max_workers = no_threads) as e:
		for idx in xrange(0, len(list_of_dates)-1, 1) :
			try:
				e.submit(createCleanTextField, list_of_dates[idx], list_of_dates[idx+1], language)
			except Exception as e:
				print e
	"""
	
	
	
	#TO_DO this is just a test, remove this line
	for idx in xrange(0, len(list_of_dates)-1, 1) :
		createCleanTextField(list_of_dates[idx], list_of_dates[idx+1], language)
	#createCleanTextField(list_of_dates[0], list_of_dates[1], language)

	
	updateVocabulary()

	end = time.time() 
	print "time clean text:", (end - start)
	#delete documents without cleanText
	#Documents.objects(cleanText__exists = False).delete();
	
"""
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
"""

def main(filename, csv_delimiter = '\t', header = True, dbname = 'ERICDB', language='EN'):
	dropAllTables()
	createAllTables()
	populateDB(filename, csv_delimiter, header, language)
	clean(language)
	#NamedEntities.drop_collection()
	#buildNamedEntities()
	

if __name__ == "__main__":
	filename = sys.argv[1]
	csv_delimiter = utils.determineDelimiter(sys.argv[2])
	header = bool(sys.argv[3])
	dbname = sys.argv[4]
	language = sys.argv[5]
	main(filename, csv_delimiter, header, dbname, language)
