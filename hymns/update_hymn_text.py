#!/usr/bin/env python
import os, shutil, pg, re
from db_functions import *

for hnum in range(1,2855):
  lastStanza = ""
  hymnText = ""
  firstLine = 1

  hymnLineData = db.query("select stanza, data from hymn_line where hnum="+str(hnum)+" order by lineorder").getresult()
  for hymnLine in hymnLineData:
    stanza = hymnLine[0]
    data = hymnLine[1]
    if lastStanza != stanza : 
      if firstLine : 
        firstLine = 0
      else: 
        hymnText += "\n"
      hymnText += stanza+" "
      lastStanza = stanza

    hymnText += data+"\n"
 

  #Store the hymn in the database
  db.query("update hymn set hymn_text='"+escape(hymnText)+"' where hnum="+str(hnum));
  print "Stored hymn #"+str(hnum)

 
