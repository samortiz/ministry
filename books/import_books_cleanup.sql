-- SQL to run after importing

update book_chunk set data = substring(data, 11, length(data)-20) where data like '<br> <br> % <br> <br>';
delete from book_chunk where data='<br> <br>';
delete from book_chunk where data = '</span></a>';
delete from book_chunk where data='<br>';
delete from book_chunk where tag_name='' and data like '</%>';
update book_chunk set tag_name='p', data=substring(data, 13, length(data)-25) where tag_name='' and data like '<blockquote>%</blockquote>';
delete from book_chunk where tag_name='' and data like '<script%';
update book_chunk set data=substring(data, 22, length(data)-28), tag_class='normal', tag_name='div' where data like '<span class=''normal''>%</span>' and tag_name='';
update book_chunk set data=substring(data, 22, length(data)-28), tag_class='normal' where data like '<span class=''normal''>%</span>';
update book_chunk set tag_name='p' where tag_name='' and data like '<b>%';
update book_chunk set data=substring(data, 13, length(data)) where tag_name='' and data like '<blockquote>%';
update book_chunk set data=substring(data, 0, length(data)-12) where tag_name='' and data like '%<blockquote>';
delete from book_chunk where tag_name='' and data like '<link %';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';

-- How did these things get through anyway?
update book_chunk set data=replace(data, '“', '"') where data like '%“%';
update book_chunk set data=replace(data, '”', '"') where data like '%”%';
update book_chunk set data=replace(data, '’', '''') where data like '%’%';

-- Cleanup the h1/h2 tags
update book_chunk set tag_name='p' where tag_name='div';
update book_chunk set tag_name='h2' where tag_name='h1' and tag_class in ('head1','head2','head3');

-- Hierarchy
-- Set all the leaf notes to their parent
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name in ('h1','h2') and id<c.id order by id desc limit 1) where c.tag_name not in ('h1', 'h2') and parent_chunk_id is null;

-- Update the header nodes
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head6' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head7' and parent_chunk_id is null;
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head5' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head6' and parent_chunk_id is null;
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head4' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head5' and parent_chunk_id is null;
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head3' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head4' and parent_chunk_id is null;
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head2' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head3' and parent_chunk_id is null;
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head1' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head2' and parent_chunk_id is null;

-- More cleanup!
update book_chunk set tag_name='h1', tag_class='msg' where tag_name='h2' and tag_class='head4' and parent_chunk_id is null and data like 'Issue No.%';
update book_chunk set tag_name='h1', tag_class='msg' where tag_name='h2' and tag_class='head4' and parent_chunk_id is null and data like '(%Issue No%';
update book_chunk set tag_name='p', tag_class='' where tag_name='h2' and parent_chunk_id is null and data like '(%';


-- Check for missing parents on paragraphs
select * from book_chunk where tag_name='p' and parent_chunk_id is null;

-- Update the fulltext indexes
update book_chunk bc1 set section_title=(select bc2.data from book_chunk bc2 where bc2.id=bc1.parent_chunk_id) where parent_chunk_id is not null and section_title is null;
update book_chunk set searchtext=(coalesce(section_title,'')||' '||data) where tag_name='p' and searchtext is null;



-- Some Checkup Queries 

select tag_name, tag_class, count(*) from book_chunk group by tag_name, tag_class order by tag_name, count(*) desc;

select tag_name, tag_class, count(*) from book_chunk where parent_chunk_id is null group by tag_name, tag_class order by tag_name, count(*) desc;


