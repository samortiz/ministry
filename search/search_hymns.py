#!/usr/bin/env python
import os, shutil, pg, cgi, re
from db_functions import *
from verse_functions import *
from www_functions import *

print "Content-type: text/html\n"
html = "<form name='theform' method='post' action='search_hymns.py'>"

#Get the parameters
search_text = getParam("search_text")

html += "Search the hymns for "
html += "<input type='text' name='search_text' value='"+search_text+"'>"
html += "<input type='submit' name='submit' value='Search'>"

if (search_text != ""):
  html += "<br>Results:"
  html += "<table border=0 cellspacing=0 cellpadding=3>"
  sql = """
select hnum
  , ts_rank(to_tsvector(hymn_text), query) AS rank
  , ts_headline(hymn_text, query, 'HighlightAll=false') as hymn
from hymn, plainto_tsquery('"""+escape(search_text)+"""') as query
where hymn_text @@ query
order by rank desc;
"""
  searchResults = db.query(sql).getresult()
  for searchResult in searchResults:
    hnum = str(searchResult[0])
    hymn_text = searchResult[2]
    html += "<tr><td valign='top'><a href='/ministry/display_hymn.py?hnum="+hnum+"'>"+hnum+"</a></td>"
    html += "<td><pre>"+hymn_text+"</pre></td></tr>"

  html += "</table>"

html += "</form>"

# Display the output
print "<html><body>"+html+"</body></html>"

