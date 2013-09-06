#!/usr/bin/env python
import os, shutil, pg, re
from db_functions import *

#Config variables
dir = "chordpro_files"

def createHymnFile(hnum, data):
  "Create or replace the file for this hymn, using the specified data for content, and the hnum for the filename."
  fileName = dir+"/"+hnum+".cho"
  file = open(fileName,"w")
  file.write(data)
  file.close()
  print "created "+fileName


# --------------- Main ------------------------

# Create the root directory
if (not os.path.exists(dir)) : 
  os.makedirs(dir)

# Go through all the hymns 
for songNum in range(1,2854):
  out = ""
  row= dbGetRow("select hnum, chinese_num, spanish_num, korean_num, tagalog_num, calgary_songbook_num from hymn where hnum="+str(songNum)
                +" and hnum in (select distinct hnum from hymn_line_chord)")  # Limit only to hymns with chords
  # If no row is found for this hymn, then it's not a valid song number (calgary songbook is non-sequential)
  if (len(row) == 0): 
    continue # Do not do anything further, go to the next hymn
  
  hnum = toString(row[0]).rjust(4,'0')
  
  #------ Begin Generating the Chordpro data -------------------
  #Header stuff
  headerData = db.query("select key, time_signature from hymn where hnum="+hnum).getresult()
  key = headerData[0][0]
  time = headerData[0][1]
  if (key == None): key = ""
  if (time == None): time = ""

  #Draw the header data (chordpro formatted)
  out += "{title:Hymn #"+hnum+"}\n"

  if ((key != "") or (time != "")): 
    out += "{comment: "+key+" "+time+"}\n"

  # Go through all the lines in this hymn
  currStanza = ""
  firstChorus = 1 # Set to 0 after the first chorus is over

  hymnLines = db.query("select id, stanza, line, data, type from hymn_line where hnum="+hnum+" order by lineorder").getresult()
  for hymnLine in hymnLines :
    hymn_line_id = toString(hymnLine[0])
    stanza = toString(hymnLine[1])
    line = toString(hymnLine[2])
    data = toString(hymnLine[3])
    data_type = toString(hymnLine[4])
    
    if ((currStanza != stanza) or (line == "1")) : # We are switching to a new stanza
      if (currStanza == "c") : out += "{eoc}\n"
      out += "\n" # Empty lines between all stanzas 
      
      # Start the new stanza
      if (stanza == "c") : out += "{soc}\n"
      else : 
        if ((stanza != "s") and (stanza != "")) : 
          out += stanza+". "
          
      if (currStanza == "c") : firstChorus = 0 # If we are switching out of a chorus, then don't do the chorus stuff again
      currStanza = stanza
    
    
    if (data_type == "data"): 
      #Setup all the chord data for this line into an accessible structure
      chordDataRs = db.query("select pos, chord from hymn_line_chord where hymn_line_id="+hymn_line_id).getresult()
      chordData = {} # Stores chords keyed on character position
      for chordRow in chordDataRs :
        chordData[chordRow[0]] = chordRow[1]
        
      #Loop variables for iterating the line
      chPos = 0 #counter, character position in the line
      
      # Go through each character in the line
      for ch in data : 
        #If this position has a chord associated
        if (chPos in chordData):
          chord = chordData[chPos]
          out += "["+chord+"]"
        out += ch
        chPos = chPos + 1
      
      # Done outputting all the characters for this line
      out += "\n"
      
    else :  # data_type is a comment or verse reference or something else
      out += "{comment:"+data+"}"
  
  #When we end the whole hymn with a chorus, we need to close the tag
  if (currStanza == "c"): out += "{eoc}" 

  #Create or replace the file with all the data
  createHymnFile(hnum, out)

print "Done."
