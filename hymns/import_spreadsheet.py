#!/usr/bin/env python
# This script opens an XLS file with a specific format and inserts the data into the table in the database 
# xlrd is in the apt-get package python-xlrd
import xlrd, pg, re, sys, datetime
from db_functions import *
from verse_functions import *

#Parameters
fileName = "hymns_ref_master.xls"
import_batch = fileName+" "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M.%S")


def abortImport():
  "If something went wrong, then we delete all the inserted data in this batch and exit."
  db.query("delete from hymn_verse where import_batch='"+import_batch+"'")
  print "All inserted data has been deleted."
  sys.exit(0)

def insertVerse(hymn_ref_id, ref) :
  verse_id = getVerseId(ref)
  if (verse_id != "") :
    db.query("insert into hymn_verse_verse (hymn_verse_id, verse_id) values ("+hymn_verse_id+", "+verse_id+") ") 
  else :  # We have an error!  Could not find the verse, abort the whole import!
    print "Error! Verse lookup failed for '"+ref+"'"
    abortImport()




# ---------------------------- Main Code -------------------------------------

#Open the xls doc
book = xlrd.open_workbook(fileName)
sh = book.sheet_by_index(1) # Second worksheet, the "Completed" tab

# This is used to abort the import if there are errors in the data
foundError = 0
data = []

# Go through the rows, and make a 2d array of all the cells
for row in range(sh.nrows)[1:]: # Remove the header row
  hnum = toString(sh.cell_value(row, 0))
  stanza = toString(sh.cell_value(row,1))
  line = toString(sh.cell_value(row,2))
  ref_orig = toString(sh.cell_value(row,3))
  fn = toString(sh.cell_value(row,4))
  par = toString(sh.cell_value(row,5))
  key = toString(sh.cell_value(row,6))
  min_ref = toString(sh.cell_value(row,7))
  min_quote = toString(sh.cell_value(row,8))
  completed_by = toString(sh.cell_value(row,9))
  verified_by = toString(sh.cell_value(row,10))
  comment = toString(sh.cell_value(row,11))

  #Fix up the reference (if possible)
  ref = fixRef(ref_orig)

  # Verify the reference
  if (not validRef(ref)) : 
    if (ref_orig != ""): # If the reference was blank, then just skip the line from the import (not an error)
      foundError = 1
      print "INVALID REFERENCE : '"+ref_orig+"' for hymn #"+hnum+" in stanza "+stanza

  else : # we have a valid reference
    #Add this row to the data list
    data.append((hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, completed_by, verified_by, comment))

if foundError : 
  print "The data has NOT been imported.  Please correct the errors to continue."
  sys.exit(0)

# ---------------------- All is well with the spreadsheet.  So begin the import! ------------------------------------

# Import the data to the database
for row in data :
  hnum = row[0]
  stanza = row[1]
  line = row[2]
  ref = row[3]
  fn = row[4]
  par = row[5]
  key = row[6]
  min_ref = row[7]
  min_quote = row[8]
  completed_by = row[9]
  verified_by = row[10]
  comment = row[11]
  
  #Generate a new ID (from the sequence
  hymn_verse_id = dbGetOne("select nextval('hymn_verse_id_seq') ")

  #Check if the reference already exists in the database 
  existing_hymn_verse_id = dbGetOne("select id from hymn_verse where hnum='"+hnum+"' and stanza='"+stanza+"' and line='"+line+"' and ref='"+ref+"' ")
  if (existing_hymn_verse_id != "") :
    # print  "Verse already exists! hymn_verse_id="+existing_hymn_verse_id+" hnum="+hnum+" stanza="+stanza+" line="+line+" "+ref
    continue

  print  "Importing hymn #"+hnum+" stanza "+stanza+" - "+ref+" hymn_verse_id="+hymn_verse_id
  #Insert the row
  sql = ("insert into hymn_verse (id, hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, completed_by, verified_by, comment, import_batch) values "+
   "("+hymn_verse_id+", '"+hnum+"','"+stanza+"','"+line+"','"+ref+"','"+fn+"','"+par+"','"+key+"','"+escape(min_ref)+"','"+escape(min_quote)+"', "+
   "'"+escape(completed_by)+"','"+escape(verified_by)+"', '"+escape(comment)+"', '"+escape(import_batch)+"' ) ")
  db.query(sql)

  #Lookup the verses 
  if validRefSingle(ref): 
    insertVerse(hymn_verse_id, ref)

  else : # It's a range of verses (eg. "Eph 1:19-22")
      #Calculate the start verse and the end verse
      startVerse = str(re.match("^([123]{0,1}[ ]{0,1}[A-Za-z]{1,10} [0-9]{0,3}[:]{0,1}[0-9]{0,3})[ ]{0,1}-.*$", ref).group(1))
      endChapVerse = str(re.match("^.* *- *([0-9]{0,3}[:]{0,1}[0-9]{1,3})$", ref).group(1))
      if (not re.match(".*:.*", endChapVerse)) : # If the ending ref does not have a chapter
        # Get the chapter from the starting verse ref
        endChap = str(re.match("^[123]{0,1}[ ]{0,1}[A-Za-z]{1,10} ([0-9]{0,3})[:]{0,1}[0-9]{0,3}.*$", ref).group(1))
        if (re.match(".*:.*",ref)): # If there is no : in the entire reference, then we can ignore the chapters altogether (don't add the chapter in)
          endChapVerse = endChap+":"+endChapVerse
      # The book that these verses are in
      endBook = str(re.match("^([123]{0,1}[ ]{0,1}[A-Za-z]{1,10}) .*$", ref).group(1))
      endVerse = endBook+" "+endChapVerse
      # Get the ids for the starting and ending verses (they are all sequential)
      startVerseId = getVerseId(startVerse)
      endVerseId = getVerseId(endVerse)

      # If any verse lookup failed, then we have a problem (like Acts 29:1 for example)
      if ((startVerseId == "") | (endVerseId=="")) :
        print "Error looking up start and/or end verse!"
        print "Verse Ref Start='"+startVerse+"' End='"+endVerse+"' "
        print "verse(id) Start="+startVerseId+" End="+endVerseId
        abortImport()

      #Insert  the range of verses into the database
      db.query("insert into hymn_verse_verse (hymn_verse_id, verse_id) (select "+hymn_verse_id+", id from verse where id >= "+startVerseId+" and id <= "+endVerseId+")")
      print "  Inserted range of verses : "+startVerse+"-"+endVerse+" id="+startVerseId+"-"+endVerseId








