alter table verse_note add column searchtext text;
create index verse_note_searchtext_idx on verse_note using gin(to_tsvector('english', searchtext));

-- Set the search text
update verse_note set searchtext=(select ref||' '||verse from verse where id=verse_note.verse_id)||' '||word||' '||note; 

