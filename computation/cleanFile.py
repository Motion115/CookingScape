import os
import shutil

def cleanScene():
    dir = "./.cache/"
    for filename in os.listdir(dir):
        # delete clip folder
        if os.path.exists(os.path.join(dir, filename, "clip")):
            shutil.rmtree(os.path.join(dir, filename, "clip"))
        # delete scene folder
        if os.path.exists(os.path.join(dir, filename, "scene")):
            shutil.rmtree(os.path.join(dir, filename, "scene"))
        if os.path.exists(os.path.join(dir, filename, "scene_list.csv")):
            os.remove(os.path.join(dir, filename, "scene_list.csv"))

def cleanEmbeddingOnly():
    dir = "./.cache/"
    for filename in os.listdir(dir):
        if os.path.exists(os.path.join(dir, filename, "video_embedding.npy")):
            os.remove(os.path.join(dir, filename, "video_embedding.npy"))
        # delete scene_list.csv and video_embedding.npy
        if os.path.exists(os.path.join(dir, filename, "eval_videoTag_info.json")):
            os.remove(os.path.join(dir, filename, "eval_videoTag_info.json"))

def cleanSceneRelatedFile():
    dir = "./.cache/"
    for filename in os.listdir(dir):
        # delete clip folder
        if os.path.exists(os.path.join(dir, filename, "clip")):
            shutil.rmtree(os.path.join(dir, filename, "clip"))
        # delete scene folder
        if os.path.exists(os.path.join(dir, filename, "scene")):
            shutil.rmtree(os.path.join(dir, filename, "scene"))
        
        # delete scene_list.csv and video_embedding.npy
        if os.path.exists(os.path.join(dir, filename, "eval_videoTag_info.json")):
            os.remove(os.path.join(dir, filename, "eval_videoTag_info.json"))
       
        if os.path.exists(os.path.join(dir, filename, "scene_list.csv")):
            os.remove(os.path.join(dir, filename, "scene_list.csv"))
        
        if os.path.exists(os.path.join(dir, filename, "video_embedding.npy")):
            os.remove(os.path.join(dir, filename, "video_embedding.npy"))

