drop table book_chunk_attr;
drop table book_chunk;
drop table book;

create table book (
   id serial unique
 , name text
 , display_name text
 , path_name text
);

create table book_chunk (
   id serial unique
 , book_id integer references book(id) on delete cascade on update cascade
 , page_num integer
 , tag_name text
 , tag_class text
 , data text 
);
 
create table book_chunk_attr (
   id serial unique
 , book_chunk_id integer references book_chunk(id) on delete cascade on update cascade
 , name text
 , value text
);

create table book_chapter(
   id serial unique
 , book_id integer references book(id) on delete cascade on update cascade
 , chap_num text
 , chap_title text
 , page_num integer
);

select setval('book_id_seq', 1000);
select setval('book_chunk_id_seq', 1000);
select setval('book_chunk_attr_id_seq', 1000);
create index book_chunk_book_id_idx on book_chunk(book_id);
create index book_chunk_tag_name_idx on book_chunk(tag_name);

-- Hierarchy
alter table book_chunk add column parent_chunk_id integer references book_chunk(id);


-- Indexing for full text search
CREATE INDEX idx_ft_book_chunk_data ON book_chunk USING gin(to_tsvector('english', data));

-- Add a column with the parent title data
alter table book_chunk add column section_title text;
update book_chunk bc1 set section_title=(select bc2.data from book_chunk bc2 where bc2.id=bc1.parent_chunk_id) where parent_chunk_id is not null;
create index idx_ft_book_chunk_title on book_chunk using gin(to_tsvector('english',section_title));

-- More complete search column
alter table book_chunk add column searchtext text;
update book_chunk set searchtext=(coalesce(section_title,'')||' '||data) where tag_name='p';
CREATE INDEX book_chunk_searchtext_ftidx ON book_chunk USING gin(to_tsvector('english', searchtext));

-- Chapter Info
-- notice there is no cascade, I don't want to delete chunks just because someone deleted a chapter...
alter table book_chunk add column chapter_id integer references book_chapter(id);




