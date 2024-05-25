import os, json

# list dir data
files = os.listdir("./data/videos/")

filesSet = set(files)


with open("filtered_ground_truth.json", 'r', encoding='utf-8') as f:
    filtered_ground_truth = json.load(f)

video_ids = set()
for k, v in filtered_ground_truth.items():
    video_ids.add(k)

print(video_ids, filesSet)
# intersection
final_list = list(filesSet.intersection(video_ids))

# filter from filtered_ground_truth
output = {k: v for k, v in filtered_ground_truth.items() if k in final_list}
print(len(output))
with open('final_list.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
