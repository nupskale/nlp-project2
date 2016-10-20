from nltk.tag import CRFTagger
from os import listdir

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
        train_list.append(sentence_list)
        sentence_list = []
    file.close()
  return train_list

def getSentences(path):
  sentences_list = []
  for filename in listdir(path):
    file = open(path + "/" + filename, "r")
    lines = file.readlines()
    sentence = []
    for line in lines:
      if line != "\n":
        word = line.split()[0]
        word = word.decode("unicode_escape")

        if word != ".":
          sentence.append(word)
        else:
          sentences_list.append(sentence)
          sentence = []
    file.close()
  return sentences_list


def tagSentences(path):
  ct = CRFTagger()
  train_list = getTrainList()
  ct.train(train_list, 'model.crf.tagger')
  sentences = getSentences(path)
  tagged_sentences = ct.tag_sents(sentences)
  return tagged_sentences

# path variables
path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"

# run
sentences = tagSentences(path_private)
