from tqdm import tqdm
from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM_langchain, Qwen1_8
from utils.zhipu.generateToken import getToken
from utils.foodNER import foodNER
from utils.probabilityWeighting import probabilityWeighting
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from cleanFile import cleanSceneRelatedFile, cleanEmbeddingOnly


def instructional_cooking_video_knowledge_extraction_computation_pipeline(
    video_file_path: str,
    video_name: str,  # without encoding
    video_encoding: str,
    whisper_ASR_model_path: str,
    glm_token_file: str,
    vlm_weight_path: str,
    vlm_dictionary_filepath: str,
    step_list: list,
    shortForm=False,
):
    video_info_directory = f"./{video_file_path}/.cache/{video_name}"

    videoPreprocessingModel = Video(
        file_path=video_file_path,
        file_name=video_name,
        encoding=video_encoding,
        ASR_model_path=whisper_ASR_model_path,
        isShortForm=shortForm)

    complexSceneList = videoPreprocessingModel.get_scene_list()
    if len(complexSceneList) == 0:
        with open(f"./.cache/{video_name}/eval_videoTag_info.json", "w") as f:
            json.dump({
            "content": []}, f)
        return

    transcript = videoPreprocessingModel.get_transcript()[0]

    weightGenerator = probabilityWeighting(
        step_list, complexSceneList)
    weighted_sequential_steps = weightGenerator.getWeightingVector()

    visionLanguageModel = MIL_NCE(
        weight_filepath=vlm_weight_path,
        dictionary_filepath=vlm_dictionary_filepath,
        video_filepath=f".cache/{video_name}/")

    weightedTags = visionLanguageModel.weighted_instructiontag(
        weighted_sequential_steps)
    
    clip_list = []
    for step, detail in weightedTags.items():
        info = complexSceneList[detail["clip_id"][0]]
        content = {
            "start": info["startTime"] ,
            "end": info["endTime"],
            "sentence": detail["description"],
        }
        clip_list.append(content)
    
    # to json
    with open(f"./.cache/{video_name}/eval_videoTag_info.json", "w") as f:
        json.dump({
            "content": clip_list}, f)
    return
    

def compute_iou(interval_1, interval_2):
    start_i, end_i = interval_1[0], interval_1[1]
    start, end = interval_2[0], interval_2[1]
    intersection = max(0, min(end, end_i) - max(start, start_i))
    union = min(max(end, end_i) - min(start, start_i),
                end-start + end_i-start_i)
    iou = float(intersection) / (union + 1e-8)
    return iou


def load_data(gt_data, pred_data):
    gt = gt_data
    pred = pred_data

    if isinstance(gt_data, str):
        with open(gt_data, 'r') as f:
            gt = json.load(f)
    else:
        assert isinstance(gt, dict), "GT data should be a str path or a dict"

    if isinstance(pred_data, str):
        with open(pred_data, 'r') as f:
            pred = json.load(f)
    else:
        assert isinstance(
            pred, dict), "Prediction data should be a str path or a dict"

    return gt, pred

def compute_step_bound_scores(gt_data, pred_data):
    gt, pred = load_data(gt_data, pred_data)
    results = {}
    results["recall"] = {}
    results["precision"] = {}

    for tiou in [0.3, 0.5, 0.7]:
        recall = []
        precision = []
        ious = []
        for i, video in tqdm(enumerate(gt), total=len(gt)):
            best_recall = 0
            best_precision = 0

            ref_set_covered = set([])
            pred_set_covered = set([])

            refs = gt[video]["bounds"]
            preds = pred[video]["bounds"]

            for pred_i, pred_x in enumerate(preds):
                local_ious = []

                for ref_i, gt_x in enumerate(refs):
                    iu = compute_iou(pred_x, gt_x)

                    local_ious.append(iu)
                    if iu > tiou:
                        ref_set_covered.add(ref_i)
                        pred_set_covered.add(pred_i)

                ious.append(max(local_ious))

            new_precision = float(len(pred_set_covered)) / (pred_i + 1)
            best_precision = max(best_precision, new_precision)

            new_recall = float(len(ref_set_covered)) / len(refs)
            best_recall = max(best_recall, new_recall)

            recall.append(best_recall)
            precision.append(best_precision)

        if len(recall) > 0:
            results["recall"][f"{tiou}"] = sum(
                recall) / len(recall) * 100
            results["precision"][f"{tiou}"] = sum(
                precision) / len(precision) * 100
            results["total"] = len(recall)

    return results


def evaluate_moment_retrieval(gt_data, pred_data):
    gt, pred = load_data(gt_data, pred_data)

    score_dict = {}

    tIoUs = [0.3, 0.5, 0.7]
    for tIoU in tIoUs:
        scores = []

        for prompt in tqdm(gt):
            for video in gt[prompt]:
                if gt[prompt][video]["clip"]:
                    gt_bounds = gt[prompt][video]["bounds"]
                    pred_bounds = pred[prompt][video]["bounds"]

                    iou = compute_iou(gt_bounds, pred_bounds)

                    if iou < tIoU:
                        score = 0
                    else:
                        score = 1

                    scores.append(score)

        if len(scores) > 0:
            score_dict["total_videos"] = len(scores)
            score_dict[f"R@{tIoU}"] = np.mean(scores) * 100

    return score_dict


if __name__ == "__main__":
    GENERATE = False
    # cleanSceneRelatedFile()
    src_dir = "evaluation/"
    with open(f"{src_dir}/final_list.json", "r") as f:
        ground_truth = json.load(f)

    if GENERATE:  
        # cleanEmbeddingOnly()
        for video, actions in tqdm(ground_truth.items()):
            video = video[:-4]
            captions = actions["captions"]
            step_list = []
            for act in captions:
                step_list.append(act["sentence"])

            clip_list = instructional_cooking_video_knowledge_extraction_computation_pipeline(
                video_file_path=f"{src_dir}/data/videos/",
                video_name=video,
                video_encoding=".mp4",
                whisper_ASR_model_path="E:/Data(E)/Models/Openai-Whisper",
                glm_token_file="./utils/api_config.json",
                vlm_weight_path="utils/S3D/s3d_howto100m.pth",
                vlm_dictionary_filepath="utils/S3D/s3d_dict.npy",
                step_list=step_list,
                shortForm=False
            )

    pred_data = {}
    useful_list = []
    for video, actions in ground_truth.items():
        video = video[:-4]
        scene_len = len(os.listdir(f"./.cache/{video}/clip"))
        if scene_len > 5:
            useful_list.append(video + ".mp4")
            file_path = f"./.cache/{video}/eval_videoTag_info.json"
            with open(file_path, "r") as f:
                content = json.load(f)
            bounds = []
            for t in content["content"]:
                bounds.append([t["start"], t["end"]])
            
            pred_data[video + ".mp4"] = {"bounds": bounds, "content": content["content"]}

    filtered_ground_truth = {k: v for k, v in ground_truth.items()
              if k in useful_list}
    
    print(len(filtered_ground_truth), len(pred_data))

    res = compute_step_bound_scores(filtered_ground_truth, pred_data)
    print(res)

    

        
