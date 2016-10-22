import nltk
import numpy as np
from os import listdir
from nltk.corpus import treebank
from nltk.tag import hmm

def getTrainList(file_list = []):
  path = "nlp_project2_uncertainty/train_modified"
  train_list = []
  if file_list == []:
    file_list = listdir(path)
  for filename in file_list:
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    sentence_list = []
    for line in lines:
      word = line.split()[0]
      if '\\' in word:
        word = word.replace('\\', '')
      word = word.decode("unicode_escape")
      tag = line.split()[2][0].lower()

      if word != ".":
        sentence_list.append((word, tag))
      else:
        if sentence_list != []:
          train_list.append(sentence_list)
        sentence_list = []
    file.close()
  return train_list

#function for generating sentences as string (format accepted by tagger)
def getSentences(path, file_list = []):
  sentence_list = []
  if file_list == []:
    file_list = listdir(path)
  for filename in file_list:
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    for line in lines:
      if line != "\n":
        word = line.split()[0]
        sentence_list.append(word)
    file.close()
    sentence_str = ' '.join(sentence_list)
  return sentence_str

# accuracy
def precision(path_train):
  # get file list
  training_files = listdir(path_train)
  for_training = training_files[:len(training_files) * 3 / 4]
  for_testing = training_files[len(training_files) * 3 / 4:]
  training_sentences = tagSentences(path_train, training_list = for_training, testing_list = for_testing)

  number_of_predictions = 0.0
  correct_predictions = 0.0
  number_of_b = 0.0
  b_prediction = 0.0
  number_of_i = 0.0
  i_prediction = 0.0
  number_of_o = 0.0
  o_prediction = 0.0
  # get correct sentence tag
  test_sentences = getTrainList(for_testing)
  for i in range(len(training_sentences)):
    train_s = training_sentences[i]
    actual_s = test_sentences[i]
    for j in range(len(train_s)):
      train_w = train_s[j][0]
      train_t = train_s[j][1]
      actual_w = actual_s[j][0]
      actual_t = actual_s[j][1]

      if actual_w != train_w:
        print "indexing got messed up..."
        return

      # check precision for b tags
      if actual_t == 'b':
        if train_t == 'b':
          b_prediction += 1
        number_of_b += 1
      # check precision for i tags
      if actual_t == 'i':
        if train_t == 'i':
          i_prediction += 1
        number_of_i += 1
      # check precision for o tags
      if actual_t == 'o':
        if train_t == 'o':
          o_prediction += 1
        number_of_o += 1
      # all tags
      if train_t == actual_t:
        correct_predictions += 1
      number_of_predictions += 1

  if number_of_b == 0:
    print("For B - tags: there were none detected")
  else:
    print("For B - tags: " + str(b_prediction / number_of_b))
  if number_of_i == 0:
    print("For I - tags: there were none detected")
  else:
    print("For I - tags: " + str(i_prediction / number_of_i))
  if number_of_o == 0:
    print("For O - tags: there were none detected")
  else:
    print("For O - tags: " + str(o_prediction / number_of_o))
  if number_of_predictions == 0:
    print("For all tags: there were none detected")
  else:
    print("For all tags: " + str(correct_predictions / number_of_predictions))

  print("is the length of test set == actual set?")
  print(len(training_sentences) == len(test_sentences))
  return correct_predictions / number_of_predictions

def tagSentences(path, training_list = [], testing_list = []):
  trainer = hmm.HiddenMarkovModelTrainer()
  train_data = getTrainList(training_list)
  tagger = trainer.train_supervised(train_data)
  sentences = getSentences(path, testing_list)
  tagged_sentences = tagger.tag(sentences.split())
  return tagged_sentences

# for precision calculations
path_train = "nlp_project2_uncertainty/train_modified"
p = precision(path_train) 
print p
