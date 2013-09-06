import os

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

def readFile(fileName):
  return open(fileName, 'r').read()



