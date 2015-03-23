import sys
import threading
import time
import gc
import shutil
from datetime import timedelta
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from data_layer_logic import *
from models.mongo_models import *




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

def clean(language):	
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
	
	"""
	#method 1
	pool = ThreadPool(no_threads)
	for idx in xrange(0, len(list_of_dates)-1, 1) :
		#print list_of_dates[idx], list_of_dates[idx+1]		
		#pool.apply_async(func = createCleanTextField_orig, args=(list_of_dates[idx], list_of_dates[idx+1], ))
		pool.apply_async(func = createCleanTextField, args=(list_of_dates[idx], list_of_dates[idx+1], idx+1,  ))
	pool.close()
	pool.join()
	"""
	
	#method 2
	with ThreadPoolExecutor(max_workers = no_threads) as e:
		for idx in xrange(0, len(list_of_dates)-1, 1) :
			 e.submit(createCleanTextField, list_of_dates[idx], list_of_dates[idx+1], language)
	
	end = time.time() 
	print "time clean text:", (end - start)

	#TO_DO this is just a test, remove this line
	#createCleanTextField(list_of_dates[0], list_of_dates[1], language)

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


def main(filename, csv_delimiter = '\t', header = True, dbname = 'ERICDB', language='EN'):
	connectDB(dbname)
	Documents.drop_collection()
	populateDB(filename, csv_delimiter, header, language)
	Documents.objects(intText__exists = False).delete()
	#this curretnly work only for English
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
