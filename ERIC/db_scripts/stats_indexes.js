createInvertedIndex()
createPOSIndex()
createVocabulary()

function testing(n){
	print("pos=[");
	for(var i=0; i<n; i++){
		createPOSIndex();
		print(",");
	}
	print("]");
	print("iv=[");
	for(var i=0; i<n; i++){
		createInvertedIndex();
		print(",");
	}
	print("]");
	
	print("vocab=[");
	for(var i=0; i<n; i++){
		createVocabulary();
		print(",");
	}
	print("]");
	print("print \"pos:\", round(sum(pos)/len(pos),2)");
	print("print \"iv:\", round(sum(iv)/len(iv),2)");
	print("print \"vocabulary:\", round(sum(vocab)/len(vocab),2)");
}

db.documents.stats()
db.words.stats()
db.pos_index.stats()
db.inverted_index.stats()
db.vocabulary.stats()


updateVocabularyUpdate(ISODate("2015-04-16T00:37:04.083Z"))
updatePOSIndex(ISODate("2015-04-16T00:37:04.083Z"))
updateInvertedIndexUpdate(ISODate("2015-04-16T00:37:04.083Z"))

//for postgres
SELECT
   a.relname as "Table",
   (SELECT n_live_tup FROM pg_stat_user_tables where relname=a.relname) NoRecs,
   pg_size_pretty(pg_total_relation_size(a.relid)) As "Size"
   FROM pg_catalog.pg_statio_user_tables a ORDER BY pg_total_relation_size(relid) DESC;


