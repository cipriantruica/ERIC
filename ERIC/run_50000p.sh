#!/bin/bash

#args:
#1 - file
#2 - delimiter
#3 - has header
#4 - Database name
#5 - language EN | FR
#example: python populateDB.py DATA_SETS/news_articles/rss.csv t 1 2 ERICDB EN

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

FILE="../DATA_SETS/testing/rss_50000.csv"
DB="ERICDB"
echo $FILE
for i in `seq 1 $N`
do
	echo "test_$i"
	START=$(getCurrentTimeInMili)
	python testing_postgres.py $FILE $DELIMITER $HEADER $DB $LANGUAGE >> $path"50000_perforance"
	END=$(getCurrentTimeInMili)
	DIFF=$(( $END - $START ))
	echo "********************************" >> $path"50000_perforance"
	echo $DIFF >> $path"50000_script_times_populatedb"
done;
