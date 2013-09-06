# Get chapters for books from the web
# This will compare the chap_html directory with the books on ministrybooks.org
# any books on ministrybooks.org that do not have directories created in chap_html
# This will lookup the chapter list and download the first page of each chapter, storing it in chapter_x.html in the chap_html dir
# After running this and getting the books from the web you need to run gen_chapter_data.py
import urllib, urllib2, cookielib, sgmllib
import os, random, time

#URL Variables
indexURL = 'http://www.ministrybooks.org/alphabetical.cfm'
bookURLBase = 'http://www.ministrybooks.org/'
chapterFrameURL = 'http://www.ministrybooks.org/reading-banner.cfm'

#File Variables
chapDir = 'chap_html'

#Data Variable
chapterData = []

#Cookie Variables, used to store cookies to maintain session state
cookiejar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1')]



# ---------------------- Misc Functions --------------------------------

#Returns a string with the HTML content of the requested URL (uses cookies)
def getPage(url):
  response = opener.open(url)
  return response.read()

# Ensures that a directory exists, it creates it if necessary
def ensure_dir(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)

# Creates a file and writes the string into it
def writeStringToFile(fileName, contentStr):
  file = open(fileName,"w")
  file.write(contentStr)
  # File closing is handled automaticaly (so the docs say!)
  file.close() # But I'm not entirely sure about that... :) 


#Cuts a string from the first startStr to the first endStr and returns it
# Note: this also strips off whitespace from the final string
def cutStr(sourceStr, startStr, endStr):
  startCutIndex = sourceStr.find(startStr) + len(startStr)
  endCutIndex = sourceStr.find(endStr)
  return sourceStr[startCutIndex:endCutIndex].strip()


# Removes all the header/footer stuff from the HTML page
# NOTE: This is copied from getbooks.py, if it changes there, it will probably need to be changed here too and vice versa
# Note: This is very sensitive to changes on the server and may need to be changed when there are updates
def cleanupHtml(pageHtml):
  #Cut off the header/footer stuff
  cleanHtml = cutStr(pageHtml, '<div id="booktext">', '</div> <!-- /booktext -->')

  # Trim the Next/Prev paragraphs
  pIndex = cleanHtml.find('</p>')
  if pIndex >= 0:
    cleanHtml = cleanHtml[pIndex+len('</p>'):] # crop the initial paragraph (containing Prev/Next)

  pIndex = cleanHtml.rfind('<p ')
  if pIndex >= 0:
    cleanHtml = cleanHtml[:pIndex] # Crop the last paragraph (containing Prev/Next)

  cleanHtml = cleanHtml.strip()

  #clean off the saved from comment on the first page
  cIndex = cleanHtml.find('<!-- saved from')
  if cIndex >= 0:
    cIndex = cleanHtml.find('-->')
    cleanHtml = cleanHtml[cIndex+len('-->'):] #trim off the comment

  return cleanHtml



# ---------------------------------------------------------------------
# Parser to take the alphabetial list of books and get URLs and book names
class booklistParser(sgmllib.SGMLParser):
  "Parses the book list, to pull out the links to the book titles"

  def parse(self, s):
      "Parse the given string 's'."
      self.feed(s)
      self.close()

  def __init__(self, verbose=0):
      sgmllib.SGMLParser.__init__(self, verbose)
      self.links = []
      self.inATag = 0
      self.aHref = ""
      self.aValue = ""

  def start_a(self, attributes):
    self.inATag = 1
    self.aValue = ""
    for name, value in attributes:
      if name == "href":
        self.aHref=value  

  def end_a(self):
    self.inATag = 0   
    if ((self.aValue != "") and (self.aHref.startswith("books.cfm?id="))):
      self.links.append((self.aHref, self.aValue))

  def handle_data(self, data):
    "Handle the textual 'data'."
    if self.inATag == 1 : 
      self.aValue += data

  def getLinks(self):
      return self.links


# Chapter parser - Parses the HTML frame, and gets the first page of each chapter
class chapterParser(sgmllib.SGMLParser):
  "Parses the chapter choicelist frame, to get the chapter information"

  def parse(self, s):
      "Parse the given string 's'."
      self.feed(s)
      self.close()

  def __init__(self, verbose=0):
      sgmllib.SGMLParser.__init__(self, verbose)
      self.links = []
      self.inOptionTag = 0
      self.optionHref = ""
      self.optionChapNum = ""
      
  def start_option(self, attributes):
    self.inOptionTag = 1
    self.optionChapNum = ""
    for name, value in attributes:
      if name == "value":
        self.optionHref=value  

  def end_option(self):
    self.inOptionTag = 0   
    if ((self.optionChapNum != "") and (self.optionHref.startswith("'text','Chapter.cfm?id="))):
      self.optionHref = self.optionHref[len("'text','"):len(self.optionHref)-1] # Trim off the funny stuff (and quotes)
      pageHtml = getPage(bookURLBase+self.optionHref)
      cleanHtml = cleanupHtml(pageHtml)
      self.links.append((self.optionHref, self.optionChapNum, pageHtml))

  def handle_data(self, data):
    "Handle the textual 'data'."
    if self.inOptionTag == 1 : 
      self.optionChapNum += data

  def getLinks(self):
      return self.links



# -----------------------------------------------------------------------------------------
# Gets the chapters of a book, specified by the book's name and URL 
# URL should be in the format given in the href component of the A tag on the alphabet page (books.cfm?id=...)
def getChapters(bookName, URL):
  print "Downloading chapters for the book "+bookName+" with URL="+URL

  # Setup the directory to store the book's chapter data
  bookPath = os.path.join(chapDir, bookName)
  ensure_dir(bookPath)
  
  # Get the frameset for the book
  framesetHtml = getPage(bookURLBase+URL)
  #Get the chapter frame contents : chapter URL listing
  chapHtml = getPage(chapterFrameURL)
 
  #Parse out the anchor tags
  chapList = chapterParser()
  chapList.parse(chapHtml)
  chapters = chapList.getLinks()
  
  # Go through the chapters
  for chapter in chapters:
    chapNum = chapter[1]
    chapHtml = chapter[2]
    pageFileName = "chapter_"+chapNum.rjust(3,"0")+".html"
  
    #Write out the chapter page
    outputPage(bookName, pageFileName, chapHtml)
   

#Clean a single page of html, removing the header and footer
def outputPage(bookName, pageFileName, pageHtml):
  #Create the output directory if necessary
  outputDir = os.path.join(chapDir, bookName)
  ensure_dir(outputDir)

  cleanHtml = cleanupHtml(pageHtml)
  
  #Write out the output file
  writeStringToFile(os.path.join(outputDir, pageFileName), cleanHtml)
  


#Returns a list of all the books missing from the data set, given a master list (the www books are all the books on the web site)
def getMissingBooks(wwwBooks, dataDir):
  missingBooks = []
  #Directory containing all the books downloaded so far
  currentBooks = os.listdir(dataDir)
  for book in wwwBooks:
    bookURL = book[0]
    bookName = book[1]
    bookDir = os.path.join(dataDir, bookName)
    if (   not os.path.exists(bookDir)     # Directory doesn't exist
        or len(os.listdir(bookDir)) == 0   # Empty directory 
       ):
      missingBooks.append(bookName)
      
  #Return a list of all missing books
  return missingBooks


#----------------------------------------------------------------------------------------------
# Start the main program

# Get the alphabetical listing page
bookListHtml = getPage(indexURL)
#writeStringToFile("booklist.html", bookListHtml) # DEBUG
#bookListHtml = open("booklist.html", 'r').read() # DEBUG


#Parse out the links to each book
bookList = booklistParser()
bookList.parse(bookListHtml)
wwwBooks = bookList.getLinks()

#Ensure the data dir exists
ensure_dir(chapDir)

#Get the list of books we currently have in stock
missingBooks = getMissingBooks(wwwBooks, chapDir)
while len(missingBooks) > 0 :
  bookIndex = random.randint(0, (len(missingBooks)-1))
  bookName = missingBooks[bookIndex]
  bookURL = ""
  for book in wwwBooks:
    if bookName == book[1]:
      bookURL = book[0]
  #Get the book data
  getChapters(bookName, bookURL)
  print "Finished getting chapters for "+bookName+"\n"
  missingBooks = getMissingBooks(wwwBooks, chapDir)
  #break #DEBUG, only do one pass



