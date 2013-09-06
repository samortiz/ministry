# Helper functions.  This will setup the database connection
import  pg

#Setup the database
db = pg.DB(dbname='ministry', host='localhost', user='www', passwd='your-password-here')

# to query multiple rows and get the results as a 2-D array use 
# db.query(sql).getresult()

def dbGetOne(sql) :
  "Returns a single value from a query (first row, first col) as a string"
  res = db.query(sql).getresult()
  if (len(res) > 0): 
    if (len(res[0]) > 0):
      return str(res[0][0])
  return ""

def dbGetRow(sql) :
  "Returns a single row from a query (first row) as an array. Returns an empty array if no rows are generated"
  res = db.query(sql).getresult()
  if (len(res) > 0): 
    return res[0]
  return []

def dbGetCol(sql) :
  "Returns a single column from a query (first column) as an array. Returns an empty array if no rows are generated"
  res = db.query(sql).getresult()
  if (len(res) == 0):
    return []
  retVal = []
  for row in res:
    if (len(row) > 0):
      retVal.append(row[0])
  return retVal

def dbQuery(sql): 
  "Runs and returns a resultset from a db query"
  res = db.query(sql).getresult()
  return res

def toString(var) :
  "Convert the var to a string, this will truncate floating point numbers, to remove the .0 from the end, trims whitespace"
  retVal = var
  if (type(retVal) == float): retVal = `int(retVal)`
  if (type(retVal) == int): retVal = str(retVal)
  if (retVal == None) : retVal = ""
  retVal = retVal.strip() # Trim whitespace
  return retVal

def toInt(var) :
  "Convert the var to an integer, truncate floating point numbers, convert strings"
  return int(var)

def escape(var):
   return pg.escape_string(var)
