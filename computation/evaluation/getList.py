import json

# read categories.json
with open('categories.json', 'r', encoding='utf-8') as f:
    categories = json.load(f)
    f.close()

video_to_cat = categories["video_to_cat"]
# filter out only the videos with type "Food and Entertaining"
filtered_videos = [video for video in video_to_cat.keys() if video_to_cat[video] == "Food and Entertaining"]
filtered_videos = set(filtered_videos)

# read all_data_test.json
with open('all_data_test.json', 'r', encoding='utf-8') as f:
    all_data_test = json.load(f)
    f.close()

video_list = set()
video_dict = {}
for key, val in all_data_test.items():
    for k, v in val.items():
        video_list.add(k)
        video_dict[k] = v["v_duration"]
print(len(video_list))

# get intersection
intersection = video_list.intersection(filtered_videos)
print(len(intersection))

# filter video_dict with items in intersection
filtered_video_dict = {k: v for k, v in video_dict.items() if k in intersection}

# filter video_dict if the val is bigger than 180 and less than 600
filtered_video_dict = {k: v for k, v in filtered_video_dict.items() if v > 180}

# filter out the ground_truth for the filtered videos
with open("formatted_moment_evaluation_gt.json", 'r', encoding='utf-8') as f:
    ground_truth = json.load(f)
    f.close()

filtered_ground_truth = {k: v for k, v in ground_truth.items() if k in filtered_video_dict}

# write filtered_ground_truth to a json file
with open('filtered_ground_truth.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_ground_truth, f, ensure_ascii=False)
    f.close()
