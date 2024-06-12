import json

with open('final_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
startWord = {}
uniqWord = set()
totalWordLen = 0
for key, val in data.items():
    count += len(val["captions"])
    for caption in val["captions"]:
        sent = caption["sentence"].split()
        totalWordLen += len(sent)
        # all letters to lower
        for i in range(len(sent)):
            sent[i] = sent[i].lower()
            uniqWord.add(sent[i])
        word = sent[0]
        if word not in startWord:
            startWord[word] = 1
        else:
            startWord[word] += 1

print(len(data))
print(count)
print("Start Words:", len(startWord))
print("Unique Words:", len(uniqWord))
print("Average Word Length:", totalWordLen / count)

# sort the startWord by value
startWord = dict(sorted(startWord.items(), key=lambda item: item[1], reverse=True))
i = 0
# print the first 10 startWord
for key, val in startWord.items():
    print(key, val)
    if i >= 10:
        break
    i += 1

