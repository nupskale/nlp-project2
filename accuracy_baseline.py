from os import listdir

# THIS FILE JUST RETURNS THE PRECISION FOR B, I, O, AND ALL TAGS FOR THE BASELINE.

# training
path = "nlp_project2_uncertainty/train_modified"
all_files = listdir(path)
# use 75% for training, 25% for testing accuracy
training_files = all_files[:len(all_files) * 3 / 4]
testing_files = all_files[len(all_files) * 3 / 4:]

train_dict = {}
for filename in training_files:
  file = open(path + "/" + filename, "r")
  lines = file.readlines()
  for i in range(len(lines)):
    line = lines[i]
    word = line.split()[0].lower() + " " + line.split()[1].lower()
    tag = line.split()[2][0].lower()

    if word not in train_dict:
      train_dict[word] = {}
      train_dict[word]["before"] = {"b": [], "i": [], "o": []}
      train_dict[word]["after"] = {"b": [], "i": [], "o": []}

    if i > 0:
      train_dict[word]["before"][tag].append(lines[i-1].split()[0].lower())
    else:
      train_dict[word]["before"][tag].append("")

    if i < len(lines) - 1:
      train_dict[word]["after"][tag].append(lines[i+1].split()[0].lower())
    else:
      train_dict[word]["after"][tag].append("")

    # not sure if we should remove duplicates
    # # remove duplicates
    # list(set(train_dict[word]["before"][tag]))
    # list(set(train_dict[word]["after"][tag]))

# sequence tagger
test = {}
for filename in testing_files:
  file = open(path + "/" + filename, "r")
  test[filename] = {}
  lines = file.readlines()
  for i in range(len(lines)):
    line = lines[i]
    # check if newline
    if line != "\n":
      word = line.split()[0].lower() + " " + line.split()[1].lower()

      if word in train_dict:
        before_words = train_dict[word]["before"]
        after_words = train_dict[word]["after"]

        if i > 0 and lines[i-1] != "\n":
          preceding = lines[i-1].split()[0].lower()
        else:
          preceding = ""
        if i < len(lines) - 2 and lines[i+1] != "\n":
          following = lines[i+1].split()[0].lower()
        else:
          following = ""

        b_count = before_words["b"].count(preceding) + after_words["b"].count(following)
        i_count = before_words["i"].count(preceding) + after_words["i"].count(following)
        o_count = before_words["o"].count(preceding) + after_words["o"].count(following)

        if b_count > i_count:
          tag = "b"
        elif b_count > o_count:
          tag = "i"
        elif i_count > o_count:
          tag = "i"
        else:
          tag = "o"

      else:
        # todo: handle unknown words
        # print word + " not in train_dict... giving it tag O"
        tag = "o"

      test[filename][i] = tag

# precision = # correct predictions /  # predictions
number_of_predictions = 0.0
correct_predictions = 0.0
for filename in test.keys():
  tags = test[filename]

  lines = open(path + "/" + filename, "r").readlines()

  for i in range(len(lines)):
    line = lines[i]
    actual_tag = line.split()[2][0].lower()
    predicted_tag = tags[i]
    if actual_tag == predicted_tag:
      correct_predictions += 1
    number_of_predictions += 1

print("Precision for all tags: " + str(correct_predictions / number_of_predictions))

number_of_predictions = 0.0
correct_predictions = 0.0
for filename in test.keys():
  tags = test[filename]

  lines = open(path + "/" + filename, "r").readlines()

  for i in range(len(lines)):
    line = lines[i]
    actual_tag = line.split()[2][0].lower()
    predicted_tag = tags[i]

    if actual_tag == "b":
      if actual_tag == predicted_tag:
        correct_predictions += 1
      number_of_predictions += 1

print("Precision for B-cue tags: " + str(correct_predictions / number_of_predictions))

number_of_predictions = 0.0
correct_predictions = 0.0
for filename in test.keys():
  tags = test[filename]

  lines = open(path + "/" + filename, "r").readlines()

  for i in range(len(lines)):
    line = lines[i]
    actual_tag = line.split()[2][0].lower()
    predicted_tag = tags[i]

    if actual_tag == "i":
      if actual_tag == predicted_tag:
        correct_predictions += 1
      number_of_predictions += 1

print("Precision for I-cue tags: " + str(correct_predictions / number_of_predictions))

number_of_predictions = 0.0
correct_predictions = 0.0
for filename in test.keys():
  tags = test[filename]

  lines = open(path + "/" + filename, "r").readlines()

  for i in range(len(lines)):
    line = lines[i]
    actual_tag = line.split()[2][0].lower()
    predicted_tag = tags[i]

    if actual_tag == "o":
      if actual_tag == predicted_tag:
        correct_predictions += 1
      number_of_predictions += 1

print("Precision for O tags: " + str(correct_predictions / number_of_predictions))
