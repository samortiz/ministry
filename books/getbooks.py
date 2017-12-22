# Get books from the web

import urllib, urllib2, cookielib, sgmllib
import os, random, time


#URL Variables
indexURL = 'https://www.ministrybooks.org/alphabetical.cfm?all'
bookURLBase = 'http://www.ministrybooks.org/'
nextPageURL = 'http://www.ministrybooks.org/books.cfm?n'

#File Variables
dataDir = 'raw_html'

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


# -----------------------------------------------------------------------------------------
# Gets a book, specified by it's name and URL 
# URL should be in the format given in the href component of the A tag on the alphabet page (books.cfm?id=...)
def getBook (bookName, URL):
  print "Downloading the book "+bookName+" with URL="+URL

  # Setup the directory for the book data
  bookPath = os.path.join(dataDir, bookName)
  ensure_dir(bookPath)
  
  # Get the first page of the book
  firstPageHtml = getPage(bookURLBase+URL)
  writeStringToFile(os.path.join(bookPath, "page_001.html"), firstPageHtml)
  
  # Check to see if there are more pages
  nextPortionStr = '<a href="books.cfm?n" class="button radius">next'
  # <a href="books.cfm?n" class="button radius">next chapter <i class="fa fa-caret-right" aria-hidden="true"></i></a>
  # <a href="books.cfm?n" class="button radius">next section <i class="fa fa-caret-right" aria-hidden="true"></i></a>
  pageNum = 1
  pageHtml = firstPageHtml #Stores all the page html data
  while pageHtml.find(nextPortionStr) > 0: 
    pageNum += 1
    pageHtml = getPage(nextPageURL)
    pageFileName = "page_"+str(pageNum).rjust(3,"0")+".html"
    pagePath = os.path.join(bookPath, pageFileName)
    writeStringToFile(pagePath, pageHtml)
    print "Downloaded "+bookName+" Page "+pageFileName
    time.sleep(random.randint(1,2)) # Pause between page loads to go easy on their server
  
  #The download completed successfully (we assume!)
  #Write out the sucess file (so we know the download wasn't aborted before it finished)
  finishedStr = "<pagecount>"+str(pageNum).rjust(3,"0")+"</pagecount>"
  writeStringToFile(os.path.join(bookPath, "download_data.txt"), finishedStr)


#Cuts a string from the first startStr to the first endStr and returns it
# Note: this also strips off whitespace from the final string
def cutStr(sourceStr, startStr, endStr):
  startCutIndex = sourceStr.find(startStr) + len(startStr)
  endCutIndex = sourceStr.find(endStr)
  return sourceStr[startCutIndex:endCutIndex].strip()


#Returns a list of all the books missing from the data set, given a master list (the www books are all the books on the web site)
def getMissingBooks(wwwBooks):
  missingBooks = []
  #Directory containing all the books downloaded so far
  currentBooks = os.listdir(dataDir)
  for book in wwwBooks:
    bookURL = book[0]
    bookName = book[1]
    if not os.path.exists(os.path.join(dataDir, bookName, "download_data.txt")):
      missingBooks.append(bookName)
      
  #Return a list of all missing books
  return missingBooks


#----------------------------------------------------------------------------------------------
# Start the main program

# Get the alphabetical listing page
bookListHtml = getPage(indexURL)
writeStringToFile("booklist.html", bookListHtml)
#bookListHtml = open("booklist.html", 'r').read()

#Parse out the links to each book
bookList = booklistParser()
bookList.parse(bookListHtml)
wwwBooks = bookList.getLinks()

#Ensure the data dir exists
ensure_dir(dataDir)

#Get the list of books we currently have in stock
missingBooks = getMissingBooks(wwwBooks)

print 'missing '+ str(len(missingBooks))
print missingBooks

#missingBooks = [] #DEBUG below
while len(missingBooks) > 0 :
  bookIndex = random.randint(0, (len(missingBooks)-1))
  bookName = missingBooks[bookIndex]
  bookURL = ""
  for book in wwwBooks:
    if bookName == book[1]:
      bookURL = book[0]
  #Get the book data
  getBook(bookName, bookURL)
  print "Finished downloading "+bookName+"\n"
  missingBooks = getMissingBooks(wwwBooks)

# DEBUG - force the book (so we're not jumping around to different books)
#bookName = "Mystery of Human Life, The"
#for book in wwwBooks:
#  if bookName == book[1]:
#    bookURL = book[0]
#getBook(bookName, bookURL)



