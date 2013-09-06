#!/usr/bin/env python
import os, shutil, pg, cgi, re
from db_functions import *
from verse_functions import *
from www_functions import *

PAGESIZE = 100

print "Content-type: text/html\n"

# ------------------------- Functions -----------------------

def genUrl(book, chapter, verse_num, note_num=""):
  "Create a URL into the HTML Bible"
  bookUrl = ""
  if book == "Gen": bookUrl="Gen"
  if book == "Exo": bookUrl="Exo"
  if book == "Lev": bookUrl="Lev"
  if book == "Num": bookUrl="Num"
  if book == "Deut": bookUrl="Deu"
  if book == "Josh": bookUrl="Jos"
  if book == "Judg": bookUrl="Jdg"
  if book == "Ruth": bookUrl="Rut"
  if book == "1 Sam": bookUrl="1Sa"
  if book == "2 Sam": bookUrl="2Sa"
  if book == "1 Kings": bookUrl="1Ki"
  if book == "2 Kings": bookUrl="2Ki"
  if book == "1 Chron": bookUrl="1Ch"
  if book == "2 Chron": bookUrl="2Ch"
  if book == "Ezra": bookUrl="Ezr"
  if book == "Neh": bookUrl="Neh"
  if book == "Esth": bookUrl="Est"
  if book == "Job": bookUrl="Job"
  if book == "Psa": bookUrl="Psa"
  if book == "Prov": bookUrl="Prv"
  if book == "Eccl": bookUrl="Ecc"
  if book == "SS": bookUrl="SoS"
  if book == "Isa": bookUrl="Isa"
  if book == "Jer": bookUrl="Jer"
  if book == "Lam": bookUrl="Lam"
  if book == "Ezek": bookUrl="Ezk"
  if book == "Dan": bookUrl="Dan"
  if book == "Hosea": bookUrl="Hos"
  if book == "Joel": bookUrl="Joe"
  if book == "Amos": bookUrl="Amo"
  if book == "Obad": bookUrl="Oba"
  if book == "Jonah": bookUrl="Jon"
  if book == "Micah": bookUrl="Mic"
  if book == "Nahum": bookUrl="Nah"
  if book == "Hab": bookUrl="Hab"
  if book == "Zeph": bookUrl="Zep"
  if book == "Hag": bookUrl="Hag"
  if book == "Zech": bookUrl="Zec"
  if book == "Mal": bookUrl="Mal"
  if book == "Matt": bookUrl="Mat"
  if book == "Mark": bookUrl="Mrk"
  if book == "Luke": bookUrl="Luk"
  if book == "John": bookUrl="Joh"
  if book == "Acts": bookUrl="Act"
  if book == "Rom": bookUrl="Rom"
  if book == "1 Cor": bookUrl="1Co"
  if book == "2 Cor": bookUrl="2Co"
  if book == "Gal": bookUrl="Gal"
  if book == "Eph": bookUrl="Eph"
  if book == "Phil": bookUrl="Phi"
  if book == "Col": bookUrl="Col"
  if book == "1 Thes": bookUrl="1Th"
  if book == "2 Thes": bookUrl="2Th"
  if book == "1 Tim": bookUrl="1Ti"
  if book == "2 Tim": bookUrl="2Ti"
  if book == "Titus": bookUrl="Tit"
  if book == "Philem": bookUrl="Phm"
  if book == "Heb": bookUrl="Heb"
  if book == "James": bookUrl="Jam"
  if book == "1 Pet": bookUrl="1Pe"
  if book == "2 Pet": bookUrl="2Pe"
  if book == "1 John": bookUrl="1Jo"
  if book == "2 John": bookUrl="2Jo"
  if book == "3 John": bookUrl="3Jo"
  if book == "Jude": bookUrl="Jud"
  if book == "Rev": bookUrl="Rev"
  
  # Assemble the URL
  url = bookUrl
  if note_num != "": 
    url += "N.htm#n"  
  else:
    url += ".htm#v"

  if book in ("2 John", "3 John", "Jude", "Obad", "Phil"):
    url += verse_num
  else:
    url += chapter+"_"+verse_num

  if note_num != "": 
    url += "x"+note_num
   
  return url


# --------------------- Begin Main Program -----------------------------

#Get the parameters
debug = getParam("debug")
search_text = getParam("search_text")
pageStr = getParam("page")
page = 0
if pageStr:
  page = int (pageStr)

html  = "<form name='theform' method='post' action='search_bible.py'>"
html += "Search the Bible for "
html += "<input type='text' name='search_text' value='"+search_text.replace("'", "&#39;")+"'>"
html += "<input type='submit' name='submit' value='Search'>"
html += "<input type='hidden' name='debug' value='"+debug+"'>"
html += "</form>"


if (search_text != ""):

 # ------------------------- Search Verses -----------------
  sql = """
select v.id
     , v.ref
     , v.book
     , v.chapter
     , v.verse_num
     , v.verse
     , ts_rank(to_tsvector(v.verse), query, 0) AS rank
     , ts_headline(v.verse, query, 
         'HighlightAll=false, MaxWords=1000, MinWords=100 '
        ) as text_highlight
from  verse v
    , plainto_tsquery('"""+escape(search_text)+"""') as query
where to_tsvector('english', v.verse) @@ query
order by rank desc, v.id
"""
  verseResults = dbQuery(sql)
  if len(verseResults) > 0 :
    html += "<b>Verses</b> :"
  for verseResult in verseResults:
    verse_id = str(verseResult[0])
    ref = verseResult[1]
    book = verseResult[2]
    chapter = verseResult[3]
    verse_num = verseResult[4]
    verse = verseResult[5]
    rank = str(verseResult[6])
    highlight = verseResult[7]

    url = genUrl(book, chapter, verse_num)

    html += "<div style='padding:3px'>"
    html += "<a href='/bible/"+url+"'>"+ref+"</a>"
    html += " "+highlight
    if (debug): html += " ("+verse_id+" "+rank+")"
    html += "</div>"


  # --------------- Search the Footnotes ---------------------------

  sql = """
select vn.id
     , v.ref
     , v.book
     , v.chapter
     , v.verse_num
     , vn.num
     , vn.par
     , vn.word
     , ts_rank( /*      note  verse  word */
            array[0.1,  0.4,  0.4,   0.8 ]
          , setweight(to_tsvector(coalesce(vn.note, '')),'C')
         || setweight(to_tsvector(coalesce(v.verse, '')),'B')
         || setweight(to_tsvector(coalesce(vn.word, '')),'A')
         ,  query, 0) AS rank
    , ts_headline(vn.note, query, 
         'HighlightAll=false, MaxWords=5000, MinWords=1000'
        ) as highlight
from  verse v
    , verse_note vn
    , plainto_tsquery('"""+escape(search_text)+"""') as query
where to_tsvector('english', vn.searchtext) @@ query
  and vn.verse_id = v.id
order by rank desc, v.id
"""
  noteResults = dbQuery(sql)
  if len(noteResults) > 0 :
    html += "<hr><b>Footnotes</b> :"
  for noteResult in noteResults:
    note_id = str(noteResult[0])
    ref = noteResult[1]
    book = noteResult[2]
    chapter = noteResult[3]
    verse_num = noteResult[4]
    note_num = noteResult[5]
    note_paragraph = noteResult[6]
    note_word = noteResult[7]
    rank = str(noteResult[8])
    highlight = noteResult[9]

    verseUrl = genUrl(book, chapter, verse_num)
    noteUrl = genUrl(book, chapter, verse_num, note_num)

    html += "<div style='padding:3px'>"
    html += "<a href='/bible/"+verseUrl+"'>"+ref+"</a>"
    html += "<a href='/bible/"+noteUrl+"'>"
    html += "<sup>"+note_num+"</sup>"
    if note_paragraph != "":
      html += " par "+note_paragraph
    html += " <b>"+note_word+"</b></a>"
    html += " "+highlight
    if (debug): html += " ("+note_id+" "+rank+")"
    html += "</div>"






# Display the output
print "<html><body>"+html+"</body></html>"

