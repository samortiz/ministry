#!/usr/bin/env python
import os, shutil, pg, cgi, re
from db_functions import *
from verse_functions import *
from www_functions import *

print "Content-type: text/html\n"
html = "<form name='theform' method='post' action='generate_versesheet.py'>"

# ############################
# Harness code to try out different strings
test = """
(1 Chronicles 2:18)
(Job 1:2-3)
1 Peter 1:24-2:3
Revelation
(21:20), 
In Revelation 2, we see in verse 18 that He has eyes like a flame of fire. 
In First John chapter 1 verse 9 we see that His blood is effective for every sin, 
and keeps us in fellowship (v. 7)  Hallelujah!
First Corinthians 15:45 shows us that the Lord is the Spirit
Hebrews shows us in 4:12 that the Word of God is living
chapter 7 of John talks about living water
verse 39 mentions the Spirit
we see in chapter 2 verse 3 of 1 Peter that we need to taste the word
first Cor 12 
*** In verses 10 and 12 Paul concludes,
*** John 1:1,4,14
vv. 3-5
we see in v 9 (no period)
something seen in vv. 6 to 7 it is shown
1Sam 2 in verse 3
3 John 5
Jude 2-6
John 1:12-13
(3:15 - 16)
We see in 2:24 to 3:1
Mark 16:10 to 11 
Titus 1:15 - 2:1

"""

# Match books 
book = ("(((1|2|[fF]irst|[sS]econd)[ ]*(Chronicles|Chron|Corinthians|Cor|Kings|"+
     "Thessalonians|Thess|Thes|Peter|Pet|Samuel|Sam|Timothy|Tim|John))|"+
     "((3|[tT]hird|)[ ]*John)|"+
     "(Acts|Amos|Daniel|Dan|Deuteronomy|Deut|Ecclesiastes|Eccl|Ephesians|Eph|Esther|Esth|Exodus|Exo|"+
     "Ezekiel|Ezek|Ezra|Galatians|Gal|Genesis|Gen|Habakkuk|Hab|Haggai|Hag|Hebrews|Heb|Hosea|Hos|"+
     "Isaiah|Isa|James|Jeremiah|Jer|Job|Joel|Joe|John|Jonah|Josh|Jude|Judges|Judg|Lamentations|Lam|"+
     "Leviticus|Lev|Luke|Malachi|Mal|Mark|Matthew|Matt|Micah|Nahum|Nehemiah|Neh|Numbers|Num|"+
     "Obadiah|Obad|Philippians|Phil|Philemon|Philem|Proverbs|Prov|Psalm[s]*|Psa|Revelation|Rev"+
     "Romans|Rom|Ruth|Song of (Songs|Solomon)|S\.S\.|SS|Titus|Zechariah|Zech|Zephaniah|Zeph))")

book_with_no_chapters = "(((2|[sS]econd|3|[tT]hird)[ ]*John)|Jude|Obadiah|Obad|Philemon|Philem)"

book_with_chapters =  ("(((1|2|[fF]irst|[sS]econd)[ ]*(Chronicles|Chron|Corinthians|Cor|Kings|"+
    "Thessalonians|Thess|Thes|Peter|Pet|Samuel|Sam|Timothy|Tim))|"+
    "((1|[fF]irst)[ ]*John)|"+
    "(Acts|Amos|Daniel|Dan|Deuteronomy|Deut|Ecclesiastes|Eccl|Ephesians|Eph|Esther|Esth|Exodus|Exo|"+
    "Ezekiel|Ezek|Ezra|Galatians|Gal|Genesis|Gen|Habakkuk|Hab|Haggai|Hag|Hebrews|Heb|Hosea|Hos|"+
    "Isaiah|Isa|James|Jeremiah|Jer|Job|Joel|Joe|John|Jonah|Josh|Judges|Judg|Lamentations|Lam|"+
    "Leviticus|Lev|Luke|Malachi|Mal|Mark|Matthew|Matt|Micah|Nahum|Nehemiah|Neh|Numbers|Num|"+
    "Philippians|Phil|Proverbs|Prov|Psalm[s]*|Psa|Revelation|Rev"+
    "Romans|Rom|Ruth|Song of (Songs|Solomon)|S\.S\.|SS|Titus|Zechariah|Zech|Zephaniah|Zeph))")

# Match Chapters (this is book + chapter, or just chapter with book implied from the context)
chapter_full = "("+book_with_chapters+"[ ]*([cC]hapter){0,1} *([0-9]{1,3}))"
chapter_verbose = "([cC]hapter *([0-9]{1,3}) *of *"+book_with_chapters+")"
chapter_brief = "([cC]hapter[ ]*([0-9]{1,3}))"
chapter = "("+chapter_full+"|"+chapter_verbose+"|"+chapter_brief+")"


# Match particular verse(s) (book+chapter+verse, or perhaps just verse with book or chapter implied from context)
verse_full = "("+chapter+" *(:|[vV]erse) *([0-9]{1,3})( *(to|-) *(([0-9]{1,3}) *: *){0,1}([0-9]{1,3})){0,1})"
verse_no_chapters = "("+book_with_no_chapters+" *([vV]erse){0,1} *([0-9]{1,3})( *(to|-) *(([0-9]{1,3}) *: *){0,1}([0-9]{1,3})){0,1})"
verse_vv = "(vv\. *([0-9]{1,3}) *(to|-) *([0-9]{1,3}))"
verse_v = "(v\. *([0-9]{0,3}))"
verse_verses = "([vV]erses *([0-9]{1,3}) *(to|-) *([0-9]{1,3}))"
verse_verse = "([vV]erse *([0-9]{1,3}))"
verse_just_numbers = "(([0-9]{1,3}) *: *([0-9]{1,3})( *(to|-) *(([0-9]{1,3}) *: *){0,1}([0-9]{1,3})){0,1})"
verse = ("("+verse_full+"|"+verse_no_chapters+"|"+verse_vv+"|"+verse_v+"|"+
    verse_verses+"|"+verse_verse+"|"+verse_just_numbers+")")




#TODO : Handle lists of verses with , separators 

#Get the parameters
text = getParam("text")
hide_verse_numbers = getParam("hide_verse_numbers")

text = test # ######### Remove this line before going live

# Variables
verses = []
last_book = "John"
last_chap_num = "15"


def getGroup(match, grp):
  "Returns the specified group number.  If a -1 is the grp number then, it returns """
  # For any invalid index, return an empty string
  if ((grp < 0) or (grp > match.groups)) : 
    return ""
  else : 
    return toString(match.group(grp))
#end def getGroup



def makeRef(book, chap, verse, chap_end="", verse_end=""):
  "Creates a standard reference string from a book chapter and verse."
  ref = ""
  hasChapters = 1
  if (re.match(book_with_no_chapters, book)):
    hasChapters = 0
  # Default the ending chapter and verse to match (for single-verse mode instead of ranges)
  if chap_end == "": chap_end = chap
  if verse_end == "": verse_end = verse

  # Start Constructing the reference
  ref = book+" "
  if hasChapters: ref += chap+":"
  ref += verse

  if ((chap_end != chap) or (verse_end != verse)): 
    ref += "-"
    if hasChapters and chap_end != chap:
      ref += chap_end+":"
    ref += verse_end

  return ref
#end def makeRef 
    


def storeVerseData(ref, pattern, bookGrp, chapGrp, bookChapGrp, verseGrp, endChapGrp, endVerseGrp, strPos):
  "Takes a reference and a pattern, and returns the reference and verse text for the verse(s) found"
  global verses, last_book, last_chap_num
  verseData = []

  # Check for a match on the pattern
  patternMatch = re.match(pattern, ref)
  if patternMatch :
    #Debug to help in adding new groups
    #print patternMatch.groups()
    #print "<br>"

    #Check what kind of mode we are in (getting a verse, or just setting context for book and/orchapter)
    mode = "verse"
    if ((chapGrp >= 0) and (verseGrp < 0)): mode = "chapter"
    if ((chapGrp < 0) and (verseGrp < 0)): mode = "book"

    #bookChap is a book+chap_num (hard to separate in some groups)
    book_name = getGroup(patternMatch, bookGrp)
    chap_num = getGroup(patternMatch, chapGrp)
    bookChap = getGroup(patternMatch, bookChapGrp)
    verse_num = getGroup(patternMatch, verseGrp)
    chap_end_num = getGroup(patternMatch, endChapGrp)
    verse_end_num = getGroup(patternMatch, endVerseGrp)

    #Fill in all the implicit information
    # If the reference contains a book name, then extract it
    bookMatch = re.search(book, ref)
    if bookMatch:
      book_name = bookMatch.group()

    # If there is a chapter with a book name, then separate the chapter number eg. "John 12", "John chapter 12" "chapter 12 of John"
    if bookChap != "":
      chapWithoutBook = re.sub(book, "", bookChap)
      chapNumMatch = re.search("[0-9]{1,3}",chapWithoutBook)
      if chapNumMatch: 
        chap_num = chapNumMatch.group()
  
    if book_name == "":
      book_name = last_book
    else: 
      book_name = fixBookName(book_name)

    if chap_end_num == "":
      if chap_num != "": 
        chap_end_num = chap_num
      else:
        chap_end_num = last_chap_num
        chap_num = last_chap_num

    if verse_end_num == "":
      verse_end_num = verse_num


    # Get the ids of the start and ending verse
    startVerseRef = makeRef(book_name, chap_num, verse_num)
    startVerseId = getVerseId(startVerseRef)
    endVerseRef = makeRef(book_name, chap_end_num, verse_end_num)
    endVerseId = getVerseId(endVerseRef)
   
    if (mode == "verse"):
      if (startVerseId == ""): print "<font color='red'>Error! Invalid reference : "+startVerseRef+" in "+ref+"</font><br>"
      if ((endVerseId == "") and (endVerseRef != startVerseRef)): print "<font color='red'>Error! Invalid reference : "+endVerseRef+"</font><br>"

    # Generate a standardized reference
    standardRef = makeRef(book_name, chap_num, verse_num, chap_end_num, verse_end_num)

    # if we have a valid start and end, lookup the verses
    verseText = ""
    if ((mode == "verse") and (startVerseId != "") and (endVerseId != "")):
      # Get the text of the verses (all the text in one block)
      verseList = db.query("select verse_num, verse from verse where id >="+startVerseId+" and id <= "+endVerseId+" order by id").getresult()
      firstVerse = 1
      for v in verseList:
        if firstVerse: 
          firstVerse = 0
        else: 
          if hide_verse_numbers == "true": 
            verseText += " "
          else : 
            verseText += " "+v[0]+". "
        verseText += v[1]
 
      # Get the verse data for this reference
      verseData.append(standardRef)
      verseData.append(verseText)
    
    # Store the context (in case the next verse needs it)
    last_book = book_name
    if mode != "book": 
      last_chap_num = chap_num
    #print "mode="+mode+" last_book="+last_book+" last_chap_num="+last_chap_num+"<br>"


  #Store the results in the global variable
  if len(verseData) > 0 : 
    verseData.append(strPos) #Position in the string that the reference was found
    verses.append(verseData) # Store the reference

#End def storeVerseData



# Title
html += "Verse Sheet Generator<br>"

# Display when no text is submitted
#if text == "" : 
#  html += "<textarea rows=30 cols=80 name='text'></textarea>  <input type='submit'><br>"


# Display when text is submitted
if text != "" : 
  html += "<pre>"+text+"</pre>"
  #Find any instance of a reference
  searchPattern = "("+verse+"|"+chapter+"|"+book+")"

  #Go through each match (reference) found
  for match in re.finditer(searchPattern, text):
    matchStr =  match.group(0)
    matchPos = match.start()
    verseCount = len(verses)

    # If it's any kind of verse reference eg. Rom 12:12, Philemon 2, John 1:12-13, vv.12-13, v. 13, verse 12
    if re.match(verse, matchStr):
      # storeVerseData(ref, pattern, bookGrp, chapGrp, bookChapGrp, verseGrp, endChapGrp, endVerseGrp, strPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_full, -1, -1, 2, 27, 31, 32, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_no_chapters, 1, -1, -1, 6, -1, 11, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_vv, -1, -1, -1, 2, -1, 4, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_v,  -1, -1, -1, 2, -1, -1, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_verses,-1, -1, -1, 2, -1, 4, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_verse, -1, -1, -1, 2, -1, -1, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, verse_just_numbers, -1, 2, -1, 3, 7, 8, matchPos)
    if re.match(chapter, matchStr):
      if len(verses) == verseCount: storeVerseData(matchStr, chapter_full, 2, 11, -1, -1, -1, -1, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, chapter_verbose, 3, 2, -1, -1, 1, -1, matchPos)
      if len(verses) == verseCount: storeVerseData(matchStr, chapter_brief, -1, 2, -1, -1, 1, -1, matchPos)
    if len(verses) == verseCount: storeVerseData(matchStr, book, 1, -1, -1, -1, 1, -1, matchPos)

    html += matchStr+" ("+str(match.start())+")<br>"

html += "<br>Verses Found <br>"
for verse in verses:
  html += "<b>"+verse[0]+"</b> "+verse[1]+"<br>"
  

html += "</form>"


# Display the output
print "<html><body>"+html+"</body></html>"

