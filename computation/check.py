import json
from math import sqrt
import os
import shutil
import pandas as pd
folder = ".cache/"
videoSrc = "data/New/"
targetDir = ".cacheTest/"

dirs = os.listdir(folder)

CHECK = False
if CHECK:
    for dir in dirs:
        # check if video_info.json exist
        if not os.path.exists(folder + dir + "/video_info.json"):
            print(dir)
            continue
                
        # make a directory for the video
        os.mkdir(targetDir + dir)
        # copy video from videoSrc
        shutil.copy(videoSrc + dir + ".mp4", targetDir + dir + "/" + dir + ".mp4")
        # copy video_info.json from folder
        shutil.copy(folder + dir + "/video_info.json", targetDir + dir + "/video_info.json")

info = []
for dir in dirs:
    # read scene_list.csv
    df = pd.read_csv(folder + dir + "/scene_list.csv")
    number_of_scene = len(df)
    avg_length_of_scene = df["Length (seconds)"].sum() / number_of_scene
    std_length_of_scene = df["Length (seconds)"].std()

    # read video_info.json
    with open(folder + dir + "/video_info.json", "r") as f:
        video_info = json.load(f)
    
    steps_number = len(video_info["steps"]["sequential"])
    description_len_list = []
    for key, value in video_info["steps"]["sequential"].items():
        length = len(value["description"].split())
        description_len_list.append(length)
        
    step_description_length_avg = sum(description_len_list) / steps_number
    step_description_length_std = sqrt(sum(
        [(length - step_description_length_avg) ** 2 for length in description_len_list]) / steps_number)

    ingredients_number = len(video_info["ingredients"])
    info.append({
        "video": dir,
        "scene_number": number_of_scene,
        "avg_length_of_scene": avg_length_of_scene,
        "std_length_of_scene": std_length_of_scene,
        "steps_number": steps_number,
        "step_description_length_avg": step_description_length_avg,
        "step_description_length_std": step_description_length_std,
        "ingredients_number": ingredients_number
    })

df = pd.DataFrame(info)
# keep 2 digits
df = df.round(2)
df.to_csv("info.csv", index=False)

