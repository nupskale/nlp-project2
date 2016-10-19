from os import listdir
import accuracy_metrics as am

"""
THE LOGIC:
P(t1,...,tn | w1,...,wn)

  P(t1,...,tn) * P(w1,...,wn | t1,...,tn)
= ---------------------------------------
  P(w1,...,wn)


approximate using bigram model:
from i to n, multiply:
P(ti | ti-1) * P(wi | ti)

where P(ti | ti-1) is the transition probability
and P(wi | ti) is the lexical generation probability
"""

"""
returns:
  w_prob: dictionary of P(w_i | t_i) where w_i is a word, and t_i is the tag for w_i
          access these values by calling w_prob[word][tag]
  t_prob: dictionary of P(t_i | t_i-1) where t_i is a tag, and t_(i-1) is the tag that comes immediately before t_i
          access these values by calling t_prob[tag][prev_tag]
arguments:
  path: this should always be the training path
  testing_list: an optional argument. The default is the empty list, so if you just call getWordTransitionProbabilities(path),
                the file list that will be iterated over will be the files in the path.
                This option is available for testing accuracy; meaning, you can iterate over a different file list. Just provide
                a list of these file names (and the path has to match the filename, meaning: path + "/" + testing_lst[i] will return a valid file)
  usePos: another optional argument. The default is true, meaning the w_i token in the probabilities will incorporate the word and the part of speech
          if you do not want to include part of speech and only use the word, then call getWordTransitionProbabilities(path, usePos = False)
          else, call getWordTransitionProbabilities(path)
"""
def getWordAndTransitionProbabilities(path, testing_lst = [], usePos = True):
  # get counts of transitions and of words
  w_count = {}
  t_count = {"b": {"b": 0, "i": 0, "o": 0, "": 0}, "i": {"b": 0, "i": 0, "o": 0, "": 0}, "o": {"b": 0, "i": 0, "o": 0, "": 0}}
  if testing_lst == []:
    testing_lst = listdir(path)
  for filename in testing_lst:
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    for i in range(len(lines)):
      line = lines[i]
      word = line.split()[0].lower()
      if usePos:
        pos = line.split()[1].lower()
        word = word + " " + pos
      tag = line.split()[2][0].lower()

      # get previous
      if i != 0:
        prev_line = lines[i-1].split()
        prev_tag = prev_line[2][0].lower()
      else:
        prev_tag = ""
      
      if not word in w_count:
        w_count[word] = {}
        w_count[word]["b"] = 0
        w_count[word]["i"] = 0
        w_count[word]["o"] = 0

      w_count[word][tag] += 1
      t_count[tag][prev_tag] += 1

  # w_prob[wi][ti] is P(wi | ti)
  w_prob = {}
  for k in w_count.keys():
    w_prob[k] = {}
    for v in w_count[k].keys():
      # bigram: P(x|y) = count(y x) / count(y) 
      w_prob[k][v] = float(w_count[k][v]) / sum(w_count[k].values())
  # t_prob[ti][ti-1] is P(ti | ti-1)
  t_prob = {}
  for k in t_count.keys():
    t_prob[k] = {}
    for v in t_count[k].keys():
      t_prob[k][v] = float(t_count[k][v]) / sum(t_count[k].values())

  return w_prob, t_prob

"""
A Helper Function
We essentially want to see which probability is highest for the three possible tn values: "B", "I", and "O"
"""
def computeTagProbabilities(assigned_tags, w_prob, t_prob, line, i, usePos = True):
  # check for index out of range (meaning first word), or stop if line[i] is end of sentence
  while (i >= 0 and line[i] != "\n"):
    word = line[i].split()[0].lower()
    if usePos:
      pos = line[i].split()[1].lower()
      word = word + " " + pos
    currProb = {}
    if word in w_prob:
      if i > 0 and line[i-1] != "\n":
        prev_tag = assigned_tags[i-1]
      else:
        prev_tag = ""
      for tag in ["b", "i", "o"]:
        currProb[tag] = w_prob[word][tag] * t_prob[tag][prev_tag]
      # find the max value, and check that no values are equal to each other...
      if currProb["b"] != currProb["i"] or currProb["b"] != currProb["o"] or currProb["i"] != currProb["o"]:
        assigned_tags[i] = max(currProb, key=currProb.get)
      else:
        # # I saw some cases where w_prob[word][tag] = 1 for a certain tag, but t_prob[tag][prev_tag] = 0
        # # So this is a test to see if only using w_prob would improve accuracy metrics
        for tag in ["b", "i", "o"]:
          currProb[tag] = w_prob[word][tag]
        if currProb["b"] != currProb["i"] or currProb["b"] != currProb["o"] or currProb["i"] != currProb["o"]:
          assigned_tags[i] = max(currProb, key=currProb.get)
        else:
          for tag in ["b", "i", "o"]:
            currProb[tag] = t_prob[tag][prev_tag]
          if currProb["b"] != currProb["i"] or currProb["b"] != currProb["o"] or currProb["i"] != currProb["o"]:
            assigned_tags[i] = max(currProb, key=currProb.get)
          # last case, all probabilities are equal... (don't see this as being very likely to happen)
          else:
            assigned_tags[i] = ""
    else:
      # TODO: handle unknown words
      assigned_tags[i] = ""
    i -= 1
  return assigned_tags

"""
Tag the lines!
returns:
  test: a nested dictionary where the first layer is a dictionary where the keys are filenames and the values
        are a dictionary. This second layer dictionary has the keys equal to the index of the line, and the value
        is the tag
arguments:
  w_prob: word probability
  t_prob: transition probability (tag probability)
  path: filepath used to determine which files to tag
  testing_lst: optional argument, used for testing if testing_lst != []
  usePos: tells the function if we want to use part of speech AND word, or just word
"""
def tagLines(w_prob, t_prob, path, testing_lst = [], usePos = True):
  test = {}
  # allows for testing purposes
  if testing_lst == []:
    testing_lst = listdir(path)
  for filename in testing_lst:
    test[filename] = {}
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    file.close()
    for i in range(len(lines)):
      line = lines[i]
      # check if newline
      if line != "\n":
        test[filename] = computeTagProbabilities(test[filename], w_prob, t_prob, lines, i, usePos)
  return test

# path variables
train_path = "nlp_project2_uncertainty/train_modified"
path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"

# USING WORD + POS

# test the accuracy
print("Testing accuracy for word + pos...")
test_path_list = listdir(train_path)
training_files = test_path_list[:len(test_path_list) * 3 / 4]
testing_files = test_path_list[len(test_path_list) * 3 / 4:]
test_w_prob, test_t_prob = getWordAndTransitionProbabilities(train_path, training_files)
test_tags = tagLines(test_w_prob, test_t_prob, train_path, testing_files)
print("Precision for B tags: " + str(am.precision(train_path, test_tags, "b")))
print("Precision for I tags: " + str(am.precision(train_path, test_tags, "i")))
print("Precision for O tags: " + str(am.precision(train_path, test_tags, "o")))

p = am.precision(train_path, test_tags)
print("Precision for all tags: " + str(p))
r = am.recall(train_path, test_tags)
print("Recall for all tags: " + str(r))
print("F-measure for all tags: " + str(am.fMeasure(p, r)))

# # do the tagging
# w_prob, t_prob = getWordAndTransitionProbabilities(train_path)
# private_tags = tagLines(w_prob, t_prob, path_private)
# public_tags = tagLines(w_prob, t_prob, path_public)

# USING ONLY WORD

# test the accuracy
print("Testing accuracy for word (not pos)...")
test_path_list = listdir(train_path)
training_files = test_path_list[:len(test_path_list) * 3 / 4]
testing_files = test_path_list[len(test_path_list) * 3 / 4:]
test_w_prob, test_t_prob = getWordAndTransitionProbabilities(train_path, training_files, False)
test_tags = tagLines(test_w_prob, test_t_prob, train_path, testing_files, False)
print("Precision for B tags: " + str(am.precision(train_path, test_tags, "b")))
print("Precision for I tags: " + str(am.precision(train_path, test_tags, "i")))
print("Precision for O tags: " + str(am.precision(train_path, test_tags, "o")))

p = am.precision(train_path, test_tags)
print("Precision for all tags: " + str(p))
r = am.recall(train_path, test_tags)
print("Recall for all tags: " + str(r))
print("F-measure for all tags: " + str(am.fMeasure(p, r)))

# # do the tagging
# w_prob, t_prob = getWordAndTransitionProbabilities(train_path, [], False)
# private_tags = tagLines(w_prob, t_prob, path_private, [], False)
# public_tags = tagLines(w_prob, t_prob, path_public, [], False)
