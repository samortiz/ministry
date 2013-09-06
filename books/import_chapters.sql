--- Set the chapter_id on book_chunk

update book_chunk set chapter_id = (
 select id 
 from book_chapter
 where book_id = book_chunk.book_id
   and book_chapter.page_num <= book_chunk.page_num
 order by page_num desc
 limit 1
) where chapter_id is null;


-- Fix up the chapter names
update book_chapter set chap_title=substring(chap_title, 21+1, length(chap_title)-(21+7-1)) 
  where chap_title like '<span class="normal">%</span>';

update book_chapter set chap_title=substring(chap_title, 0, length(chap_title)-(11))
  where chap_title like '%<br /><br />';

update book_chapter set chap_title=substring(chap_title, 19+1, length(chap_title)-(19+7))
  where chap_title like '<span class="bdit">%</span>';

update book_chapter set chap_title=substring(chap_title, 0, length(chap_title)-7)
  where chap_title like '%<br><br>';

-- Ran this repeatedly until all the <br> are gone
update book_chapter set chap_title=replace(chap_title, '<br />', '') where chap_title like '%<br />%';
update book_chapter set chap_title=replace(chap_title, '<br>', ' ') where chap_title like '%<br>%';

-- whoops, missed a < at the end (one of the lines above must be wrong)
update book_chapter set chap_title=substring(chap_title, 0, length(chap_title)) where chap_title like '%<';


-- Remove tags
update book_chapter set chap_title=replace(chap_title, '<span class="normal">', '') where chap_title like '%<span clas="normal">%';
update book_chapter set chap_title=replace(chap_title, '<span>', '') where chap_title like '%<span>%';
update book_chapter set chap_title=replace(chap_title, '</span>', '') where chap_title like '%</span>%';
update book_chapter set chap_title=replace(chap_title, '<strong>', '') where chap_title like '%<strong>%';
update book_chapter set chap_title=replace(chap_title, '</strong>', '') where chap_title like '%</strong>%';
update book_chapter set chap_title=replace(chap_title, '<em>', '') where chap_title like '%<em>%';
update book_chapter set chap_title=replace(chap_title, '</em>', '') where chap_title like '%</em>%';
update book_chapter set chap_title=replace(chap_title, '<i>', '') where chap_title like '%<i>%';
update book_chapter set chap_title=replace(chap_title, '</i>', '') where chap_title like '%</i>%';
update book_chapter set chap_title=replace(chap_title, '<li>', '') where chap_title like '%<li>%';

update book_chapter set chap_title=replace(chap_title, '<div style="padding-left:25px">', '') where chap_title like '%<div style="padding-left:25px">%';
update book_chapter set chap_title=replace(chap_title, '</div>', '') where chap_title like '%</div>%';

update book_chapter set chap_title=substring(chap_title,0,strpos(chap_title,'<ul class="decimal"'))||substring(chap_title, strpos(chap_title, '">')+2, length(chap_title)) where chap_title like '%<ul class="decimal"%';
update book_chapter set chap_title=replace(chap_title, '</ul>', '') where chap_title like '%</ul>%';

-- Manual
update book_chapter set chap_title = 'A Short Introduction - Raising Up a Unique Gift to the Age' where id=16137;

-- Replace funny characters
update book_chapter set chap_title=replace(chap_title, '&#151;', '-') where chap_title like '%&#151;%';
update book_chapter set chap_title=replace(chap_title, '&#146;', '''') where chap_title like '%&#146;%';
update book_chapter set chap_title=replace(chap_title, '&#147;', '"') where chap_title like '%&#147;%';
update book_chapter set chap_title=replace(chap_title, '&#148;', '"') where chap_title like '%&#148;%';

update book_chapter set chap_title=replace(chap_title, '&rdquo;', '"') where chap_title like '%&rdquo;%';
update book_chapter set chap_title=replace(chap_title, '&ldquo;', '"') where chap_title like '%&ldquo;%';
update book_chapter set chap_title=replace(chap_title, '&rsquo;', '''') where chap_title like '%&rsquo;%';
update book_chapter set chap_title=replace(chap_title, '&mdash;', '-') where chap_title like '%&mdash;%';
update book_chapter set chap_title=replace(chap_title, '&ndash;', '-') where chap_title like '%&ndash;%';
update book_chapter set chap_title=replace(chap_title, '&nbsp;', ' ') where chap_title like '%&nbsp;%';

update book_chapter set chap_title=replace(chap_title, E'\r\n', ' ') where chap_title like E'%\r\n%';
update book_chapter set chap_title=replace(chap_title, E'\t', ' ') where chap_title like E'%\t%';
update book_chapter set chap_title=replace(chap_title, E'—', '-') where chap_title like E'%—%';

-- Whitespace cleanup
update book_chapter set chap_title=trim(chap_title);
update book_chapter set chap_title=replace(chap_title, '  ', ' ') where chap_title like '%  %';
update book_chapter set chap_title=replace(chap_title, '  ', ' ') where chap_title like '%  %';
update book_chapter set chap_title=replace(chap_title, '  ', ' ') where chap_title like '%  %';

-- Cleanup 0 prefixed Chapter numbers
update book_chapter set chap_num=substring(chap_num, 2,length(chap_num)) where chap_num like '0%';
update book_chapter set chap_num=substring(chap_num, 2,length(chap_num)) where chap_num like '0%';


-- Check for funny stuff in the chap_title
select * from book_chapter where chap_title like '%<%>%';
select * from book_chapter where chap_title like '%&#%;%';
select * from book_chapter where chap_title like '%&%;%';
select * from book_chapter where chap_title like '%  %'; 







