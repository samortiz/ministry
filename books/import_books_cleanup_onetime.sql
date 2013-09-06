-- SQL Run after importing

update book_chunk set data = substring(data, 11, length(data)-20) where data like '<br> <br> % <br> <br>';
delete from book_chunk where tag_name='' and data='<br> <br>';
delete from book_chunk where tag_name='' and data = '</span></a>';
delete from book_chunk where data='<br>';
delete from book_chunk where tag_name='' and data like '</%';
update book_chunk set tag_name='p', data=substring(data, 13, length(data)-25) where tag_name='' and data like '<blockquote>%</blockquote>';
delete from book_chunk where tag_name='' and data like '<script%';
update book_chunk set data=substring(data, 22, length(data)-28), tag_class='normal', tag_name='div' where data like '<span class=''normal''>%</span>' and tag_name='';
update book_chunk set data=substring(data, 22, length(data)-28), tag_class='normal' where data like '<span class=''normal''>%</span>';
update book_chunk set data='The Tabernacle of God', tag_name='h2', tag_class='head3' where data='<ph2 class=''head3''>The Tabernacle of God';
delete from book_chunk where data='< @6>';
update book_chunk set tag_name='p' where tag_name='' and data like '<b>%';
update book_chunk set data=substring(data, 13, length(data)) where tag_name='' and data like '<blockquote>%';
update book_chunk set data=substring(data, 0, length(data)-12) where tag_name='' and data like '%<blockquote>';
delete from book_chunk where data='] < @>';
delete from book_chunk where tag_name='' and data like '<link %';
delete from book_chunk where data like '<html>%';
update book_chunk set tag_name='p' where tag_name='';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';
update book_chunk set data=substring(data, 0, length(data)-4) where data like '% <br>';
update book_chunk set data='Lord, I consecrate the following completely to You:' where data like '% <br> <br>';
delete from book_chunk where tag_name='table';


-- Dirty mess, someone missed a quote (we can't insert a node either because it's all ordered by id)
select * from book_chunk where tag_class like 'head1>%';
update book_chunk set data='XI. BY LIVING IN THE ORGANISM OF THE DIVINE TRINITY AND PARTICIPATING IN THE DISPENSING OF THE DIVINE TRINITY', tag_class='head1' where id=388960;
update book_chunk set data='in this lesson we will see that the believers experience and enjoy the dispensing of the divine trinity in the divine transformation for the divine conformation by living in the organism of the divine trinity and participating in the dispensing of the divine trinity.<br>The Lord''s word in John 14 through 16 is deep and mysterious because the Lord wanted to bring the disciples into the depths of the unfathomable divine mysteries. These mysteries include the Father''s house with its many abodes, the vine tree, and the newborn child.' where id=388961;

-- Cleanup the h1/h2 tags
update book_chunk set tag_name='p' where tag_name='div';
update book_chunk set tag_name='h2' where tag_name='h1' and tag_class in ('head1', 'head3');
update book_chunk set tag_class='scripture' where tag_class='scritpure';
update book_chunk set tag_class='title' where tag_name='h1' and tag_class='';
update book_chunk set tag_class='head4' where tag_name='h2' and tag_class='head4f';
update book_chunk set tag_class='head4' where tag_name='h2' and tag_class='head4p';
update book_chunk set tag_class='head1' where tag_name='h2' and tag_class='uhead1';
update book_chunk set tag_class='head3' where tag_name='h2' and tag_class='head3u';
update book_chunk set tag_class='head5' where tag_name='h2' and tag_class='head5f';
update book_chunk set tag_class='head3' where tag_name='h2' and tag_class='head3f';
update book_chunk set tag_name='h1' where tag_name='h2' and tag_class='series';
 

-- Hierarchy
alter table book_chunk add column parent_chunk_id integer references book_chunk(id);

-- Set all the leaf notes to their parent
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name in ('h1','h2') and id<c.id order by id desc limit 1) where c.tag_name not in ('h1', 'h2');

-- Update the header nodes
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head6' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head7';
select now();
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head5' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head6';
select now();
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head4' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head5';
select now();
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head3' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head4';
select now();
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head2' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head3';
select now();
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id=c.book_id and tag_name='h2' and tag_class='head1' and id<c.id order by id desc limit 1) where c.tag_name='h2' and c.tag_class='head2';
select now();

-- More cleanup!
update book_chunk set tag_name='h1', tag_class='msg' where tag_name='h2' and tag_class='head4' and parent_chunk_id is null and data like 'Issue No.%';
update book_chunk set tag_name='h1', tag_class='msg' where tag_name='h2' and tag_class='head4' and parent_chunk_id is null and data like '(%Issue No%';

update book_chunk set tag_name='p', tag_class='' where tag_name='h2' and parent_chunk_id is null and data like '(%';
update book_chunk set tag_class='head1' where book_id=1319 and tag_name='h2';

-- In the conclusion messages the outline spans books
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id >= 1144 and book_id <= 1168 and tag_name='h2' and tag_class='head1' and id<c.id order by id desc limit 1) where book_id >= 1144 and book_id <= 1168 and parent_chunk_id is null and c.tag_name='h2' and c.tag_class='head2';
update book_chunk c set parent_chunk_id=(select id from book_chunk where book_id >= 1144 and book_id <= 1168 and tag_name='h2' and tag_class='head2' and id<c.id order by id desc limit 1) where book_id >= 1144 and book_id <= 1168 and parent_chunk_id is null and c.tag_name='h2' and c.tag_class='head3';

-- Mystery of Human life 
update book_chunk set tag_class='head1' where tag_name='h2' and tag_class='head2' and book_id=1463;




-- Queries 
select tag_name, tag_class, count(*) from book_chunk group by tag_name, tag_class order by tag_name, count(*) desc;




