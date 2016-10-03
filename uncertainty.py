import os
from os import listdir
import shutil

"""
--------------------------------------------------------------------------------
PREPROCESSING
--------------------------------------------------------------------------------
"""

path = "nlp_project2_uncertainty/train"
newpath = "nlp_project2_uncertainty/train_modified"

#create directory to store BIO tagged training files
if not os.path.exists(newpath):
  os.makedirs(newpath)
else:
  shutil.rmtree(newpath)
  #removes all the subdirectories
  os.makedirs(newpath)

#preprocess files to remove blank lines
for filename in listdir(path):
  with open(path+"/"+filename) as infile, open(newpath+"/"+filename, 'w') as outfile:
    for line in infile:
      if not line.strip(): 
        continue
        # skip the empty line
      else:
        outfile.write(line)
        # non-empty line. Write it to output

#replacing cue phrases with BI and other words with O
#new folder created from training data (with BIO tags replacing the CUE tags)
for filename in listdir(newpath):
  file = open(newpath+"/"+filename,"r+")
  linelist = []
  current_line = file.readlines()
  linelist = current_line
  file.seek(0,0)
  for i in range (0, len(linelist)):
    third_column = linelist[i].split()[2]
    prev_third_column = linelist[i-1].split()[2]
    if(i<len(linelist)-1):
      next_third_column = linelist[i+1].split()[2]
    if(third_column == "_"):
      notation = linelist[i].replace("_","O")
      file.write(notation)
      #tags O
    if(third_column != "_" and "_" in prev_third_column):
      notation = linelist[i].replace(third_column, "B-CUE")      
      file.write(notation)
      #tags B
    if(third_column!="_" and "CUE-" in prev_third_column):
      notation = linelist[i].replace(third_column, "I-CUE")      
      file.write(notation)
      #tags I
