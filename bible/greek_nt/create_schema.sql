------------------------------------
-- ----- Vines Schema
------------------------------------
create table vines(
   id serial unique
 , vines_num integer
 , word text
);

create table vines_def(
   id serial unique
 , vines_id integer references vines(id) on delete cascade on update cascade
 , vines_num integer
 , code text
 , word_type text
 , strongs_num text
 , greek text
 , definition text
);


-------------------------------------
-- ----- Green NT Schema
-------------------------------------

create table lookup(
   id serial unique
 , group_type text
 , code text
 , name text
 , short_name text
 , sorder real 
);

insert into lookup(id, group_type, code, name, short_name) values (101, 'part_of_speech', 'r', 'r', 'r');
insert into lookup(id, group_type, code, name, short_name) values (102, 'part_of_speech', 'n', 'Noun', 'Noun');
insert into lookup(id, group_type, code, name, short_name) values (103, 'part_of_speech', 'v', 'Verb', 'Verb');
insert into lookup(id, group_type, code, name, short_name) values (104, 'part_of_speech', 'c', 'c', 'c');
insert into lookup(id, group_type, code, name, short_name) values (105, 'part_of_speech', 'p', 'Pronoun', 'Pronoun');
insert into lookup(id, group_type, code, name, short_name) values (106, 'part_of_speech', 'a', 'a', 'a');
insert into lookup(id, group_type, code, name, short_name) values (107, 'part_of_speech', 'd', 'd', 'd');
insert into lookup(id, group_type, code, name, short_name) values (108, 'part_of_speech', 'x', 'x', 'x');
insert into lookup(id, group_type, code, name, short_name) values (109, 'part_of_speech', 'i', 'i', 'i');

N- = Noun
A- = Adjective
R- = Relative pronoun
C- = reCiprocal pronoun
D- = Demonstrative pronoun
T- = definite article
K- = correlative pronoun
I- = Interrogative pronoun
X- = indefinite pronoun
Q- = correlative or interrogative pronoun
F- = reFlexive pronoun (person 1,2,3 added)
S- = poSsessive pronoun (person 1,2,3 added)
P- = Personal pronoun (person 1,2,3 added) > (Note: 1st and 2nd personal pronouns have no gender)



insert into lookup(id, group_type, code, name, short_name) values (201, 'tense', 'a', 'Aorist', 'Aor');
insert into lookup(id, group_type, code, name, short_name) values (202, 'tense', 'p', 'Present', 'Pres');
insert into lookup(id, group_type, code, name, short_name) values (203, 'tense', 'i', 'Imperfect', 'Imp');
insert into lookup(id, group_type, code, name, short_name) values (204, 'tense', 'f', 'Future', 'Fut');
insert into lookup(id, group_type, code, name, short_name) values (205, 'tense', 'x', 'Perfect', 'Per');
insert into lookup(id, group_type, code, name, short_name) values (206, 'tense', 'y', 'Pluperfect', 'Plu');

insert into lookup(id, group_type, code, name, short_name) values (300, 'voice', 'a', 'Active', 'Act');
insert into lookup(id, group_type, code, name, short_name) values (301, 'voice', 'm', 'Middle', 'Mid');
insert into lookup(id, group_type, code, name, short_name) values (302, 'voice', 'p', 'Passive', 'Pas');

insert into lookup(id, group_type, code, name, short_name) values (401, 'mood', 'i', 'Indicative', 'Ind');
insert into lookup(id, group_type, code, name, short_name) values (402, 'mood', 'p', 'Participle', 'Part');
insert into lookup(id, group_type, code, name, short_name) values (403, 'mood', 'n', 'Infinitive', 'Inf');
insert into lookup(id, group_type, code, name, short_name) values (404, 'mood', 's', 'Subjunctive', 'Subj');
insert into lookup(id, group_type, code, name, short_name) values (405, 'mood', 'd', 'Imperative', 'Imp');
insert into lookup(id, group_type, code, name, short_name) values (406, 'mood', 'o', 'Optative', 'Opt');

insert into lookup(id, group_type, code, name, short_name) values (501, 'person', '3', 'Third',  '3');
insert into lookup(id, group_type, code, name, short_name) values (502, 'person', '2', 'Second', '2');
insert into lookup(id, group_type, code, name, short_name) values (503, 'person', '1', 'First',  '1');

insert into lookup(id, group_type, code, name, short_name) values (601, 'number', 's', 'Singular', 'Sing');
insert into lookup(id, group_type, code, name, short_name) values (602, 'number', 'p', 'Plural', 'Pl');

insert into lookup(id, group_type, code, name, short_name) values (701, 'gender', 'm', 'Masculine', 'Masc');
insert into lookup(id, group_type, code, name, short_name) values (702, 'gender', 'f', 'Feminine', 'Fem');
insert into lookup(id, group_type, code, name, short_name) values (703, 'gender', 'n', 'Neuter', 'Neut');

insert into lookup(id, group_type, code, name, short_name) values (801, 'case', 'n', 'Nominative', 'Nom');
insert into lookup(id, group_type, code, name, short_name) values (802, 'case', 'a', 'Accusative', 'Acc');
insert into lookup(id, group_type, code, name, short_name) values (803, 'case', 'g', 'Genitive', 'Gen');
insert into lookup(id, group_type, code, name, short_name) values (804, 'case', 'd', 'Dative', 'Dat');
insert into lookup(id, group_type, code, name, short_name) values (805, 'case', 'v', 'Vocative', 'Voc');

update lookup set sorder=id;


create table greek_nt(
   id serial unique
 , verse_id integer references verse(id)
 , greek text
 , lemma text
 , part_of_speech_id integer references lookup(id)
 , tense_id  integer references lookup(id)
 , voice_id  integer references lookup(id)
 , mood_id   integer references lookup(id)
 , person_id integer references lookup(id)
 , number_id integer references lookup(id)
 , gender_id integer references lookup(id)
 , case_id   integer references lookup(id)
);

-- Temp import table
create table greek_nt_import(
   id serial unique
 , book_num text
 , chap_num text
 , verse_num text
 , word_type text
 , parse text
 , word text
 , lemma text
);

-- View to help with seeing the greek NT data
create or replace view greek_nt_view as 
select 
   gnt.id as greek_nt_id
  ,gnt.verse_id as verse_id
  ,v.ref as ref
  ,gnt.greek as greek
  ,gnt.lemma as lemma
  ,(select name from lookup where id=gnt.part_of_speech_id) as pos
  ,(select name from lookup where id=gnt.tense_id) as tense
  ,(select name from lookup where id=gnt.voice_id) as voice
  ,(select name from lookup where id=gnt.mood_id) as mood
  ,(select short_name from lookup where id=gnt.person_id) as person
  ,(select name from lookup where id=gnt.number_id) as number
  ,(select short_name from lookup where id=gnt.gender_id) as gender
  ,(select short_name from lookup where id=gnt.case_id) as "case"
from 
   greek_nt gnt
 , verse v 
where
 gnt.verse_id = v.id
;



--- -----------------------------------------
-- --- Strongs Schema
-- ------------------------------------------
create table strongs(
   num integer primary key unique not null
 , lemma text
 , unicode text
 , translit text
 , pronunciation text
 , derivation text
 , def text
 , kjv_def text
 , entry text
);

create table strongs_see(
   id serial unique
 , strongs_num integer references strongs(num) on delete cascade on update cascade
 , see_strongs_num integer 
 , see_strongs_language text 
);



