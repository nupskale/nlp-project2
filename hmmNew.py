import nltk
import numpy as np
from os import listdir
from nltk.corpus import treebank

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

train_data = getTrainList()

from nltk.tag import hmm
#hmm trainer
trainer = hmm.HiddenMarkovModelTrainer()
#training hmm tagger
tagger = trainer.train_supervised(train_data)

print tagger

#function for generating sentences as string (format accepted by tagger)
def getSentences(path):
  sentence_list = []
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

#sentences generated for test private folder
test_private = getSentences('nlp_project2_uncertainty/test-private')
#sentences generated for test public folder
test_public = getSentences('nlp_project2_uncertainty/test-public')

#BIO tags assigned to test private sentences, returns list of word and tag
test_private_tags = tagger.tag(test_private.split())

#BIO tags assigned to test public sentences, returns list of word and tag
test_public_tags = tagger.tag(test_public.split())