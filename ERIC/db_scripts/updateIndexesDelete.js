function updateIndexesDelete(docIDs){
	for (var idx in docIDs){
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
	
	//TO DO
	// delete words that have no related document

	var noDocs = db.documents.count();
	//update idf
	var words = db.vocabulary.find().addOption(DBQuery.Option.noTimeout);
	while(words.hasNext()){
		var word = words.next();
		var n = db.vocabulary.aggregate([
		{$match: {word: word.word}},
		{$project: { noWords: { $size: "$docIDs" }}}
		]);
		var noWords = 1;
		while(n.hasNext()){ 
			var v = n.next(); 
			noWords = v.noWords; 
		}
		var widf = Math.round(Math.log(noDocs/noWords) * 100)/100;
		db.vocabulary.update({word: word.word}, {$set: {idf: widf}});
	}
}

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

var docIDs = [ ObjectId("552e7c928528d40d01d36b7b")]

updateIndexesDelete(docIDs)

db.vocabulary.find({word: "back"}, {idf: 1})

