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
