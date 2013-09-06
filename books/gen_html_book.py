# Generate html files, one file for each book 
import os, random, time
from book_functions import *


#File Variables
cleanDir = 'clean_html'
htmlBooksDir = 'html_books'

#----------------------------------------------------------------------------------------------
# Start the main program

# Make sure the target directory exists
# note : make sure the book_styles.css exists in this directory as well
ensure_dir(htmlBooksDir)

# Directory containing all the books downloaded so far
currentBooks = os.listdir(cleanDir)
currentBooks.sort()
#currentBooks = currentBooks[300:]
for book in currentBooks:
  html = '<html><head><link rel="stylesheet" type="text/css" href="book_styles.css" /></head><body>'
  bookPath = os.path.join(cleanDir, book)
  pages = os.listdir(bookPath)
  pages.sort()
  lastPageNum = pages[len(pages)-1][5:8]

  #Get the html for each page of the book
  for page in pages :
    pageHtml = open(os.path.join(bookPath, page), "r").read()

    # Add the book title if it's the first page
    if page == "page_001.html":
      # If the title is already at the top, don't duplicate it
      bookTitle = cleanFileName(book).lower()
      if bookTitle.endswith("_the"):
        bookTitle = bookTitle[:len(bookTitle)-4]
      # Find the position of the book title in the string
      titlePos = cleanFileName(pageHtml.replace("&rsquo;","'")).lower().find(bookTitle)
      #cleanHtml = "pos="+str(titlePos)+" bookTitle="+bookTitle+"<br>"+cleanFileName(html)
      if  titlePos == -1 or titlePos > 100 :
        pageHtml = "<div style='text-align:center; font-weight:bold'>"+bookDisplayName(book)+"</div>"+pageHtml

    html += cleanupHtml(pageHtml)

  html += '</body></html>'
  htmlFilename = os.path.join(htmlBooksDir, cleanFileName(book)+".html")
  writeStringToFile(htmlFilename, html)  
  print "Wrote file "+htmlFilename
 











