from nltk.tag import CRFTagger
from os import listdir
import accuracy_metrics as am

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
        # to avoid key, value errorin ct.train(train_list, 'model.crf.tagger')
        if sentence_list != []:
          train_list.append(sentence_list)
        sentence_list = []
    file.close()
  return train_list

def getSentences(path, file_list = []):
  sentences_list = []
  if file_list == []:
    file_list = listdir(path)
  for filename in file_list:
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


def tagSentences(path, training_list = [], testing_list = []):
  ct = CRFTagger()
  train_list = getTrainList(training_list)
  ct.train(train_list, 'model.crf.tagger')
  sentences = getSentences(path, testing_list)
  tagged_sentences = ct.tag_sents(sentences)
  return tagged_sentences

# path variables
path_train = "nlp_project2_uncertainty/train_modified"
path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"

# # get sentences
# private_sentences = tagSentences(path_private)
# public_sentences = tagSentences(path_public)

# for testing
training_files = listdir(path_train)
for_training = training_files[:len(training_files) * 3 / 4]
for_testing = training_files[len(training_files) * 3 / 4:]
training_sentences = tagSentences(path_train, training_list = for_training, testing_list = for_testing)

# accuracy metrics
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

print("For B - tags:" + str(b_prediction / number_of_b))
print("For I - tags:" + str(i_prediction / number_of_i))
print("For O - tags:" + str(o_prediction / number_of_o))
print("For all tags:" + str(correct_predictions / number_of_predictions))
