# in other files, you can use the functions defined in this file by writing:
# import accuracy_metrics
# accuracy_metrics.precision(...)
# and so on

"""
precision is number of correct over numer of predictions
arguments:
  path: specifies the file path
  test: a nested dictionary.
        test[filename] returns the tags for that particular file, where
        test[filename][i] returns the tag for a particular index i
  specific_tag: an optional argument. If you want to see the precision of B, I, and O tags, you can call
                precision(path, test, "b") (for a b tag, and so on)
                If you want to see overall precision, which is what is used in the f-measure calculation,
                just call precision(path, test)
"""
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

      # all tags
      if specific_tag == "":
        if actual_tag == predicted_tag:
          correct_predictions += 1
        number_of_predictions += 1
      # specific tag
      else:
        if specific_tag == actual_tag:
          if actual_tag == predicted_tag:
            correct_predictions += 1
          number_of_predictions += 1
  return correct_predictions / number_of_predictions

"""
recall is number correct over number of examples in test set
arguments:
  path: specifies the file path
  test: a nested dictionary.
        test[filename] returns the tags for that particular file, where
        test[filename][i] returns the tag for a particular index i
"""
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

"""
F-Measure = 2 * precision * recall / (precision + recall)
"""
def fMeasure(p, r):
  return 2 * p * r / (p + r)
