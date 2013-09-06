-- Import young's literal translation into the database
create table youngs_import (
   book_num text
 , book text
 , chapter text
 , verse text
 , youngs text
);

-- Run as superuser (sortiz)
 copy youngs_import from '/home/sortiz/project/ministry/greek_nt/youngs/youngs.dat' with delimiter as '~' csv quote as '"';

alter table youngs_import add column book_abbr text;


-- Set the book names 
update youngs_import set book_abbr='Gen' where book_num='01';
update youngs_import set book_abbr='Exo' where book_num='02';
update youngs_import set book_abbr='Lev' where book_num='03';
update youngs_import set book_abbr='Num' where book_num='04';
update youngs_import set book_abbr='Deut' where book_num='05';
update youngs_import set book_abbr='Josh' where book_num='06';
update youngs_import set book_abbr='Judg' where book_num='07';
update youngs_import set book_abbr='Ruth' where book_num='08';
update youngs_import set book_abbr='1 Sam' where book_num='09';
update youngs_import set book_abbr='2 Sam' where book_num='10';
update youngs_import set book_abbr='1 Kings' where book_num='11';
update youngs_import set book_abbr='2 Kings' where book_num='12';
update youngs_import set book_abbr='1 Chron' where book_num='13';
update youngs_import set book_abbr='2 Chron' where book_num='14';
update youngs_import set book_abbr='Ezra' where book_num='15';
update youngs_import set book_abbr='Neh' where book_num='16';
update youngs_import set book_abbr='Esth' where book_num='17';
update youngs_import set book_abbr='Job' where book_num='18';
update youngs_import set book_abbr='Psa' where book_num='19';
update youngs_import set book_abbr='Prov' where book_num='20';
update youngs_import set book_abbr='Eccl' where book_num='21';
update youngs_import set book_abbr='SS' where book_num='22';
update youngs_import set book_abbr='Isa' where book_num='23';
update youngs_import set book_abbr='Jer' where book_num='24';
update youngs_import set book_abbr='Lam' where book_num='25';
update youngs_import set book_abbr='Ezek' where book_num='26';
update youngs_import set book_abbr='Dan' where book_num='27';
update youngs_import set book_abbr='Hosea' where book_num='28';
update youngs_import set book_abbr='Joel' where book_num='29';
update youngs_import set book_abbr='Amos' where book_num='30';
update youngs_import set book_abbr='Obad' where book_num='31';
update youngs_import set book_abbr='Jonah' where book_num='32';
update youngs_import set book_abbr='Micah' where book_num='33';
update youngs_import set book_abbr='Nahum' where book_num='34';
update youngs_import set book_abbr='Hab' where book_num='35';
update youngs_import set book_abbr='Zeph' where book_num='36';
update youngs_import set book_abbr='Hag' where book_num='37';
update youngs_import set book_abbr='Zech' where book_num='38';
update youngs_import set book_abbr='Mal' where book_num='39';
update youngs_import set book_abbr='Matt' where book_num='40';
update youngs_import set book_abbr='Mark' where book_num='41';
update youngs_import set book_abbr='Luke' where book_num='42';
update youngs_import set book_abbr='John' where book_num='43';
update youngs_import set book_abbr='Acts' where book_num='44';
update youngs_import set book_abbr='Rom' where book_num='45';
update youngs_import set book_abbr='1 Cor' where book_num='46';
update youngs_import set book_abbr='2 Cor' where book_num='47';
update youngs_import set book_abbr='Gal' where book_num='48';
update youngs_import set book_abbr='Eph' where book_num='49';
update youngs_import set book_abbr='Phil' where book_num='50';
update youngs_import set book_abbr='Col' where book_num='51';
update youngs_import set book_abbr='1 Thes' where book_num='52';
update youngs_import set book_abbr='2 Thes' where book_num='53';
update youngs_import set book_abbr='1 Tim' where book_num='54';
update youngs_import set book_abbr='2 Tim' where book_num='55';
update youngs_import set book_abbr='Titus' where book_num='56';
update youngs_import set book_abbr='Philem' where book_num='57';
update youngs_import set book_abbr='Heb' where book_num='58';
update youngs_import set book_abbr='James' where book_num='59';
update youngs_import set book_abbr='1 Pet' where book_num='60';
update youngs_import set book_abbr='2 Pet' where book_num='61';
update youngs_import set book_abbr='1 John' where book_num='62';
update youngs_import set book_abbr='2 John' where book_num='63';
update youngs_import set book_abbr='3 John' where book_num='64';
update youngs_import set book_abbr='Jude' where book_num='65';
update youngs_import set book_abbr='Rev' where book_num='66';


-- Lookup the verse ids 
alter table youngs_import add column verse_id integer;

update youngs_import y set verse_id=(select id from verse where 
  book=y.book_abbr and lpad(chapter, 3, '0')=y.chapter and lpad(verse_num, 3, '0')=y.verse)
where book_abbr not in ('2 John','3 John','Jude','Obad','Philem');

-- Books with one chapter have the verse/chapter mixed up! (I need to fix that, but it requires updates to the hymn_verse code...)
update youngs_import y set verse_id=(select id from verse where 
  book=y.book_abbr and lpad(chapter, 3, '0')=y.verse)
where book_abbr in ('2 John','3 John','Jude','Obad','Philem');


--- ---------- Validation ------------------
-- Verses that don't exist in Young's
select * from youngs_import where verse_id is null;

-- Verses that are in RcV that aren't in Young's (Rev 12:18, all the titles of the Psalms)
select * from verse where id not in (select verse_id from youngs_import);


--- ----------- Put the data live -------------
alter table verse add column youngs text;
update verse set youngs=(select youngs from youngs_import where verse_id=verse.id);

select * from verse where youngs is null;


drop table youngs_import;
