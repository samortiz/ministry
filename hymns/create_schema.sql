-- Create the Schema in postgres

-- Clean the schema
drop table hymn_verse_verse;
drop table hymn_verse;

drop table hymn_line_chord;
drop table hymn_line;
drop table hymn;
drop table verse_note;
drop table verse;


create table hymn (
   hnum integer primary key not null 
 , author text
 , composer text
 , chinese_num text
 , spanish_num text
 , korean_num text
 , tagalog_num text
 , meter text
 , calgary_songbook_num text
);

create table hymn_line (
   id serial primary key not null
 , hnum integer not null references hymn(hnum) on delete cascade on update cascade
 , stanza text 
 , line text
 , data text
 , type text
);

create table hymn_line_chord (
   id serial primary key not null
 , hnum integer not null references hymn(hnum) on delete cascade on update cascade
 , hymn_line_id integer not null references hymn_line(id) on delete cascade on update cascade
 , pos integer
 , chord text
);

create table verse (
   id serial primary key not null
 , book text
 , chapter text
 , verse_num text
 , ref text
 , verse text 
);
create unique index verse_ref on verse(ref);
create index verse_book on verse(book);

create table verse_note (
   id serial primary key not null
 , verse_id integer not null references verse(id) on delete cascade on update cascade
 , num text
 , word text
 , par text
 , note text
 , searchtext text
);
create index verse_note_searchtext_idx on verse_note using gin(to_tsvector('english', searchtext));


create table hymn_verse (
   id serial primary key not null
 , hnum integer not null references hymn(hnum) on delete cascade on update cascade
 , stanza text
 , line text
 , ref text
 , fn text
 , par text
 , key text
 , min_ref text
 , min_quote text
 , completed_by text
 , verified_by text
 , comment text
 , import_date timestamp not null default now()
 , import_batch text
);
create index hymn_verse_hnum on hymn_verse(hnum);
create index hymn_verse_ref on hymn_verse(ref);

create table hymn_verse_verse (
   id serial primary key not null
 , hymn_verse_id integer not null references hymn_verse(id) on delete cascade on update cascade
 , verse_id  integer not null references verse(id) on delete cascade on update cascade
);
create index hymn_verse_verse_hymn_verse_id on hymn_verse_verse(hymn_verse_id);
create index hymn_verse_verse_verse_id on hymn_verse_verse(verse_id);


--- Function to do concatenation ---
CREATE AGGREGATE textcat (
    BASETYPE = text,
    SFUNC = textcat,
    STYPE = text,
    INITCOND = ''
);


