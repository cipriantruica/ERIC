//construct vocabulary
//this does not keep the POS tag
function updateVocabularyUpdate(startDate){
	db.temp_collection.drop();
	
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
			intermediar.ids = v.ids.concat(intermediar.ids);
		});
		//remove duplicates
		for (i in intermediar.ids){
			if(i > 0){
				var ok = true;
				for (j in result.ids){
					if (result.ids[j].docID.toString() == intermediar.ids[i].docID.toString()){
						ok = false;
					}
				}
				if(ok){
					result.ids.push(intermediar.ids[i]);
				}
			}
			else{
				result.ids.push(intermediar.ids[i]);
			}
		}
		return result;
	};

	//var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "temp_collection" });
	var time = db.words.mapReduce( mapFunction, reduceFunction, { query: {createdAt: {$gt: startDate}}, out: "temp_collection" });
	//print(time.timeMillis/1000.0);
	
	var noDocs = db.documents.count();

	var start = new Date();
	/*
	var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var wordID = item._id;
		var dids = []
		dids = item.value.ids
		var exists = db.vocabulary.count({word: wordID});
		if (exists > 0){
				var word = db.vocabulary.find({word: wordID}, {docIDs: 1, _id:0});
				var docids_orig = [];
				var docids_vec = [];
				while(word.hasNext()){
					var w = word.next();
					docids_orig = w.docIDs;
				}
				docids_vec = docids_orig.concat(dids);
				var n = docids_vec.length;
				var widf = Math.round(Math.log(noDocs/n) * 100)/100;
				db.vocabulary.update({word: wordID}, {$set: {idf: widf, docIDs: docids_vec}});
		}else{
			var n = dids.length;
			var widf = Math.round(Math.log(noDocs/n) * 100)/100;
			doc = {word: wordID, idf: widf, createdAt: new Date(), docIDs: dids};
			db.vocabulary.insert(doc);
		}
	}
	*/
	var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var wordID = item._id;
		var exists = db.vocabulary.findOne({word: wordID}, {docIDs: 1, _id: 0});
		if (exists){
			var docIDs = exists.docIDs;
			docIDs = docIDs.concat(item.value.ids);
			var n = docIDs.length;
			var widf = Math.round(Math.log(noDocs/n) * 100)/100;
			db.vocabulary.update({word: wordID}, {$set: {idf: widf, docIDs: docIDs}});
		}else{
			var n = item.value.ids.length;
			var widf = Math.round(Math.log(noDocs/n) * 100)/100;
			doc = {word: wordID, idf: widf, createdAt: new Date(), docIDs: item.value.ids};
			db.vocabulary.insert(doc);
		}
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.temp_collection.drop();
}

updateVocabularyUpdate(ISODate("2015-04-15T23:01:05.176Z"))


db.vocabulary.find({"word": "back"}).pretty()

function testing(n){
	for(var i=0; i<n; i++){
		createVocabulary();
	}
}

testing(20)

db.vocabulary.findOne()