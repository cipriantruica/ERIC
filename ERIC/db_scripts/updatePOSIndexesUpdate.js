function updatePOSIndex(startDate){
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

	var time = db.words.mapReduce( mapFunction, reduceFunction, { query: {createdAt: {$gt: startDate}}, out: "temp_collection" });

	var start = new Date();
	var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var pos_uniq = item.value.pos.reduce(function(a,b){
			if (a.indexOf(b) < 0 ) 	{
				a.push(b); 
			}
			return a;   },[]);
		var exists = db.pos_index.count({word: item._id});
		if (exists > 0){
				var word = db.pos_index.find({word: item._id}, {pos: 1, _id:0});
				var pos_orig = []
				var pos_vec = []
				while(word.hasNext()){
					var item = word.next();
					pos_orig = item.pos;
				}
				pos_vec = pos_uniq.concat(pos_orig.filter(function (item) {
								return pos_uniq.indexOf(item) < 0;
								}));
				print (pos_vec);
				//db.pos_index.update({word: item._id}, {$set: {pos: pos_vec}});
		}else{
			doc = {word: item._id, createdAt: new Date(), pos: pos_uniq};
			db.pos_index.insert(doc);
		}
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	db.temp_collection.drop();

}

updatePOSIndex(ISODate("2015-04-15T23:01:05.176Z"))

function testing(n){
	for(var i=0; i<n; i++){
		createPOSIndex();
	}
}

testing(20)

ISODate("2015-04-15T23:01:05.176Z")