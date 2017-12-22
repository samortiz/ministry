#! /usr/bin/env python
# Go through the books and create iSilo compatible HTML
import os, time, shutil

#File Variables
htmlDir = 'clean_html'
isiloDir = 'isilo_separate_html'
projectBooksDir = '/home/sortiz/project/ministry/books'

# ---------------------- Misc Functions --------------------------------

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


# -----------------------------------------------------------------------
# Main functions

# Clean up file names
def cleanFileName(rawFileName):
  cleanFileName = ""
  
  # Loop through and copy each character (except funny ones)
  for char in rawFileName :
    cnum = ord(char)
    if cnum == 32 or cnum == 45: # space or hyphen
      cleanFileName += "_"  
    elif cnum >= 48 and cnum <= 57 : # digit 0-9
      cleanFileName += char
    elif ((cnum >= 65 and cnum <= 90) # uppercase
          or (cnum >= 97 and cnum <= 122)) : # lowercase
      cleanFileName += char
      
  return cleanFileName
  

# Clean up various problems in the HTML
def cleanupHtml(rawHtml):
  # Convert funny quotes to HTML entities
  html = rawHtml.replace('\xe2\x80\x9c', '&#8220;')  # Left double quote
  html = html.replace('\xe2\x80\x9d', '&#8221;')  # Right double quote
  html = html.replace('\xe2\x80\xa6', '...')  # ellipsis
  html = html.replace('\xe2\x80\x98', '&#8216;')  # left single quote
  html = html.replace('\xe2\x80\x99', '&#8217;')  # Right single quote
  html = html.replace('\xe2\x80\x94', '-') # some kind of hyphen
  html = html.replace('\xe2\x80\x93', '-') # some kind of hyphen
  html = html.replace('\xc3\xbc', 'u')  # u with double dots above it
  html = html.replace('\xe2\x80\xa2', '-') # Funny centered dot (bullet)
  html = html.replace('\xc3\xa0', '&#224;') # a with accent
  html = html.replace('\xc3\xa9', '&#233;') # e with an up accent
  html = html.replace('\xc3\xa8', '&#232;') # e with a down accent
  html = html.replace('\xc3\xa7', '&#231;') # c with a hook under it
  html = html.replace('\xc2\xa0', ' ') # maybe whitespace?
  html = html.replace('\xc2\xbc', ' ') # weird fraction
  html = html.replace('\xc2\xbd', ' ') # weird fraction
  html = html.replace('\xc2\xbe', ' ') # weird fraction
  html = html.replace('\xc2\xad', ' ') # whitespace maybe?
#  html = html.replace('\x\x\x', '&#;') #
 
  # There are many tables with width set to 70, especially on the first page with the index of chapters
  # This is a real waste of space, especially on the palm and looks silly, so I'm removing here
  html = html.replace('width="70%"', 'width="100%"')
    
  # Go through all the characters, see if there are any error-characters
  count = 0
  for char in html:
    if ord(char) > 127:
      print "Found Invalid Char at "+str(count-113)
      print "Hex : %2x %2x %2x " % (ord(char), ord(html[count+1]), ord(html[count+2]) )
      print "Context : "+html[count-10:count+10]
      os._exit(1)
    count += 1
  
  return html
  
  

# Takes an HTML page and produces an iSilo page out of it
def createIsiloPage(bookName, pageNum, lastPageNum, html):
  print "    "+str(pageNum)+" of "+str(lastPageNum)
  #Create the output directory if necessary
  outputDir = os.path.join(isiloDir, bookName)
  ensure_dir(outputDir)

  cleanHtml = cleanupHtml(html)
  navHtml = ""
  
  # Generate the navigation HTML (header and footer, next/prev links)  
  if pageNum > 1:  
    navHtml += '<a href="./page_001.html"> Home </a> ' # Home defaults to the first page
    navHtml += '| <a href="./page_'+str(pageNum-1).rjust(3,"0")+'.html">Prev</a> '
  else: 
    navHtml += 'Home | Prev '
      
  if pageNum < lastPageNum:
    navHtml += '| <a href="page_'+str(pageNum+1).rjust(3,"0")+'.html">Next</a> '
  else:
    navHtml += '| Next '

  # Generate the main HTML (add the navigation to the content)
  isiloHtml = '<html><head><link rel="stylesheet" type="text/css" href="book_styles.css" /></head><body>'
  isiloHtml += navHtml + '<br>'
  isiloHtml += cleanHtml + '<br>'
  isiloHtml += navHtml 
  isiloHtml += '</body></html>'

  #Write out the output file for this page
  pageFileName = "page_"+str(pageNum).rjust(3,"0")+".html"
  writeStringToFile(os.path.join(outputDir, pageFileName), isiloHtml)
  



#----------------------------------------------------------------------------------------------
# Start the main program

iSiloControlStr = """
?xml version="1.0"?>
<iSiloXDocumentList>
"""

todaysDate = time.strftime("%b %d, %Y %H:%M.%S", time.localtime())
currentFirstLetter = ""

books = os.listdir(htmlDir)
books = sorted(books, key=str.lower)
#books = books[1:50] #DEBUG
for bookRaw in books:
  book = cleanFileName(bookRaw)
  print "Generating iSilo html for book : "+bookRaw+" as "+book
  
  #Create directory for the target pdb (sort each book by first letter for easier navigation)
  firstLetter = book[0].upper()
  ensure_dir("isilo_pdb/books/"+firstLetter)
  
  #Control path (list of pages)
  iSiloPagePaths = ""
  
  #Get the pages for the book
  bookPath = os.path.join(htmlDir, bookRaw)
  pages = os.listdir(bookPath)
  pages.sort()
  lastPageNum = pages[len(pages)-1][5:8]
  
  #Produce iSilo Html for each page of the book
  for page in pages :
    if page == "page_001.html":
      tocFile = os.path.join("chap_html",bookRaw, "toc_with_links.html")
      if os.path.exists(tocFile):
        html = open(tocFile).read()
      else:
        html = open(os.path.join(bookPath, page), "r").read()
    else:
      html = open(os.path.join(bookPath, page), "r").read()
    pageNum = page[5:8]
    createIsiloPage(book, int(pageNum), int(lastPageNum), html)
    iSiloPagePaths += "<Path>"+projectBooksDir+"/"+isiloDir+"/"+book+"/"+page+"</Path>\n"


  #Copy the extra data files
  htmlExtras = os.listdir("html_extras")
  for extraFile in htmlExtras:
    if not os.path.exists(os.path.join(isiloDir, book, extraFile)):
      shutil.copy2(os.path.join("html_extras", extraFile), os.path.join(isiloDir, book, extraFile))


  #Produce the iSilo control file for this book
  iSiloControlStr += """
 <iSiloXDocument>
    <Source>
      <Sources>
        """+iSiloPagePaths+"""
      </Sources>
    </Source>
    <Destination>
      <Title>"""+bookRaw+"""</Title>
      <Files>
        <Path>"""+projectBooksDir+"""/isilo_pdb/books/"""+firstLetter+"""/"""+book+""".pdb</Path>
      </Files>
    </Destination>
    
    <LinkOptions>
      <FollowOffsite            value="no"/>
      <MaximumOffsiteDepth      value="0"/>
    </LinkOptions>

    <LastConversion>
      <Date>"""+todaysDate+"""</Date>
    </LastConversion>
  
    <Messages>
      <Title>Ministry Books</Title>
      <Version>"""+todaysDate+"""</Version>
    </Messages>
    
  </iSiloXDocument>
"""  
 # print iSiloPagePaths
  print "" #A blank line between each book


#Generate the final String
iSiloControlStr += "</iSiloXDocumentList>"

# Generate the control file
writeStringToFile("isilo_separate.ixl", iSiloControlStr)

