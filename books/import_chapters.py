# Generate the chapter data files
import sgmllib
import os, random, time
from file_functions import *
from db_functions import *

#File Variables
cleanDir = 'clean_html'
chapDir = 'chap_html'

#Data Variable
chapterData = []


# -------------------- Chapter Parsing Functions -------------------------

def getStrBetween(s, startPos, startStr, endStr):
  "Gets the substring of s that is after startPos and between startStr and endStr"
  startSlice = s.find(startStr, startPos)
  endSlice = s.find(endStr, startSlice)
  # Error, start or end string not found
  if ((startSlice < 0) or (endSlice < 0)):
    #print "Str not found startPos="+str(startPos)+" startStr:"+startStr+"@"+str(startSlice)+" endStr:"+endStr+"@"+str(endSlice) 
    return ""
  return s[(startSlice+len(startStr)) : endSlice]

def getAllLi(s, chapNumParam, chapterList):
  "Returns a list of strings which are the contents of the li tags (or SP data)"
  chapNum = chapNumParam
  startStr = "<li>"
  endStr = "</li>"
  pos = 0
  foundStr = getStrBetween(s, pos, startStr, endStr)
  pos = s.find(endStr) + len(endStr)
  #print "      pos="+str(pos)+" foundStr="+foundStr
  while len(foundStr) > 0:
    chapNum += 1
    chapterList.append((str(chapNum), foundStr))
    foundStr = getStrBetween(s, pos, startStr, endStr)
    pos = s.find(endStr, pos) + len(endStr)
    #print "      pos="+str(pos)+" foundStr="+foundStr
    
    # Hardcode a hack for "Deeper Study of the Divine Dispensing" with it's special fellowship chapters
    if s.find("(SP1) A Supplementary Word (1)") > 0:
      if chapNum == 3: chapterList.append(("SP1", "(SP1) A Supplementary Word (1)"))
      if chapNum == 6: chapterList.append(("SP2", "(SP2) A Supplementary Word (2)"))
      
  return chapNum  


def getOlData(html, posParam, chapNumParam, chapterList):
  "Returns the new pos and chapNum, after adding the hapters found in the first <ol> after startPos to chapList " 
  pos = posParam
  chapNum = chapNumParam 
  # Get the first ordered list after startPos
  ol = getStrBetween(html, pos, "<ol", "</ol>")
  
  # If there already was an ordered list found, then we need to be continuing it, or else we will ignore this <ol> tag
  if ((chapNum > 0) and (ol.find('start="'+str(chapNum+1)+'"') < 0)):
    # We ignore the second ol tag, that is not a continuation of the previous ones
    #print "ol tag found, but not continuing with string start=\""+str(chapNum+1)+"\"  in ol="+ol
    ol = ""
  
  # Get all the <li> tags within the ordered list
  if len(ol) > 0 :
    pos = html.find(ol, pos) + len(ol)
    chapNum = getAllLi(ol, chapNum, chapterList)
    #print "pos:"+str(pos)+" ol:"+ol
    return pos, chapNum
  else:
    # If there is no ol found that matches, then set the pos past the end of the string
    return (len(html)+1), chapNum

# This will return a list of chapter information in the format ((chapNumStr, chapTitleStr), (chapNumStr, chapTitleStr)...)
# Collect <li> tags within a top level <ol> tag
# Parse only the first <ol> unless it's <ol start="x">, then it's continuing a previous list so we will continue as well
# There are a couple of special fellowships called "SP1" "SP2" which don't increment the numbering but still get added as chapters
# for nested <ol> tags, only take the top level ol tag
def parseChapters(html): 
  chapNum = 0
  pos = 0
  chapterList = []
  #print "toc="+html
  
  pos, chapNum = getOlData(html, pos, chapNum, chapterList)
  while pos < len(html):
    #print "calling getOlData again with pos="+str(pos)+" chap="+str(chapNum)
    pos, chapNum = getOlData(html, pos, chapNum, chapterList) 
  
  return chapterList
  




#----------------------------------------------------------------------------------------------
# Start the main program

# Directory containing all the books downloaded so far
currentBooks = os.listdir(chapDir)
currentBooks.sort()
#currentBooks = currentBooks[300:]
for book in currentBooks:
  # Determine if we need to look up chapters for this book
  if (   len(os.listdir(os.path.join(chapDir, book))) == 1 # only one chapter
      or book == "Three Aspects of the Church: Book 3, The Organization of the Church" #do manually
     ):  # There are no chapters in this book
    continue

  print "\n---------------------------------------------------------------------------------------------"
  print "Looking up chapters for "+book
  
  # Get the chapter titles
  chapters = [] #Contains ((chapNum-int, chapName-String))
  tocFile = os.path.join(chapDir, book, "chapter_Table of Contents.html")
  tocHtml = ""
  if os.path.exists(tocFile):
    tocHtml = readFile(tocFile)
    # Parse out all the chapter informtion from the html
    chapters = parseChapters(tocHtml)
    
    #If no chapters were found in the toc then what's up with having a TOC at all?
    if len(chapters) == 0:
      print "ERROR!  No chapters found when parsing the TOC!"
      sys.exit # Error, this will exit :) 
    
  else : # There is no table of contents
    # The new ministrybooks.org style doesn't have a separate table of contents
    # So we need to copy the first page over and check if there is a TOC in there
    if (os.path.exists(os.path.join(cleanDir, book, "page_001.html"))):  
      tocHtml = readFile(os.path.join(cleanDir, book, "page_001.html")) # Get the toc from the first page
      chapters = parseChapters(tocHtml)
      #If no chapters were found in the toc then what's up with having a TOC at all?
      if len(chapters) == 0:
        print "ERROR!  No chapters found when parsing the first page as a TOC, but there are more chapters!"
        sys.exit # Error, this will exit :) 
      else:
        # We found a toc in the first page, so copy that to the  chapter_Table of Contents.html file
        print "Found TOC on the first page"
    else:
      print "ERROR! Chapters exist, but I can't find the TOC"
      sys.exit

  # Calculate the chapter offset (if the book is a continuation of another book)
  chapterFiles = os.listdir(os.path.join(chapDir, book))
  chapterFiles.sort()
  chapterOffset = int(chapterFiles[0][8:11]) - 1  #The first chapter value (where the chapter counting starts)

  
  # If there is a table of contents (more than one chapter)
  if len(chapters) > 0:
    # Find the number of chapters on the file system
    chapterFileCount = 0
    for chapterFile in chapterFiles :
      if chapterFile.startswith("chapter_") and not chapterFile.startswith("chapter_Table") :
        chapterFileCount += 1
    
    # Find the number of chapters in the table of contents
    maxChapterTOC = len(chapters)

    # Check if the file system matches the table of contents    
    if (chapterFileCount != maxChapterTOC) :
      print "chapters="
      print chapters
      print "Error! The chapter files don't match the TOC!"
      print "Files="+str(chapterFileCount)+" TOC="+str(maxChapterTOC)
      sys.exit # This is an error, so it will exit.. :) 


  # Go through all the chapters  
  for chapter in chapters:
    chapTitle = chapter[1]
    chapNum = 0
    if (chapter[0].startswith("SP")):
      chapNum = chapter[0]
    else :
      chapNum = str(int(chapter[0]) + chapterOffset).rjust(3,"0")

    #print "  processing chapter "+chapNum+" ("+str(chapterOffset)+") "+chapTitle
    
    # verify that each chapter has an associated file (no chapter files are missing)
    chapterFile = "chapter_"+chapNum+".html"
    if not os.path.exists(os.path.join(chapDir, book, chapterFile)):
      print "ERROR! Missing File "+book+"/"+chapterFile
      sys.exit # Error, this will exit :) 
      
    # Get the page the chapter link was pointing to
    chapterHtml = readFile(os.path.join(chapDir, book, chapterFile))
    
    # Find the page number for this chapter
    chapPageNum = ""
    # Go through the all the page files and find one that matches the file contents
    cleanFiles = os.listdir(os.path.join(cleanDir, book))
    for cleanFile in cleanFiles:
      cleanHtml = readFile(os.path.join(cleanDir, book, cleanFile))
      if cleanHtml == chapterHtml:
        chapPageNum = cleanFile[5:8]
    
    # Check if no page was found to match the chapter contents
    if chapPageNum == "": 
      print "Error!  No matching html content in the clean_html dir for chapter "+chapNum
      sys.err # Error, this will exit :) 
  
    bookId = dbGetOne("select id from book where name='"+escape(book)+"'")
    if not bookId:
      print "Could not get book_id for book "+book
      sys.err

    print "Chapter "+chapNum+" on page "+chapPageNum+" : "+chapTitle
    db.query("insert into book_chapter (book_id, chap_num, chap_title, page_num) values "+\
              "("+bookId+", '"+escape(chapNum)+"', '"+escape(chapTitle)+"', "+chapPageNum+" )")



print "Now you should probably consider running some of import_chapters.sql"






