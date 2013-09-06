# Get chapters for books from the web
import sgmllib, os, re
from db_functions import *
from book_functions import *



# ------- Calculate and generate the path names for the books (stripped) -----------
bookDir = "isilo_group_html"
books = dbQuery("select id, name from book")
for bookRow in books:
  bookId = str(bookRow[0])
  bookName = bookRow[1]

  # See if the book exists in the file system
  bookNameClean = cleanFileName(bookName)
  if not os.path.exists(os.path.join(bookDir, bookNameClean)):
    print "ERROR! Missing book :"+bookName
  else:
    # If all is well, then we'll update the database with the clean book name
    print "Updating "+bookNameClean
    db.query("update book set path_name='"+bookNameClean+"' where id="+bookId)



