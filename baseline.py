from os import listdir
from csv import writer

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
path = "nlp_project2_uncertainty/train_modified"
train_dict = {}
for filename in listdir(path):
  file = open(path + "/" + filename, "r")
  lines = file.readlines()
  for i in range(len(lines)):
    line = lines[i]
    word = line.split()[0] + " " + line.split()[1]
    word = word
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
  return test

path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"
# uncomment below line plus the last line in the tagLines function to see a table of BIO counts
# print("filename\t|\tB\t|\tI\t|\tO")
test_private = tagLines(path_private)
test_public = tagLines(path_public)

# # make sure id counts are correct
# private_sum = 0
# for key in test_private.keys():
#   private_sum = private_sum + len(test_private[key])
# print "Private sum should be 55664, got " + str(private_sum)
# public_sum = 0
# for key in test_public.keys():
#   public_sum = public_sum + len(test_public[key])
# print "Public sum should be 55759, got " + str(public_sum)

# Kaggle submission
def phraseDetectorString(test):
  cues = ""
  cum_index_count = 0
  for filename in test.keys():
    file_cues = test[filename]
    for index in file_cues.keys():
      cue = file_cues[index]
      # we only add cues indices in these cases:
      # cue is B
      if cue == "B":
        # if I is not the next cue, index-index
        if (index + 1) in file_cues and file_cues[index + 1] != "I":
          index += cum_index_count
          cues += str(index) + "-" + str(index) + " "
        # next cue is I
        elif (index + 1) in file_cues and file_cues[index + 1] =="I":
          index += cum_index_count
          cues += str(index) + "-"
      # cue is I
      elif cue == "I":
        # previous cue was B or I
        if (index - 1) in file_cues and (file_cues[index - 1] == "B" or file_cues[index - 1] == "I"):
          # next cue is not I
          if (index + 1) in file_cues and (file_cues[index + 1] != "I"):
            index += cum_index_count
            cues += str(index) + " "
    cum_index_count += len(file_cues)
  return cues

def sentenceDetectorString(test, path):
  indices = ""
  cum_sentence_count = 0
  for filename in test.keys():
    file_cues = test[filename]
    sentences = open(path + "/" + filename, "r").readlines()
    foundCue = False
    for i in range(len(sentences)):
      word = sentences[i]
      if word == "\n":
        if foundCue:
          cum_sentence_count += 1
          indices += str(cum_sentence_count) + " "
          foundCue = False
      elif test[filename][i] == "B":
        foundCue = True
  return indices

with open("uncertain_phrase_detection.csv", 'w') as file:
  w = writer(file)
  w.writerow(["Type", "Spans"])
  w.writerow(["CUE-public", phraseDetectorString(test_public)])
  w.writerow(["CUE-private", phraseDetectorString(test_private)])

with open("uncertain_sentence_detection.csv", "w") as file:
  w = writer(file)
  w.writerow(["Type", "Indices"])
  w.writerow(["SENTENCE-public", sentenceDetectorString(test_public, "nlp_project2_uncertainty/test-public")])
  w.writerow(["SENTENCE-private", sentenceDetectorString(test_private, "nlp_project2_uncertainty/test-private")])
