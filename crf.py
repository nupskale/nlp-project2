from nltk.tag import CRFTagger
from os import listdir
from csv import writer

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

      # # use pos
      # word = word + line.split()[1]

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

        # # use pos
        # word = word + line.split()[1]

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

# p = precision(path_train)
# print("-----------------------")
# print("Precision is " + str(p) + " and recall and F-measure will be the same")

# path variables
path_train = "nlp_project2_uncertainty/train_modified"
path_private = "nlp_project2_uncertainty/test-private"
path_public = "nlp_project2_uncertainty/test-public"

# Kaggle submission
def cueDetector(tagged_sentences):
  word_index_cues = ""
  sent_index_cues = ""
  cum_word_index = 0
  for sentence_index in range(len(tagged_sentences)):
    sentence = tagged_sentences[sentence_index]
    sentence_flag = False
    for word_index in range(len(sentence)):
      tag = sentence[word_index][1]
      if tag == "b":
        sentence_flag = True
        # check if word is not last word
        if word_index < len(sentence) - 1:
          # if 'i' is the next cue
          if sentence[word_index + 1][1] == 'i':
            word_index_cues += str(cum_word_index) + "-"
          # if 'i' is not the next cue, index-index
          else:
             word_index_cues += str(cum_word_index) + "-" +  str(cum_word_index) + " "
        else:
          # word is last word
          word_index_cues += str(cum_word_index) + "-" +  str(cum_word_index) + " "
      elif tag == "i":
        sentence_flag = True
        # previous cue was not o
        if word_index > 0 and sentence[word_index - 1][1] != 'o':
          # next cue is not 'i', or does not exist
          if word_index == len(sentence) - 1 or (word_index < len(sentence) - 1 and sentence[word_index + 1][1] != 'i'): 
            word_index_cues += str(cum_word_index) + " "
      cum_word_index += 1
    if sentence_flag:
      sent_index_cues += str(sentence_index) + " "
  return word_index_cues, sent_index_cues

# # get sentences
private_sentences = tagSentences(path_private)
public_sentences = tagSentences(path_public)

private_w_cues, private_s_cues = cueDetector(private_sentences)
public_w_cues, public_s_cues = cueDetector(public_sentences)

with open("crf_uncertain_phrase_detection.csv", 'w') as file:
  w = writer(file)
  w.writerow(["Type", "Spans"])
  w.writerow(["CUE-public", public_w_cues])
  w.writerow(["CUE-private", private_w_cues])

with open("crf_uncertain_sentence_detection.csv", "w") as file:
  w = writer(file)
  w.writerow(["Type", "Indices"])
  w.writerow(["SENTENCE-public", public_s_cues])
  w.writerow(["SENTENCE-private", private_s_cues])
