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
path="times/postgres/"

getCurrentTimeInMili() {
  date +'%H 3600 * %M 60 * + %S + 1000 * %N 1000000 / + p' | dc
}

FILE="../DATA_SETS/testing/rss_10000.csv"
DB="ERICDB"
echo $FILE
for i in `seq 1 $N`
do
	echo "test_$i"
	START=$(getCurrentTimeInMili)
	python testing_postgres.py $FILE $DELIMITER $HEADER $DB $LANGUAGE >> $path"10000_perforance"
	END=$(getCurrentTimeInMili)
	DIFF=$(( $END - $START ))
	echo "********************************" >> $path"10000_perforance"
	echo $DIFF >> $path"10000_script_times_populatedb"
done;
