create or replace function IDF() returns void 
as $$
declare
	noDocs int;
	noWord int;
	curs CURSOR FOR SELECT id, word FROM words order by word;
begin
 select count(*) into noDocs from documents; 
 for rec in curs
 loop
	select count(documentid) into noWord 
	from vocabulary
	where wordid = rec.id;
	--raise notice 'id = %, word = %, nowords= %, idf=%', rec.id, rec.word, noWord, ln(noDocs/noWord);
	update vocabulary 
	set idf = ln(noDocs/noWord)
	where
		wordid=rec.id;
 end loop;
end;
$$ LANGUAGE plpgsql;