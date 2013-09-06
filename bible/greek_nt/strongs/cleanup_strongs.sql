-- Lowercase the greek (to match the NT)
update strongs set lemma=lower(lemma);


-- Add a strongs num to the greek_nt
alter table greek_nt add column strongs_num integer;
update greek_nt set strongs_num=(select num from strongs where lemma=greek_nt.lemma and lemma not in 
   ( 'ei)/kw', 'r(e/w', 'su/neimi', 'ba/tos', 'w)=', 'mh/n', 'a)/peimi'));

-- Some cleanup of misc mismatches
update greek_nt set strongs_num=599 where lemma='a)poqnh/|skw';
update greek_nt set strongs_num=4982 where lemma='sw/|zw';
update greek_nt set strongs_num=1492 where lemma='oi)=da';
update greek_nt set strongs_num=5398 where lemma='fobe/omai';
update greek_nt set strongs_num=1138 where lemma='*daui/d';
update greek_nt set strongs_num=3475 where lemma='*mwu+sh=s';
update greek_nt set strongs_num=3062 where lemma='loipo/s';
update greek_nt set strongs_num=3062 where lemma='*barnaba=s';
update greek_nt set strongs_num=3062 where lemma='*(hrw/|dhs';


