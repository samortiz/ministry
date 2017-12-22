#! /usr/bin/env python
# Go through the books and create iSilo compatible HTML
import os, time, shutil
from book_functions import *

#File Variables
htmlDir = 'clean_html'
chapDir = 'chap_html'
isiloDir = 'isilo_group_html'
projectBooksDir = '/home/sortiz/project/ministry/books'


# Takes an HTML page and produces an iSilo page out of it
def createIsiloPage(bookName, rawBookName, pageNum, lastPageNum, html):
  #print "    "+str(pageNum)+" of "+str(lastPageNum)
  #Create the output directory if necessary
  outputDir = os.path.join(isiloDir, bookName)
  ensure_dir(outputDir)

  cleanHtml = cleanupHtml(html)
  # There are many tables with width set to 70, especially on the first page with the index of chapters
  # This is a real waste of space, especially on the palm and looks silly, so I'm removing them here
  cleanHtml = cleanHtml.replace('width="70%"', 'width="100%"')

  # Generate the navigation HTML (header and footer, next/prev links)  
  navHtml = '<a href="../index.html"> Home </a> ' # Home goes to the book index
  if pageNum > 1: 
    navHtml += '| <a href="page_001.html"> First </a> ' # First page
    navHtml += '| <a href="page_'+str(pageNum-1).rjust(3,"0")+'.html">Prev</a> '
  else:
    navHtml += '| First | Prev '
      
  if pageNum < lastPageNum:
    navHtml += '| <a href="page_'+str(pageNum+1).rjust(3,"0")+'.html">Next</a> '
  else: 
    navHtml += '| Next '

  # Add the book title if it's the first page
  if pageNum == 1:
    # If the title is already at the top, don't duplicate it
    bookTitle = cleanFileName(rawBookName).lower()
    if bookTitle.endswith("_the"):
      bookTitle = bookTitle[:len(bookTitle)-4]
    # Find the position of the book title in the string
    titlePos = cleanFileName(html.replace("&rsquo;","'")).lower().find(bookTitle)
    #cleanHtml = "pos="+str(titlePos)+" bookTitle="+bookTitle+"<br>"+cleanFileName(html)
    if  titlePos == -1 or titlePos > 100 :
      cleanHtml = "<div style='text-align:center; font-weight:bold'>"+bookDisplayName(rawBookName)+"</div>"+cleanHtml

  # Get a display name
  bookTitle = bookDisplayName(rawBookName)
 
  # Generate the main HTML (add the navigation to the content)
  isiloHtml = '<html><head><link rel="stylesheet" type="text/css" href="../book_styles.css" /></head><body>'
  isiloHtml += navHtml + '<br>'
  isiloHtml += cleanHtml + '<br>'
  isiloHtml += navHtml
  isiloHtml += "<div style='text-align:center'>"+bookTitle+" &nbsp; pg "+str(pageNum)+"</div>"
  isiloHtml += "<br>"
  isiloHtml += '</body></html>'

  #Write out the output file for this page
  pageFileName = "page_"+str(pageNum).rjust(3,"0")+".html"
  writeStringToFile(os.path.join(outputDir, pageFileName), isiloHtml)
  



#----------------------------------------------------------------------------------------------
# Start the main program

iSiloControlStr = """<?xml version="1.0"?>
<iSiloXDocumentList>
 <iSiloXDocument>
    <Source>
      <Sources>
      <Path>"""+projectBooksDir+"""/"""+isiloDir+"""/index.html</Path>
"""

# Contents of the index.html file, containing links to all the books
indexHtmlStr = """
<html>
 <head><link rel="stylesheet" type="text/css" href="book_styles.css" /></head>
<body>
 <a name="top"></a>
 <div style='font-weight:bold; text-align:center; padding-bottom:5px;'>Ministry Books</div>
 <div id='navlinks' style='padding-bottom:8px; text-align:center'><a href="#A">A</a><a href="#B">B</a><a href="#C">C</a><a href="#D">D</a><a href="#E">E</a><a href="#F">F</a><a href="#G">G</a><a href="#H">H</a><a href="#I">I</a><a href="#J">J</a><a href="#K">K</a><a href="#L">L</a><a href="#M">M</a><a href="#N">N</a><a href="#O">O</a><a href="#P">P</a><a href="#Q">Q</a><a href="#R">R</a><a href="#S">S</a><a href="#T">T</a><a href="#U">U</a><a href="#V">V</a><a href="#W">W</a><a href="#Y">Y</a></div>
"""
prevFirstLetter = "1" # We won't add links to 1 (there is only one book)
books = os.listdir(htmlDir)
books = sorted(books, key=str.lower)
#books = books[1:20] #DEBUG

for bookRaw in books:
  book = cleanFileName(bookRaw)
  print "Generating iSilo html for book : "+bookRaw+" as "+book

  #Control path (list of pages)
  iSiloPagePaths = ""
  
  #Get the pages for the book
  bookPath = os.path.join(htmlDir, bookRaw)
  pages = os.listdir(bookPath)
  pages.sort()
  lastPageNum = pages[len(pages)-1][5:8]
  
  # The first letter of the book is used to do internal hyperlinks (# style)
  firstLetter = book[0].upper()
  if firstLetter != prevFirstLetter:
    indexHtmlStr += ('<div style="text-align:center; font-weight:bold; margin-top:4px">'+
      '<a name="'+firstLetter+'" href="#top">'+firstLetter+'</div>')
    prevFirstLetter = firstLetter
  
  #Produce iSilo Html for each page of the book
  for page in pages :
    if page == "page_001.html":
      tocFile = os.path.join(chapDir, bookRaw, "toc_with_links.html")
      if os.path.exists(tocFile):
        html = open(tocFile).read()
      else:
        html = open(os.path.join(bookPath, page), "r").read()
    else:
      html = open(os.path.join(bookPath, page), "r").read()
    pageNum = page[5:8]
    createIsiloPage(book, bookRaw, int(pageNum), int(lastPageNum), html)
    iSiloPagePaths += "<Path>"+projectBooksDir+"/"+isiloDir+"/"+book+"/"+page+"</Path>\n"

  #Add this book to the index.html file
  bookTitleCleaned = bookRaw.replace('\xe2\x80\x94', '-').replace('\xe2\x80\x93', '-') # replace hyphens
  indexHtmlStr += '<a href="'+book+'/page_001.html"><image src="bullet.gif" border=0>'+bookTitleCleaned+'</a><br>'

  #Produce the iSilo control file for this book
  iSiloControlStr += iSiloPagePaths

  #print "" #A blank line between each book

todaysDate = time.strftime("%b %d, %Y %H:%M.%S", time.localtime())

#Generate the final String
iSiloControlStr += """
      </Sources>
    </Source>
    <Destination>
      <Title>Ministry Books</Title>
      <Files>
        <Path>"""+projectBooksDir+"""/isilo_pdb/ministry_books.pdb</Path>
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
</iSiloXDocumentList>
"""

indexHtmlStr += "</body></html>"

# Generate the control file
writeStringToFile("isilo_group.ixl", iSiloControlStr)

#Generate the index page
writeStringToFile(os.path.join(isiloDir, "index.html"), indexHtmlStr)

#Copy the extra data files
htmlExtras = os.listdir("html_extras")
for extraFile in htmlExtras:
  if not os.path.exists(os.path.join(isiloDir, extraFile)):
    shutil.copy2(os.path.join("html_extras", extraFile), os.path.join(isiloDir, extraFile))

