function createPOSIndex(){
	db.pos_index.drop();
	db.temp_collection.drop();
	
	mapFunction = function() {
		for (var idx=0; idx<this.words.length; idx++){
			var pos = []
			var key = this.words[idx].word;
			pos.push(this.words[idx].wtype);
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

	//var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "temp_collection" });
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

createPOSIndex()

function testing(n){
	for(var i=0; i<n; i++){
		createPOSIndex();
	}
}

testing(20)