#!/usr/bin/env python
# Parse the text file with sonbook songs into the database
import re
from db_functions import *

def cleanText(inStr):
  out = inStr.strip()
  return out
 
#Open the sonbook text file 
file = open("songbook/final_songbook_data.txt","r")

#Stores the last X lines in order to remove duplicates
songbook_number = ""
info = ""
ref = ""
stanza = ""
line = 0
data = ""
type = ""
foundError = 0

#Starts a new stanza, sets all the variables as necessary
def newStanza():
  # global so it can alter the value 
  global stanza, line 
  stanza = ""
  line = 0
  
# Go through all the lines in the file
for lineText in file.readlines():
  
  #Start a new line
  txt = cleanText(lineText)
  line += 1
  type = "data"
  
  # Check if we're starting a new song
  songbookMatch = re.match("^Calgary Songbook : *([0-9]{4})$", txt)
  if (songbookMatch):
    songbook_number = str(songbookMatch.group(1))
    newStanza()
    #Insert the new songbook number into the database
    db.query("insert into hymn (hnum, calgary_songbook_num) values ("+songbook_number+", "+songbook_number+")")
    continue # Do not insert this line
    
  #Blank lines reset the stanza 
  if (txt == ""):
    newStanza()
    continue #Don't insert  blank lines in the database

  # Check if the line is the start of a new stanza 
  if (re.match("^[0-9cs][0-9AB]{0,1}$", txt)):
    stanza = txt
    line = 0
    continue #Do not insert to the database
  
  # Check for comment lines  (italics markup)
  commentMatch = re.match("^I:(.*)$", txt)
  if (commentMatch): 
    txt = str(commentMatch.group(1)).strip()
    type = "comment"
  
  #Check for info lines (tune, references, etc)
  infoMatch = re.match("^((Tune)|(Ref)|(Info)):(.*)$", txt)
  if (infoMatch):
    type = str(infoMatch.group(1)).strip()
    txt = str(infoMatch.group(5)).strip()
    #TODO insert into the hymn_ref table (need to fix/normalize the references first)
    line = 0
    
  #Error Checking
  if (songbook_number == "") : 
    print "Error! No songbook number."
    foundError = 1
  if  ((stanza == "") & (type=="data")):
    print "Error! No stanza found."
    foundError = 1
  
  if (foundError == 0):  
    insertSQL = "insert into hymn_line (hnum, stanza, line, data, type) values ('"+songbook_number+"','"+stanza+"','"+str(line)+"','"+escape(txt)+"','"+type+"' )"
    db.query(insertSQL)
    print "Inserted "+insertSQL
    #print  songbook_number+":"+stanza+":"+str(line)+":"+type+"="+txt
  else:
    print "songbook number : "+songbook_number+" stanza="+stanza+" line="+str(line)+" type="+type+" txt="+txt
    break
