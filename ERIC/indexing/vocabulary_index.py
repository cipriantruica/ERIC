import pymongo

mapFunction = """function() {
					for (var idx=0; idx<this.words.length; idx++){
						var key = this.words[idx].word;
						var ids = {'docID': this.docID, 'count': this.words[idx].count, 'tf': this.words[idx].tf};
						var value = { 'ids': [ids]};
						emit(key, value);
					}
				}"""

reduceFunction = """function(key, values) {
						var result = {'ids': []};
						values.forEach(function (v) {
							result.ids = v.ids.concat(result.ids);
						});
						return result;
					}"""

functionCreate = """function(){
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
		}"""

functionUpdate = """function(startDate){
			var noDocs = db.documents.count();
			var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
			while(items.hasNext()){
				var item = items.next();
				var wordID = item._id;
				var exists = db.vocabulary.findOne({word: wordID}, {docIDs: 1, _id:0});
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
		}"""

functionDelete = """function (){
						var noDocs = db.documents.count();
						//update idf
						var words = db.vocabulary.find({},{_id: 0, word: 1}).addOption(DBQuery.Option.noTimeout);
						while(words.hasNext()){
							var word = words.next();
							var n = db.vocabulary.aggregate([
								{$match: {word: word.word}},
								{$project: { noWords: { $size: "$docIDs" }}}
							]);
							var noWords = 0;
							while(n.hasNext()){ 
								var v = n.next(); 
								noWords = v.noWords; 
							}
							if (noWords == 0){
								// delete words that have no related document								
								db.vocabulary.remove({word: word.word})
							}else{
								//update tfidf
								var widf = Math.round(Math.log(noDocs/noWords) * 100)/100;
								db.vocabulary.update({word: word.word}, {$set: {idf: widf}});
							}
						}
					}"""


class VocabularyIndex:
	def __init__(self, dbname):
		client = pymongo.MongoClient()
		self.db = client[dbname]
	
	def createIndex(self, query = None):
		self.db.vocabulary.drop();
		if query:
			self.db.words.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)
		else:
			self.db.words.map_reduce(mapFunction, reduceFunction, "temp_collection")
		self.db.eval(functionCreate)
		self.db.vocabulary.ensure_index("word")
		self.db.temp_collection.drop()

	#update index after docunemts are added
	def updateIndex(self, startDate):				
		query = {"createdAt": {"$gt": startDate } }
		self.db.words.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)
		self.db.eval(functionCreate, {'startDate': startDate})
		#self.db.temp_collection.drop()

	#docIDs - list of documents
	def deleteIndex(self, docIDs):
		#this is dependent on vocabulary
		#delete from vocabulary first
		for docID in docIDs:
			self.db.vocabulary.update({ }, { "$pull": { "docIDs" :{ "docID": docID } }}, multi=True );
		self.db.eval(functionDelete)