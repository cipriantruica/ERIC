db.words.ensureIndex( { "words.word": 1 } )
db.words.ensureIndex( { "docID": 1 } )
db.words.ensureIndex( { "createdAt": 1 } )

function createPOSIndex(){
	db.pos_index.drop();
	db.temp_collection.drop();
	
	mapFunction = function() {
		for (var idx=0; idx<this.words.length; idx++){
			var key = this.words[idx].word;
			pos = this.words[idx].wtype;
			var value = { "pos": pos};
			emit(key, value);
		}
	}
	
	reduceFunction = function(key, values) {
		var result = {"pos": []};
		values.forEach(function (v) {
			result.pos = v.pos.concat(result.pos);
		});
		
		return result;
	};
	var time = db.words.mapReduce( mapFunction, reduceFunction, { out: "temp_collection" });
	var start = new Date();
	var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		pos_uniq = item.value.pos.reduce(function(a,b){
			if (a.indexOf(b) < 0 ) 	{
				a.push(b); 
			}
			return a;   },[]);
		doc = {word: item._id, createdAt: new Date(), pos: pos_uniq};
		db.pos_index.insert(doc);
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.temp_collection.drop();
}

function createInvertedIndex(){
	db.inverted_index.drop();
	db.inverted_index2.drop();
	
	mapFunction = function() {
		var ids = [];
		ids.push(this.docID)
		for (var i in this.words){
			var key = this.words[i].word;
			var value = { "ids": ids};
			emit(key, value);
		}
	}
	reduceFunction = function(key, values) {
		var result = {"ids": []};
		values.forEach(function (v) {
			result.ids = v.ids.concat(result.ids)
		});

		return result
	};
	var time = db.words.mapReduce( mapFunction, reduceFunction, { out: "inverted_index2" });
	var start = new Date();
	var items = db.inverted_index2.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		doc = {word: item._id, createdAt: new Date(), docIDs: item.value.ids};
		db.inverted_index.insert(doc);
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.inverted_index2.drop();
}

function createVocabulary(){
	db.temp_collection.drop();
	db.vocabulary.drop();
	
	mapFunction = function() {
		for (var idx=0; idx<this.words.length; idx++){
			var key = this.words[idx].word;
			var ids = {"docID": this.docID, "count": this.words[idx].count, "tf": this.words[idx].tf};
			var value = { "ids": [ids]};
			emit(key, value);
		}
	}
	reduceFunction = function(key, values) {
		var result = {"ids": []};
		var intermediar = {"ids": []};
		values.forEach(function (v) {
			result.ids = v.ids.concat(result.ids);
		});
		return result;
	};
	var time = db.words.mapReduce( mapFunction, reduceFunction, { out: "temp_collection" });
	var noDocs = db.documents.count();
	var start = new Date();
	var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var n = item.value.ids.length;
		var widf = Math.round(Math.log(noDocs/n) * 100)/100;
		doc = {word: item._id, idf: widf, createdAt: new Date(), docIDs: item.value.ids};
		db.vocabulary.insert(doc);
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.temp_collection.drop();
}

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

testing(5)

db.documents.stats()
db.words.stats()
db.pos_index.stats()
db.inverted_index.stats()
db.vocabulary.stats()

/*
updateVocabularyUpdate(ISODate("2015-04-16T00:37:04.083Z"))
updatePOSIndex(ISODate("2015-04-16T00:37:04.083Z"))
updateInvertedIndexUpdate(ISODate("2015-04-16T00:37:04.083Z"))
//for postgres
SELECT
   a.relname as "Table",
   (SELECT n_live_tup FROM pg_stat_user_tables where relname=a.relname) NoRecs,
   pg_size_pretty(pg_total_relation_size(a.relid)) As "Size"
   FROM pg_catalog.pg_statio_user_tables a ORDER BY pg_total_relation_size(relid) DESC;
*/
