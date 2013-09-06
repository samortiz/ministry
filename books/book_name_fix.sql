-- Parse the chapter and verse from the reference (uses the OLD 3 digit reference)
\qecho "Parsing out the chapter and verse numbers"
update verse set
    chapter = int4(substring(ref from '^[A-Za-z123]{3} ([0-9]{1,3})'))
  , verse_num = substring(ref from '^[A-Za-z123]{3} [0-9]{0,3}[:]{0,1}(([0-9]{1,3})|()|(Title))$')
;

-- Misc Errors --
-- Psa 119 has a footnote on the title, but doesn't actually have a title!  
insert into verse (book, chapter, verse_num, ref, verse) values ('Psa', '119', 'Title', 'Psa 119:Title', '-');


-- Book names --
\qecho "Updating book names"
update verse set book = replace(book, 'Jud', 'Jude') where book = 'Jud'; 
update verse set book = replace(book, 'Jdg', 'Judg') where book = 'Jdg'; 

update verse set book = replace(book, 'Deu', 'Deut') where book = 'Deu'; 
update verse set book = replace(book, 'Jos', 'Josh') where book = 'Jos'; 
update verse set book = replace(book, 'Rut', 'Ruth') where book = 'Rut'; 
update verse set book = replace(book, '1Sa', '1 Sam') where book = '1Sa'; 
update verse set book = replace(book, '2Sa', '2 Sam') where book = '2Sa'; 
update verse set book = replace(book, '1Ki', '1 Kings') where book = '1Ki'; 
update verse set book = replace(book, '2Ki', '2 Kings') where book = '2Ki'; 
update verse set book = replace(book, '1Ch', '1 Chron') where book = '1Ch'; 
update verse set book = replace(book, '2Ch', '2 Chron') where book = '2Ch'; 
update verse set book = replace(book, 'Ezr', 'Ezra') where book = 'Ezr'; 
update verse set book = replace(book, 'Est', 'Esth') where book = 'Est'; 
update verse set book = replace(book, 'Prv', 'Prov') where book = 'Prv'; 
update verse set book = replace(book, 'Ecc', 'Eccl') where book = 'Ecc'; 
update verse set book = replace(book, 'SoS', 'SS') where book = 'SoS'; 
update verse set book = replace(book, 'Ezk', 'Ezek') where book = 'Ezk'; 
update verse set book = replace(book, 'Hos', 'Hosea') where book = 'Hos'; 
update verse set book = replace(book, 'Joe', 'Joel') where book = 'Joe'; 
update verse set book = replace(book, 'Amo', 'Amos') where book = 'Amo'; 
update verse set book = replace(book, 'Oba', 'Obad') where book = 'Oba'; 
update verse set book = replace(book, 'Jon', 'Jonah') where book = 'Jon'; 
update verse set book = replace(book, 'Mic', 'Micah') where book = 'Mic'; 
update verse set book = replace(book, 'Nah', 'Nahum') where book = 'Nah'; 
update verse set book = replace(book, 'Zep', 'Zeph') where book = 'Zep'; 
update verse set book = replace(book, 'Zec', 'Zech') where book = 'Zec'; 
update verse set book = replace(book, 'Mal', 'Mal') where book = 'Mal'; 
update verse set book = replace(book, 'Mat', 'Matt') where book = 'Mat'; 
update verse set book = replace(book, 'Mrk', 'Mark') where book = 'Mrk'; 
update verse set book = replace(book, 'Luk', 'Luke') where book = 'Luk'; 
update verse set book = replace(book, 'Joh', 'John') where book = 'Joh'; 
update verse set book = replace(book, 'Act', 'Acts') where book = 'Act'; 
update verse set book = replace(book, '1Co', '1 Cor') where book = '1Co'; 
update verse set book = replace(book, '2Co', '2 Cor') where book = '2Co'; 
update verse set book = replace(book, 'Phi', 'Phil') where book = 'Phi'; 
update verse set book = replace(book, '1Th', '1 Thes') where book = '1Th'; 
update verse set book = replace(book, '2Th', '2 Thes') where book = '2Th'; 
update verse set book = replace(book, '1Ti', '1 Tim') where book = '1Ti'; 
update verse set book = replace(book, '2Ti', '2 Tim') where book = '2Ti'; 
update verse set book = replace(book, 'Tit', 'Titus') where book = 'Tit'; 
update verse set book = replace(book, 'Phm', 'Philem') where book = 'Phm'; 
update verse set book = replace(book, 'Jam', 'James') where book = 'Jam'; 
update verse set book = replace(book, '1Pe', '1 Pet') where book = '1Pe'; 
update verse set book = replace(book, '2Pe', '2 Pet') where book = '2Pe'; 
update verse set book = replace(book, '1Jo', '1 John') where book = '1Jo'; 
update verse set book = replace(book, '2Jo', '2 John') where book = '2Jo'; 
update verse set book = replace(book, '3Jo', '3 John') where book = '3Jo'; 

-- References --
\qecho "Updating book names in references"
update verse set ref = replace(ref, 'Jud', 'Jude') where ref like 'Jud %';
update verse set ref = replace(ref, 'Jdg', 'Judg') where ref like 'Jdg %';
update verse set ref = replace(ref, 'Tit', 'Titus') where ref like 'Tit %';

update verse set ref = replace(ref, 'Deu', 'Deut') where ref like 'Deu %';
update verse set ref = replace(ref, 'Jos', 'Josh') where ref like 'Jos %';
update verse set ref = replace(ref, 'Rut', 'Ruth') where ref like 'Rut %';
update verse set ref = replace(ref, '1Sa', '1 Sam') where ref like '1Sa %';
update verse set ref = replace(ref, '2Sa', '2 Sam') where ref like '2Sa %';
update verse set ref = replace(ref, '1Ki', '1 Kings') where ref like '1Ki %';
update verse set ref = replace(ref, '2Ki', '2 Kings') where ref like '2Ki %';
update verse set ref = replace(ref, '1Ch', '1 Chron') where ref like '1Ch %';
update verse set ref = replace(ref, '2Ch', '2 Chron') where ref like '2Ch %';
update verse set ref = replace(ref, 'Ezr', 'Ezra') where ref like 'Ezr %';
update verse set ref = replace(ref, 'Est', 'Esth') where ref like 'Est %';
update verse set ref = replace(ref, 'Prv', 'Prov') where ref like 'Prv %';
update verse set ref = replace(ref, 'Ecc', 'Eccl') where ref like 'Ecc %';
update verse set ref = replace(ref, 'SoS', 'SS') where ref like 'SoS %';
update verse set ref = replace(ref, 'Ezk', 'Ezek') where ref like 'Ezk %';
update verse set ref = replace(ref, 'Hos', 'Hosea') where ref like 'Hos %';
update verse set ref = replace(ref, 'Joe', 'Joel') where ref like 'Joe %';
update verse set ref = replace(ref, 'Amo', 'Amos') where ref like 'Amo %';
update verse set ref = replace(ref, 'Oba', 'Obad') where ref like 'Oba %';
update verse set ref = replace(ref, 'Jon', 'Jonah') where ref like 'Jon %';
update verse set ref = replace(ref, 'Mic', 'Micah') where ref like 'Mic %';
update verse set ref = replace(ref, 'Nah', 'Nahum') where ref like 'Nah %';
update verse set ref = replace(ref, 'Zep', 'Zeph') where ref like 'Zep %';
update verse set ref = replace(ref, 'Zec', 'Zech') where ref like 'Zec %';
update verse set ref = replace(ref, 'Mal', 'Mal') where ref like 'Mal %';
update verse set ref = replace(ref, 'Mat', 'Matt') where ref like 'Mat %';
update verse set ref = replace(ref, 'Mrk', 'Mark') where ref like 'Mrk %';
update verse set ref = replace(ref, 'Luk', 'Luke') where ref like 'Luk %';
update verse set ref = replace(ref, 'Joh', 'John') where ref like 'Joh %';
update verse set ref = replace(ref, 'Act', 'Acts') where ref like 'Act %';
update verse set ref = replace(ref, '1Co', '1 Cor') where ref like '1Co %';
update verse set ref = replace(ref, '2Co', '2 Cor') where ref like '2Co %';
update verse set ref = replace(ref, 'Phi', 'Phil') where ref like 'Phi %';
update verse set ref = replace(ref, '1Th', '1 Thes') where ref like '1Th %';
update verse set ref = replace(ref, '2Th', '2 Thes') where ref like '2Th %';
update verse set ref = replace(ref, '1Ti', '1 Tim') where ref like '1Ti %';
update verse set ref = replace(ref, '2Ti', '2 Tim') where ref like '2Ti %';
update verse set ref = replace(ref, 'Phm', 'Philem') where ref like 'Phm %';
update verse set ref = replace(ref, 'Jam', 'James') where ref like 'Jam %';
update verse set ref = replace(ref, '1Pe', '1 Pet') where ref like '1Pe %';
update verse set ref = replace(ref, '2Pe', '2 Pet') where ref like '2Pe %';
update verse set ref = replace(ref, '1Jo', '1 John') where ref like '1Jo %';
update verse set ref = replace(ref, '2Jo', '2 John') where ref like '2Jo %';
update verse set ref = replace(ref, '3Jo', '3 John') where ref like '3Jo %';
