/**
* Add this indexes to the DB
**/

db.documents.ensureIndex( { "cleanText": "text" } )
db.words.ensureIndex( { "words.word": 1 } )
db.words.ensureIndex( { "docID": 1 } )
db.words.ensureIndex( { "createdAt": 1 } )

/**
* Commands to drop all the indexes on a collection if needed
**/
db.runCommand({dropIndexes: "documents", index: "*"});
db.runCommand({dropIndexes: "words", index: "*"});
