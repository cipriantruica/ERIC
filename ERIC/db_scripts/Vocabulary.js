//db.documents.mapReduce( mapFunction, reduceFunction, { out: "inverted_index" })
/**
//construct vocabulary
//this keep the POS tagging - not accurate, same word, different POS tag
function createInvertedIndex(){
	db.inverted_index4.drop();
	db.inverted_index5.drop();
	
	mapFunction = function() {
		for (var idx=0; idx<this.words.length; idx++){
			var key = { "word": this.words[idx].word, "wtype": this.words[idx].wtype};
			var ids = {"docID": this._id, "count": this.words[idx].count, "tf": this.words[idx].tf};
			var value = { "ids": [ids]};
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

	var time = db.documents.mapReduce( mapFunction, reduceFunction, { out: "inverted_index4" });
	//print(time.timeMillis/1000.0);
	
	var noDocs = db.documents.count();

	var start = new Date();
	var items = db.inverted_index4.find().addOption(DBQuery.Option.noTimeout);
	while(items.hasNext()){
		var item = items.next();
		var n = item.value.ids.length;
		var widf = Math.log(noDocs/n);
		doc = {word: item._id.word, wtype: item._id.wtype, idf: widf, createdAt: new Date(), docIDs: item.value.ids};
		db.inverted_index5.insert(doc);
	}
	var end = new Date();
	print ((end.getTime() - start.getTime() + time.timeMillis)/1000.0)
	//db.inverted_index4.drop();	
}
**/


//construct vocabulary
//this does not keep the POS tag
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
	var time = db.words.mapReduce( mapFunction, reduceFunction, { out: "temp_collection" });
	//print(time.timeMillis/1000.0);
	
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

createVocabulary()


db.vocabulary.find({"word": "back"}).pretty()

function testing(n){
	for(var i=0; i<n; i++){
		createVocabulary();
	}
}

testing(20)