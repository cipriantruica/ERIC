/**
* Add this indexes to the DB
**/

db.documents.ensureIndex( { "words.word": 1 } )
db.documents.ensureIndex( { "cleanText": "text" } )

/**
* Commands to drop all the indexes on a collection if needed
**/
db.runCommand({dropIndexes: "documents", index: "*"});
db.runCommand({dropIndexes: "inverted_index", index: "*"});
