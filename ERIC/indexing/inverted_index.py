import pymongo
import time

mapFunction = """function() {
			var ids = [];
			//ids.push(this.docID.valueOf())
			ids.push(this.docID)
			for (var i in this.words){
				var key = this.words[i].word;
				var value = { "ids": ids};
				emit(key, value);
			}
		}"""

reduceFunction = """function(key, values) {
			var result = {"ids": []};
			values.forEach(function (v) {
				result.ids = v.ids.concat(result.ids)
			});
			return result;
		}"""

function = """function(){
			var items = db.inverted_index2.find().addOption(DBQuery.Option.noTimeout);
			while(items.hasNext()){
				var item = items.next();
				doc = {word: item._id, createdAt: new Date(), docIDs: item.value.ids};
				db.inverted_index.insert(doc);
			}
		}"""

class CreateInvertedIndex:
	def __init__(self, dbname, query=None):		
		client = pymongo.MongoClient()
		db = client[dbname]
		db.inverted_index.drop();
		if query:
			db.words.map_reduce(mapFunction, reduceFunction, "inverted_index2", query = query)
		else:
			db.words.map_reduce(mapFunction, reduceFunction, "inverted_index2")
		db.eval(function)
		db.inverted_index.ensure_index("word")


"""
start = time.time() 
CreateInvertedIndex('ERICDB')
end = time.time()
print (end - start)
"""