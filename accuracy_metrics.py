# number correct / number of predictions
def precision(path, test, specific_tag = ""):
  number_of_predictions = 0.0
  correct_predictions = 0.0
  for filename in test.keys():
    tags = test[filename]
    lines = open(path + "/" + filename, "r").readlines()
    for i in range(len(lines)):
      line = lines[i]
      actual_tag = line.split()[2][0].lower()
      predicted_tag = tags[i]
      if actual_tag == predicted_tag and specific_tag == "":
        correct_predictions += 1
      elif actual_tag == predicted_tag and specific_tag == actual_tag:
        correct_predictions += 1
      number_of_predictions += 1
  return correct_predictions / number_of_predictions

# number correct / number of examples in test set
def recall(path, test):
  number_of_examples = 0.0
  correct_predictions = 0.0
  for filename in test.keys():
    tags = test[filename]
    lines = open(path + "/" + filename, "r").readlines()
    for i in range(len(lines)):
      line = lines[i]
      actual_tag = line.split()[2][0].lower()
      predicted_tag = tags[i]
      if predicted_tag != "":
        if actual_tag == predicted_tag:
          correct_predictions += 1
        number_of_examples += 1
  return correct_predictions / number_of_examples

# 2 * precision * recall / (precision + recall)
def fMeasure(p, r):
  return 2 * p * r / (p + r)
