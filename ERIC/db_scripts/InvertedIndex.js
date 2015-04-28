function createInvertedIndex(){
	db.inverted_index.drop();
	db.inverted_index2.drop();
	
	mapFunction = function() {
		var ids = [];
		//ids.push(this.docID.valueOf())
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
		return result;
	};

	//var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "inverted_index2" });
	var time = db.words.mapReduce( mapFunction, reduceFunction, { out: "inverted_index2" });
	//print(time.timeMillis/1000.0);

	var start = new Date();
	var items = db.inverted_index2.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		/*
		var dids = []
		for (var i in item.value.ids){
			dids.push(new ObjectId(item.value.ids[i]));
		}
		*/
		doc = {word: item._id, createdAt: new Date(), docIDs: item.value.ids};
		db.inverted_index.insert(doc);
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.inverted_index2.drop();
}

createInvertedIndex()

 db.inverted_index.find({"word": "back"}).pretty()

function testing(n){
	for(var i=0; i<n; i++){
		createInvertedIndex();
	}
}

testing(20)