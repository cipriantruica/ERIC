#!/bin/bash

#args:
#1 - file
#2 - delimiter
#3 - has header
#4 - Database name
#example: python populateDB.py DATA_SETS/news_articles/rss.csv t 1 2 ERICDB

N=$1

HEADER=1
DELIMITER="t"
LMTZ=1
OP=1
LANGUAGE=$2
path="times/mongo/"

getCurrentTimeInMili() {
  date +'%H 3600 * %M 60 * + %S + 1000 * %N 1000000 / + p' | dc
}

FILE="../DATA_SETS/testing/rss_500.csv"
DB="ERICDB"
echo $FILE
for i in `seq 1 $N`
do
	echo "test_$i"
	START=$(getCurrentTimeInMili)
	python testing_mongo.py $FILE $DELIMITER $HEADER $DB $LANGUAGE >> $path"500_perforance"
	END=$(getCurrentTimeInMili)
	DIFF=$(( $END - $START ))
	echo "*******************" >> $path"500_perforance"
	echo $DIFF >> $path"500_script_times_populatedb"
done;
