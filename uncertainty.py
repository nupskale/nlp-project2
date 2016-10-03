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

"""
--------------------------------------------------------------------------------
MODEL
--------------------------------------------------------------------------------
"""

"""
Idea: keep track of words that come immediately before and after a given word
                    B: if w1/POS has B-cue, these are the words that immediately precede w1
          before  { I: if w1/POS has I-cue, these are the words that immediately precede w1
                    O: if w1/POS has O-cue, these are the words that immediately precede w1
w1/POS  {
                    B: if w1/POS has B-cue, these are the words that immediately follow w1
          after   { I: if w1/POS has I-cue, these are the words that immediately follow w1
                    O: if w1/POS has O-cue, these are the words that immediately follow w1

So we look at a word and it's pos, we'll access this dictionary that's developed in training
For example, if we're given the word "likely / JJ", and the dictionary looks something like this:
d["likely JJ"]["before"]["B"] = ""
d["likely JJ"]["before"]["I"] = "most", "very", "is"
d["likely JJ"]["before"]["O"] = "so"
d["likely JJ"]["after"]["B"] = "that"
d["likely JJ"]["after"]["I"] = "that", "more"
d["likely JJ"]["after"]["O"] = "."
and we have a sentence:
"It is likely that it is not true."
B-count would be 1, I-count would be 2, and O-count would be 0.
We see we hve the highest counts for "I", so likely would be given the I-cue.
"""

# training
train_dict = {}
for filename in listdir(newpath):
  file = open(newpath + "/" + filename, "r")
  lines = file.readlines()
  for i in range(len(lines)):
    line = lines[i]
    word = line.split()[0] + " " + line.split()[1]
    tag = line.split()[2][0]

    if word not in train_dict:
      train_dict[word] = {}
      train_dict[word]["before"] = {"B": [], "I": [], "O": []}
      train_dict[word]["after"] = {"B": [], "I": [], "O": []}

    if i > 0:
      train_dict[word]["before"][tag].append(lines[i-1].split()[0])
    else:
      train_dict[word]["before"][tag].append("")

    if i < len(lines) - 1:
      train_dict[word]["after"][tag].append(lines[i+1].split()[0])
    else:
      train_dict[word]["after"][tag].append("")

    # not sure if we should remove duplicates
    # # remove duplicates
    # list(set(train_dict[word]["before"][tag]))
    # list(set(train_dict[word]["after"][tag]))

# sequence tagger
def tagLines(path):
  test = {}
  for filename in listdir(path):
    file = open(path + "/" + filename, "r")
    test[filename] = {}
    lines = file.readlines()
    for i in range(len(lines)):
      line = lines[i]
      # check if newline
      if line != "\n":
        word = line.split()[0] + " " + line.split()[1]

        if word in train_dict:
          before_words = train_dict[word]["before"]
          after_words = train_dict[word]["after"]

          if i > 0 and lines[i-1] != "\n":
            preceding = lines[i-1].split()[0]
          else:
            preceding = ""
          if i < len(lines) - 2 and lines[i+1] != "\n":
            following = lines[i+1].split()[0]
          else:
            following = ""

          b_count = before_words["B"].count(preceding) + after_words["B"].count(following)
          i_count = before_words["I"].count(preceding) + after_words["I"].count(following)
          o_count = before_words["O"].count(preceding) + after_words["O"].count(following)

          if b_count > i_count:
            tag = "B"
          elif b_count > o_count:
            tag = "B"
          elif i_count > o_count:
            tag = "I"
          else:
            tag = "O"

        else:
          # todo: handle unknown words
          # print word + " not in train_dict... giving it tag O"
          tag = "O"

      test[filename][i] = tag

    # to see all counts, uncomment below line
    # print(filename + "\t|\t" + str(test[filename].values().count("B")) + "\t|\t" + str(test[filename].values().count("I")) + "\t|\t" + str(test[filename].values().count("O")))

path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"
# uncomment below line plus the last line in the tagLines function to see a table of BIO counts
# print("filename\t|\tB\t|\tI\t|\tO")
test_private = tagLines(path_private)
test_public = tagLines(path_public)
