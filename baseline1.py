from os import listdir
import accuracy_metrics as am

"""
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

def getWordAndTransitionProbabilities(path, testing_lst = []):
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
      pos = line.split()[1].lower()
      word = word + " " + pos
      tag = line.split()[2][0].lower()

      # get previous
      if i != 0:
        prev_line = lines[i-1].split()
        # prev_word = prev_line[0].lower()
        # prev_pos = prev_line[1].lower()
        prev_tag = prev_line[2][0].lower()
      else:
        # prev_word = ""
        # prev_pos = ""
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
#P(t1...tn | w1...wn) = multiply, from 1 to n, P(ti | ti-1) * P(wi | ti)
we essentially want to see which probability is highest for the three possible tn values: "B", "I", and "O"
"""
def computeTagProbabilities(assigned_tags, w_prob, t_prob, currProb, line, i):
  # check for index out of range (meaning first word), or stop if line[i] is end of sentence
  while (i >= 0 and line[i] != "\n"):
    word = line[i].split()[0].lower()
    pos = line[i].split()[1].lower()
    word = word + " " + pos
    if word in w_prob:
      if i > 0 and line[i-1] != "\n":
        prev_tag = assigned_tags[i-1]
      else:
        prev_tag = ""
      for tag in ["b", "i", "o"]:
        currProb[tag] *= w_prob[word][tag] * t_prob[tag][prev_tag]
      if currProb["b"] >= currProb["i"]:
        assigned_tags[i] = "b"
      # we do not want an "i" tag if "o" tag precedes it
      elif currProb["i"] >= currProb["o"] and assigned_tags[i-1] != "o":
        assigned_tags[i] = "i"
      else:
        assigned_tags[i] = "o"
    else:
      # TODO: handle unknown words
      assigned_tags[i] = "o"
    i -= 1
  return assigned_tags, currProb


def tagLines(w_prob, t_prob, path, testing_lst = []):
  test = {}
  # allows for testing purposes
  if testing_lst == []:
    testing_lst = listdir(path)
  for filename in testing_lst:
    test[filename] = {}
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    file.close()
    currProb = {"b": 1, "i": 1, "o": 1}
    for i in range(len(lines)):
      line = lines[i]
      # check if newline
      if line == "\n":
        currProb = {"b": 1, "i": 1, "o": 1}
      else:
        test[filename], currProb = computeTagProbabilities(test[filename], w_prob, t_prob, currProb, lines, i)
  return test

# path variables
train_path = "nlp_project2_uncertainty/train_modified"
path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"

# test the accuracy
print("Testing accuracy...")
test_path_list = listdir(train_path)
training_files = test_path_list[:len(test_path_list) * 3 / 4]
testing_files = test_path_list[len(test_path_list) * 3 / 4:]
test_w_prob, test_t_prob = getWordAndTransitionProbabilities(train_path, training_files)
test_tags = tagLines(test_w_prob, test_t_prob, train_path, testing_files)
print("Precision for all tags: " + str(am.precision(train_path, test_tags)))
print("Precision for B tags: " + str(am.precision(train_path, test_tags, "b")))
print("Precision for I tags: " + str(am.precision(train_path, test_tags, "i")))
print("Precision for O tags: " + str(am.precision(train_path, test_tags, "o")))

# do the tagging
w_prob, t_prob = getWordAndTransitionProbabilities(train_path)
private_tags = tagLines(w_prob, t_prob, path_private)
public_tags = tagLines(w_prob, t_prob, path_public)