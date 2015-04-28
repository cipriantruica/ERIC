from itertools import combinations
import psycopg2
from gensim.utils import lemmatize
from nlplib.clean_text import CleanText
import time

cleanText = CleanText()

def subQueries(searchPhrase):
	words = [word[:-3] for word in lemmatize(cleanText.removeStopWords(cleanText.cleanText(searchPhrase)))]
	words = searchPhrase.split(""" """)
	searchWords = []
	for L in range(len(words) + 1, 0, -1):
		for subset in combinations(words, L):
			searchWords.append(list(subset))
	return searchWords

def construnctQuery(searchPhrase, k):
	search = subQueries(searchPhrase)
	queries1 = []
	for elem in search:
		queries2 = []
		for word in elem:
			text = """\t\tselect v.documentid, v.idf*v.tf tfidf from vocabulary v inner join words w on w.id = v.wordid and word = '"""+word +"""'"""
			queries2.append(text)
		queries1.append("""\n\t\tintersect\n""".join(query for query in queries2))
	scores = []
	for query in queries1:
		score = """select documentid, sum(tfidf) score1\n\tfrom\n\t(\n""" + query +"""\n\t) a\n\tgroup by documentid"""
		scores.append(score)
	reunion = """\n\tunion\n\t""".join(query for query in scores)
	query = """select documentid, max(score1) score\nfrom\n(\n\t"""+ reunion +"""\n) b\ngroup by documentid\norder by score desc\nlimit """+k
	return query
 
def executeQuery(searchPhrase, k):	
	try:
		conn = psycopg2.connect(dbname='ERICDB', user='postgres', password='123456', host='127.0.0.1', port='5432')		
		try:
			cur = conn.cursor()
			query = construnctQuery(searchPhrase, k)		
			cur.execute(query)
		except Exception as e:
			print "Error execute query\n", e
	
		rows = cur.fetchall()
		#print "\nRows: \n"
		#for row in rows:
		#	print "   ", row
	except Exception as e:
		print "I am unable to connect to the database.\n", e


if __name__ == "__main__":
	#searchPhrase = "absurd"
	#searchPhrase = "absurd ability"
	#searchPhrase = "absurd ability action"
	#searchPhrase = "absurd ability action back"
	searchPhrase = "absurd ability action back go"
	
	start = time.time()
	search = executeQuery(searchPhrase, "20")
	end = time.time() 
	print 'time_5_words.append(', (end-start), ')'

