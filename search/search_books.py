#!/usr/bin/env python
import os, shutil, pg, cgi, re
from db_functions import *
from verse_functions import *
from www_functions import *

PAGESIZE = 100

print "Content-type: text/html\n"

#Get the parameters
debug = getParam("debug")
search_text = getParam("search_text")
pageStr = getParam("page")
page = 0
if pageStr:
  page = int (pageStr)

html = "<form name='theform' method='post' action='search_books.py'>"
html += "Search the Ministry Books for "
html += "<input type='text' name='search_text' value='"+search_text.replace("'", "&#39;")+"'>"
html += "<input type='hidden' name='debug' value='"+debug+"'>"
html += "<input type='submit' name='submit' value='Search'>"
html += "</form>"

if (search_text != ""):

 # ------------------------- Search Book Titles -----------------
  sql = """
select b.id as book_id
     , b.path_name as book_path_name
     , b.display_name as book_name
     , ts_rank(to_tsvector(b.display_name), query, 0) AS rank
from  book b
    , plainto_tsquery('"""+escape(search_text)+"""') as query
where to_tsvector('english', b.display_name) @@ query
order by rank desc, b.id
"""
  bookResults = dbQuery(sql)
  if len(bookResults) > 0 :
    html += "<b>Book Titles</b> :"
  for bookResult in bookResults:
    book_id = str(bookResult[0])
    book_path_name = str(bookResult[1])
    book_name = str(bookResult[2])
    rank = str(bookResult[3])

    html += "<div style='padding:3px'>"
    html += "<a href='/books/"+book_path_name+"/page_001.html'>"+book_name+"</a>"
    if (debug): html += " ("+book_id+" "+rank+")"
    html += "</div>"


  # ------------------- Search Chapter Titles ------------------------

  sql = """
select bc.id as book_chapter_id
     , b.path_name as book_path_name
     , b.display_name as book_name
     , coalesce(bc.chap_title,'') as title
     , bc.chap_num
     , bc.page_num 
     , ts_rank(to_tsvector(bc.chap_title), query, 0) AS rank
from  book_chapter bc
    , plainto_tsquery('"""+escape(search_text)+"""') as query
    , book b 
where to_tsvector('english', bc.chap_title) @@ query
  and b.id = bc.book_id
order by rank desc, bc.id
"""

  chapResults = dbQuery(sql)
  if len(chapResults) > 0 :
    html += "<hr><b>Chapter Titles</b> :"
  for chapResult in chapResults:
    book_chapter_id = str(chapResult[0])
    book_path_name = chapResult[1]
    book_name = chapResult[2]
    chap_title = chapResult[3]
    chap_num = chapResult[4]
    page_num = str(chapResult[5])
    rank = str(chapResult[6])

    html += "<div style='padding:3px'>"
    html += "<a href='/books/"+book_path_name+"/page_"+page_num.rjust(3,"0")+".html'>"+book_name+" Chapter "+chap_num+"</a>"
    html += " : "+chap_title
    if debug: html += " ("+book_chapter_id+" "+rank+")"
    html += "</div>"



  # ------------------- Search Book Content and Section Headings ----------------------------------
  sql = """
select bc.id as book_chunk_id
     , b.path_name as book_path_name
     , b.display_name as book_name
     , coalesce(bc.section_title,'') as title
     , bc.page_num
     , ts_rank(      /*       title  body */
            array[0.1,  0.1,  0.4,   0.2]
          , setweight(to_tsvector(coalesce(bc.section_title, '')),'B')
         || setweight(to_tsvector(bc.data),'A')
         ,  query, 0) AS rank
     , ts_headline(bc.data, query, 
         'HighlightAll=false, MaxWords=100, MinWords=30, MaxFragments=5, FragmentDelimiter="...<br>..."'
        ) as text_highlight
from  book_chunk bc
    , plainto_tsquery('"""+escape(search_text)+"""') as query
    , book b 
where to_tsvector('english', bc.searchtext) @@ query
  and b.id = bc.book_id
  and bc.tag_name = 'p'
order by rank desc, bc.id
"""
  sql += "limit "+str(PAGESIZE)+" offset "+str(page * PAGESIZE)

  startTime = getTime()
  searchResults = db.query(sql).getresult()
  endTime = getTime()
  
  if len(searchResults) > 0:
    html += "<hr><b>Book Contents</b>:"
    if debug: html += " ("+str(endTime-startTime)+"ms)"
  for searchResult in searchResults:
    book_chunk_id = str(searchResult[0])
    book_path_name = str(searchResult[1])
    book_name = str(searchResult[2])
    title = str(searchResult[3])
    page_num = str(searchResult[4])
    rank = str(searchResult[5])
    text_highlight = searchResult[6]
 
    html += "<div style='padding:3px'>"
    html += "<a href='/books/"+book_path_name+"/page_"+page_num.rjust(3,"0")+".html'>"
    html += book_name+" pg."+page_num+"</a> <i>"+title+"</i>"
    if debug: html +=" ("+book_chunk_id+" "+rank+")"
    html += "<br>"+text_highlight
    html += "</div>"

  # If we found exactly this number of search terms, there are probably more
  if len(searchResults) == PAGESIZE :
    html += "<form name='pageform' method='post' action='search_books.py'>"
    html += "<input type='hidden' name='search_text' value='"+search_text.replace("'", "&#39;")+"'>"
    html += "<input type='hidden' name='page' value='"+str(page+1)+"'>"
    html += "<input type='submit' name='See More Results' value='See More Results'>" 
    html += "<input type='hidden' name='debug' value='"+debug+"'>"
    html += "</form>"




# Display the output
print "<html><body>"+html+"</body></html>"

