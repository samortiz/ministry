-- Import young's literal translation into the database
create table import (
   book_num text
 , book text
 , chapter text
 , verse text
 , kjv text
);

-- Run as superuser (sortiz)
copy import from '/home/sortiz/project/ministry/translations/kjv.dat' with delimiter as '~' csv quote as '"';

alter table import add column book_abbr text;


-- Set the book names 
update import set book_abbr='Gen' where book_num='01';
update import set book_abbr='Exo' where book_num='02';
update import set book_abbr='Lev' where book_num='03';
update import set book_abbr='Num' where book_num='04';
update import set book_abbr='Deut' where book_num='05';
update import set book_abbr='Josh' where book_num='06';
update import set book_abbr='Judg' where book_num='07';
update import set book_abbr='Ruth' where book_num='08';
update import set book_abbr='1 Sam' where book_num='09';
update import set book_abbr='2 Sam' where book_num='10';
update import set book_abbr='1 Kings' where book_num='11';
update import set book_abbr='2 Kings' where book_num='12';
update import set book_abbr='1 Chron' where book_num='13';
update import set book_abbr='2 Chron' where book_num='14';
update import set book_abbr='Ezra' where book_num='15';
update import set book_abbr='Neh' where book_num='16';
update import set book_abbr='Esth' where book_num='17';
update import set book_abbr='Job' where book_num='18';
update import set book_abbr='Psa' where book_num='19';
update import set book_abbr='Prov' where book_num='20';
update import set book_abbr='Eccl' where book_num='21';
update import set book_abbr='SS' where book_num='22';
update import set book_abbr='Isa' where book_num='23';
update import set book_abbr='Jer' where book_num='24';
update import set book_abbr='Lam' where book_num='25';
update import set book_abbr='Ezek' where book_num='26';
update import set book_abbr='Dan' where book_num='27';
update import set book_abbr='Hosea' where book_num='28';
update import set book_abbr='Joel' where book_num='29';
update import set book_abbr='Amos' where book_num='30';
update import set book_abbr='Obad' where book_num='31';
update import set book_abbr='Jonah' where book_num='32';
update import set book_abbr='Micah' where book_num='33';
update import set book_abbr='Nahum' where book_num='34';
update import set book_abbr='Hab' where book_num='35';
update import set book_abbr='Zeph' where book_num='36';
update import set book_abbr='Hag' where book_num='37';
update import set book_abbr='Zech' where book_num='38';
update import set book_abbr='Mal' where book_num='39';
update import set book_abbr='Matt' where book_num='40';
update import set book_abbr='Mark' where book_num='41';
update import set book_abbr='Luke' where book_num='42';
update import set book_abbr='John' where book_num='43';
update import set book_abbr='Acts' where book_num='44';
update import set book_abbr='Rom' where book_num='45';
update import set book_abbr='1 Cor' where book_num='46';
update import set book_abbr='2 Cor' where book_num='47';
update import set book_abbr='Gal' where book_num='48';
update import set book_abbr='Eph' where book_num='49';
update import set book_abbr='Phil' where book_num='50';
update import set book_abbr='Col' where book_num='51';
update import set book_abbr='1 Thes' where book_num='52';
update import set book_abbr='2 Thes' where book_num='53';
update import set book_abbr='1 Tim' where book_num='54';
update import set book_abbr='2 Tim' where book_num='55';
update import set book_abbr='Titus' where book_num='56';
update import set book_abbr='Philem' where book_num='57';
update import set book_abbr='Heb' where book_num='58';
update import set book_abbr='James' where book_num='59';
update import set book_abbr='1 Pet' where book_num='60';
update import set book_abbr='2 Pet' where book_num='61';
update import set book_abbr='1 John' where book_num='62';
update import set book_abbr='2 John' where book_num='63';
update import set book_abbr='3 John' where book_num='64';
update import set book_abbr='Jude' where book_num='65';
update import set book_abbr='Rev' where book_num='66';


-- Lookup the verse ids 
alter table import add column verse_id integer;

-- Set the verse ids for the standard books (multiple chapters)
update import y set verse_id=(select id from verse where 
  book=y.book_abbr and lpad(chapter, 3, '0')=y.chapter and lpad(verse_num, 3, '0')=y.verse)
where book_abbr not in ('2 John','3 John','Jude','Obad','Philem');

-- Books with one chapter have the verse/chapter mixed up! (I need to fix that, but it requires updates to the hymn_verse code...)
update import y set verse_id=(select id from verse where 
  book=y.book_abbr and lpad(chapter, 3, '0')=y.verse)
where book_abbr in ('2 John','3 John','Jude','Obad','Philem');


--- ---------- Validation ------------------
-- Verses that don't exist in Young's
select * from import where verse_id is null;

-- Verses that are in RcV that aren't in Young's (Rev 12:18, all the titles of the Psalms)
select * from verse where id not in (select verse_id from import);


--- ----------- Put the data live -------------
alter table verse add column kjv text;
update verse set kjv=(select kjv from import where verse_id=verse.id);


-- Cleanup 
drop table import;



