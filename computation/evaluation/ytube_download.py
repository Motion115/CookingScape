import argparse
import json
import os
from tqdm import tqdm
from pytube import YouTube

BASE_URL = "https://www.youtube.com/watch?v="

if __name__ == "__main__":

    save_path = "./data/videos/"

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

        try:
            # caption = yt.captions["a.en"]
            # print(caption)
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc(
            ).first().download(output_path=save_path, filename=f'{v.split("=")[-1]}.mp4')
        except:
            print("Error downloading video")
