import argparse
import json
import os
from tqdm import tqdm
from pytube import YouTube

BASE_URL = "https://www.youtube.com/watch?v="

if __name__ == "__main__":

    save_path = "./data/captions/"

    with open("filtered_ground_truth.json", 'r', encoding='utf-8') as f:
        filtered_ground_truth = json.load(f)
    
    video_ids = []
    for k, v in filtered_ground_truth.items():
        # remove the .mp4 from the back
        key = k[:-4]
        video_ids.append(key)

    for v in tqdm(video_ids):
        try:
            yt = YouTube(BASE_URL + v)
        except:
            print("Connection Error")

        # try:
        caption = yt.captions
        # check if yt.actions is empty
        if caption:
            print(caption)
            # check if there is english captions
            if "en" in caption:
                caption = caption["en"]
                print(caption.download(output_path=save_path,
                    filename=f'{v.split("=")[-1]}.json'))

        # except:
        #     print("Error downloading caption")

