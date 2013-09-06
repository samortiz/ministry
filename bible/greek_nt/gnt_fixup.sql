-- After import the gnt.sql file, run this to fix up the data

-- Add the columns for all the split up data
alter table greek_nt_import add column tense text;
alter table greek_nt_import add column voice text;
alter table greek_nt_import add column mood text;
alter table greek_nt_import add column person text;
alter table greek_nt_import add column number text;
alter table greek_nt_import add column gender text;
alter table greek_nt_import add column case_txt text;
alter table greek_nt_import add column part_of_speech text;

alter table greek_nt_import add column unknown_1 text;
alter table greek_nt_import add column unknown_2 text;


-- Set the parsing data 
update greek_nt_import set person=substring(parse, 1,1);
update greek_nt_import set tense=substring(parse, 2,1);
update greek_nt_import set voice=substring(parse, 3,1);
update greek_nt_import set mood=substring(parse, 4,1);
update greek_nt_import set case_txt=substring(parse, 5,1);
update greek_nt_import set number=substring(parse,6,1);
update greek_nt_import set gender=substring(parse,7,1);
update greek_nt_import set part_of_speech=substring(word_type,1,1);

update greek_nt_import set unknown_1=substring(word_type,2,1);
update greek_nt_import set unknown_2=substring(parse,8,1);


-- Lookup or generate the ids (add the id columns to the import table)
alter table greek_nt_import add column part_of_speech_id integer;
update greek_nt_import i set part_of_speech_id=(select id from lookup where group_type='part_of_speech' and code=i.part_of_speech);

alter table greek_nt_import add column tense_id integer;
update greek_nt_import i set tense_id=(select id from lookup where group_type='tense' and code=i.tense);

alter table greek_nt_import add column voice_id integer;
update greek_nt_import i set voice_id=(select id from lookup where group_type='voice' and code=i.voice);

alter table greek_nt_import add column mood_id integer;
update greek_nt_import i set mood_id=(select id from lookup where group_type='mood' and code=i.mood);

alter table greek_nt_import add column person_id integer;
update greek_nt_import i set person_id=(select id from lookup where group_type='person' and code=i.person);

alter table greek_nt_import add column number_id integer;
update greek_nt_import i set number_id=(select id from lookup where group_type='number' and code=i.number);

alter table greek_nt_import add column gender_id integer;
update greek_nt_import i set gender_id=(select id from lookup where group_type='gender' and code=i.gender);

alter table greek_nt_import add column case_id integer;
update greek_nt_import i set case_id=(select id from lookup where group_type='case' and code=i.case_txt);

alter table greek_nt_import add column verse_id integer;
update greek_nt_import i set verse_id=(select id from verse where book = CASE
 WHEN i.book_num='01' THEN 'Matt'
 WHEN i.book_num='02' THEN 'Mark'
 WHEN i.book_num='03' THEN 'Luke'
 WHEN i.book_num='04' THEN 'John'
 WHEN i.book_num='05' THEN 'Acts'
 WHEN i.book_num='06' THEN 'Rom'
 WHEN i.book_num='07' THEN '1 Cor'
 WHEN i.book_num='08' THEN '2 Cor'
 WHEN i.book_num='09' THEN 'Gal'
 WHEN i.book_num='10' THEN 'Eph'
 WHEN i.book_num='11' THEN 'Phil'
 WHEN i.book_num='12' THEN 'Col'
 WHEN i.book_num='13' THEN '1 Thes'
 WHEN i.book_num='14' THEN '2 Thes'
 WHEN i.book_num='15' THEN '1 Tim'
 WHEN i.book_num='16' THEN '2 Tim'
 WHEN i.book_num='17' THEN 'Titus'
 WHEN i.book_num='19' THEN 'Heb'
 WHEN i.book_num='20' THEN 'James'
 WHEN i.book_num='21' THEN '1 Pet'
 WHEN i.book_num='22' THEN '2 Pet'
 WHEN i.book_num='23' THEN '1 John'
 WHEN i.book_num='27' THEN 'Rev'
END 
 and chapter::integer=i.chap_num::integer
 and verse_num=i.verse_num::integer::text
);

update greek_nt_import i set verse_id=(select id from verse where book = CASE
 WHEN i.book_num='18' THEN 'Philem'
 WHEN i.book_num='24' THEN '2 John'
 WHEN i.book_num='25' THEN '3 John'
 WHEN i.book_num='26' THEN 'Jude'
END
 and chapter::integer=i.verse_num::integer
) where book_num in ('18', '24', '25', '26');

-- Strangely 3 John has 15 verses in NA26, but only 14 in RcV.
-- Verse 15 is actually the second half of verse 14 
update greek_nt_import set verse_id=30789 where book_num='25' and chap_num='01' and verse_num='15';


-- ------------ Data Validation ------------------
-- Check for any verses that didn't look up properly
select id, word, book_num, chap_num, verse_num, verse_id from greek_nt_import where verse_id is null;

select * from greek_nt_import where part_of_speech_id is null and part_of_speech != '';
select * from greek_nt_import where tense_id is null and tense != '-';
select * from greek_nt_import where voice_id is null and voice != '-';
select * from greek_nt_import where mood_id is null and mood != '-';
select * from greek_nt_import where person_id is null and person != '-';
select * from greek_nt_import where number_id is null and number != '-';
select * from greek_nt_import where gender_id is null and gender != '-';
select * from greek_nt_import where case_id is null and case_txt != '-';



-- Insert the data in the real table
insert into greek_nt (id, verse_id, greek, lemma, part_of_speech_id, 
 tense_id, voice_id, mood_id, person_id, number_id, gender_id, case_id) 
 (select
   id
 , verse_id
 , word
 , lemma
 , part_of_speech_id
 , tense_id
 , voice_id
 , mood_id
 , person_id
 , number_id
 , gender_id
 , case_id
  from greek_nt_import
 );








