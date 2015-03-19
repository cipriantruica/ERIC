function createInvertedIndex(){
	db.inverted_index.drop();
	db.inverted_index2.drop();
	
	mapFunction = function() {
		var ids = []
		ids.push(this._id);
		for (var idx=0; idx<this.words.length; idx++){
			var key = this.words[idx].word;
			var value = { "ids": ids};
			emit(key, value);
		}
	}

	reduceFunction = function(key, values) {
		var result = {"ids": []};
		values.forEach(function (v) {
			result.ids = v.ids.concat(result.ids);
		});
		return result;
	};

	var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "inverted_index2" });
	//print(time.timeMillis/1000.0);

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

createInvertedIndex()

function testing(n){
	for(var i=0; i<n; i++){
		createInvertedIndex();
	}
}

testing(20)