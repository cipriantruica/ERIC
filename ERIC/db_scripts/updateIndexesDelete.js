function updateIndexesDelete(docIDs){
	var start = new Date();
	for (var idx in docIDs){
		db.documents.remove({_id: docIDs[idx]})
		db.words.remove({docID: docIDs[idx]});
		//remove document from vocabulary
		db.vocabulary.update(
			{ },
			{ $pull: { docIDs :{ docID: docIDs[idx] } }},
			{ multi: true }
		);
		//remove document from inveted index
		db.inverted_index.update(
			{ },
			{ $pull: { docIDs :{ docID: docIDs[idx] } }},
			{ multi: true }
		);
	}

	var noDocs = db.documents.count();
	//update idf
	var words = db.vocabulary.find().addOption(DBQuery.Option.noTimeout);
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
			db.inverted_index.remove({word: word.word});
			db.pos_index.remove({word: word.word});
			db.vocabulary.remove({word: word.word})
		}else{
			var widf = Math.round(Math.log(noDocs/noWords) * 100)/100;
			db.vocabulary.update({word: word.word}, {$set: {idf: widf}});	
		}
	}
	var end = new Date();
	print ((end.getTime() - start.getTime())/1000.0)
}


/*
//This ar tests
db.inverted_index.update(
			{ },
			{ $pull: { docIDs :{ docID: ObjectId("552e7c928528d40d01d36b78") } }},
			{multi: true}
		);


db.inverted_index.find({"docIDs": {$eq: 1} });

db.inverted_index.find({"docIDs.$": {$exists: false}})

db.vocabulary.aggregate([
		{$match: {word: "back"}},
		{$project: { noWords: { $size: "$docIDs" }}}
		]);

var docIDs = [  ObjectId("552ec0ae8528d40ce30f5c38"), ObjectId("552ec0ae8528d40ce30f5c3b"), ObjectId("552ec0ae8528d40ce30f5c3c")]

updateIndexesDelete(docIDs)

db.vocabulary.find({word: "back"}, {idf: 1})

db.inverted_index.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c38")})
db.inverted_index.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3b")})
db.inverted_index.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3c")})

db.documents.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c38")})
db.documents.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3b")})
db.documents.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3c")})

db.vocabulary.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c38")})
db.vocabulary.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3b")})
db.vocabulary.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3c")})

db.words.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c38")})
db.words.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3b")})
db.words.find({"docIDs.docID": ObjectId("552ec0ae8528d40ce30f5c3c")})


db.pos_index.find({"word":  "abandon"})
db.vocabulary.find({"word":  "abandon"})
db.inverted_index.find({"word":  "abandon"})

db.documents.count()
db.words.count()
*/