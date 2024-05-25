import flask
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

from utils.MIL_NCE import MIL_NCE

from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM_langchain, Qwen1_8
from utils.zhipu.generateToken import getToken
from utils.foodNER import foodNER
import json
import torch
import pandas as pd
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer

def getModels(
    video_file_path: str,
    video_name: str,  # without encoding
    video_encoding: str,
    glm_token_file: str,
    vlm_weight_path: str,
    vlm_dictionary_filepath: str
):
    videoPreprocessingModel = Video(
        file_path=video_file_path,
        file_name=video_name,
        encoding=video_encoding,
        ASR_model_path="E:/Data(E)/Models/Openai-Whisper",
        isShortForm=False)

    languageModel_GLM = GLM_langchain(token=getToken(glm_token_file))

    visionLanguageModel = MIL_NCE(
        weight_filepath=vlm_weight_path,
        dictionary_filepath=vlm_dictionary_filepath,
        video_filepath=f".cache/{video_name}/")
    
    return languageModel_GLM, visionLanguageModel, videoPreprocessingModel

llm, vlm, video = getModels(
        video_file_path="./data/",
        video_name="GR-FishChips",
        video_encoding=".mp4",
        glm_token_file="./utils/api_config.json",
        vlm_weight_path="utils/S3D/s3d_howto100m.pth",
        vlm_dictionary_filepath="utils/S3D/s3d_dict.npy",
    )

scene_list = video.get_scene_list()
embedding_list = []
for id, scene in scene_list.items():
    # embedding to torch data structure, 2D tensor
    embedding_list.append(torch.tensor(scene["embedding"]))
scene_semantic_emb = torch.stack(embedding_list)

sentenceBERT = SentenceTransformer("all-MiniLM-L6-v2")


app = Flask(__name__)
api = Api(app)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/textToClip', methods=['POST'])
def process_request():
    data = request.get_json()
    # get the text embedding
    text_mat = vlm.get_stacked_text_encoding([data["description"]])
    # get semantic embedding
    semantic_emb = torch.tensor(sentenceBERT.encode([data["description"]]))
    # get the weight embedding
    weight_emb = torch.cosine_similarity(
        scene_semantic_emb, semantic_emb, dim=1)
    # calculate the similarity between video and text
    similarity = vlm.calc_similarity(text_mat, vlm.video_embedding)
    similarity = torch.mul(similarity, weight_emb)
    # get the top-k similarity
    topk_values, topk_indices = torch.topk(similarity, 1, dim=1)
    # add 1 on all elements to match indexing
    topk_indices = topk_indices + 1
    # to numpy
    clip_id_list = topk_indices.numpy()[0].tolist()
    return {
        "description": data["description"],
        "clip_id": clip_id_list,
    }

@app.route('/ingredientVideoSim', methods=['POST'])
def process_request_ingredient():
    data = request.get_json()
    resp = vlm.ingredients_vidtag([data["ingredient"]])
    return resp

@app.route('/ingredientReplacer', methods=['POST'])
def process_request_replacer():
    data = request.get_json()
    usedIngredients = data["usedIngredient"]
    replacementIngredient = data["ingredient"]
    transcript = data["transcript"]
    original_resp = llm.explainIngredient(transcript, usedIngredients)
    if replacementIngredient != "":
        alter_resp = llm.exploreAlternativeIngredient(
            transcript, usedIngredients, replacementIngredient)
        return {
            "ingredientUse": original_resp,
            "ingredientAlter": alter_resp
        }
    else:
        return {
            "ingredientUse": original_resp
        }


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="127.0.0.1")
