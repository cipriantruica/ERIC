function updateInvertedIndexUpdate(startDate){
	db.inverted_index2.drop();
	
	mapFunction = function() {
		var ids = [];
		ids.push(this.docID.valueOf())
		for (var i in this.words){
			var key = this.words[i].word;
			var value = { "ids": ids};
			emit(key, value);
		}
	}

	reduceFunction = function(key, values) {
		var result = {"ids": []};
		values.forEach(function (v) {
			result.ids = v.ids.concat(result.ids.filter(function (item) {
								return v.ids.indexOf(item) < 0;
								}));
		});

		return result
	};

	//var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "inverted_index2" });
	var time = db.words.mapReduce( mapFunction, reduceFunction, {query: {createdAt: {$gt: startDate}}, out: "inverted_index2" });
	//print(time.timeMillis/1000.0);

	var start = new Date();
	var items = db.inverted_index2.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var dids = []
		for (var i in item.value.ids){
			dids.push(new ObjectId(item.value.ids[i]));
		}

		var exists = db.inverted_index.count({word: item._id});
		if (exists > 0){
				var word = db.inverted_index.find({word: item._id}, {docIDs: 1, _id:0});
				var docids_orig = []
				var docids_vec = []
				while(word.hasNext()){
					var item = word.next();
					docids_orig = item.docIDs;
				}
				for(var i in dids){
					docids_vec.push(dids[i]);
				}
				for(var i in docids_orig){
					docids_vec.push(docids_orig[i])
				}
				db.inverted_index.update({word: item._id}, {$set: {docIDs: docids_vec}});
		}else{
			doc = {word: item._id, createdAt: new Date(), docIDs: dids};
			db.inverted_index.insert(doc);
		}
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.inverted_index2.drop();
}

updateInvertedIndexUpdate(ISODate("2015-04-15T23:01:05.176Z"))

 db.inverted_index.find({"word": "back"}).pretty()

function testing(n){
	for(var i=0; i<n; i++){
		createInvertedIndex();
	}
}

testing(20)