from tqdm import tqdm
from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM_langchain, Qwen1_8
from utils.zhipu.generateToken import getToken
from utils.foodNER import foodNER
import json
import os
import pandas as pd
from datetime import datetime, timedelta


def instructional_cooking_video_knowledge_extraction_computation_pipeline(
    video_file_path: str,
    video_name: str,  # without encoding
    video_encoding: str,
    whisper_ASR_model_path: str,
    glm_token_file: str,
    vlm_weight_path: str,
    vlm_dictionary_filepath: str,
    shortForm = False,
    persistent_calc=False
):
    video_info_directory = f"./.cache/{video_name}"
    # Check if the video have been processed before
    if os.path.exists(f"{video_info_directory}/video_info.json") and persistent_calc == False:
        # here we did not check further content validity
        print("- Cached video info exist, skipping ...")
        return

    videoPreprocessingModel = Video(
        file_path=video_file_path,
        file_name=video_name,
        encoding=video_encoding,
        ASR_model_path=whisper_ASR_model_path,
        isShortForm=shortForm)
    
    # read the scene list
    scene_list = pd.read_csv(f"{video_info_directory}/scene_list.csv")
    # Convert the "Start Timecode" column to timedelta
    scene_list["Start Timecode"] = pd.to_timedelta(
        scene_list["Start Timecode"]).dt.total_seconds()
    selected_columns = scene_list[[
        "Scene Number", "Start Timecode", "Length (seconds)"]]
    # rename the columns
    selected_columns.columns = ["id", "startTime", "duration"]
    # pivot to dictionary
    video_info_dict = selected_columns.set_index('id').to_dict(orient='index')

    transcript = videoPreprocessingModel.get_transcript()[0]

    languageModel_GLM = GLM_langchain(token=getToken(glm_token_file))

    print("- Extracting Cooking Steps")
    milestonedCookingSteps = languageModel_GLM.getCookingSteps(transcript, len(scene_list))
    sequentialCookingSteps = languageModel_GLM.getSequentialCookingSteps(transcript)

    # print(milestonedCookingSteps, sequentialCookingSteps)

    # # save cooking steps as json
    # with open("./seqCookingSteps.json", "w") as f:
    #     json.dump(sequentialCookingSteps, f)

    # load cookingSteps.json
    # with open("./cookingSteps.json", "r") as f:
    #     milestonedCookingSteps = json.load(f)

    # with open("./seqCookingSteps.json", "r") as f:
    #     sequentialCookingSteps = json.load(f)

    cookingStepsTotal = milestonedCookingSteps
    cookingStepsTotal["sequential"] = sequentialCookingSteps

    # print(milestonedCookingSteps)
    print("- Extracting Food Entities")
    foodEntityRecognition = foodNER()
    ingredientsList = foodEntityRecognition.extractEntityFromSteps(
        cookingSteps=cookingStepsTotal,
        isLemmantize=True)

    # print(ingredientsList)

    # languageModel_GLM.backtraceIngredients(ingredientsList, sequentialCookingSteps)

    visionLanguageModel = MIL_NCE(
        weight_filepath=vlm_weight_path,
        dictionary_filepath=vlm_dictionary_filepath,
        video_filepath=f".cache/{video_name}/")

    tagged_cooking_steps = visionLanguageModel.regrouped_steps_vidtag(
        milestonedCookingSteps)
    tagged_ingredients = visionLanguageModel.ingredients_vidtag(
        ingredientsList)
    
    print("- Evaluating difficulty")
    # 5-shot decision-making
    ratingList = []
    for i in tqdm(range(5)):
        rating = languageModel_GLM.getRating(transcript)
        ratingList.append(rating)
    # for rate in ratingList:
    #     print(rate["rating"])
    # count the ratings
    ratingCount = {}
    for rate in ratingList:
        if rate["rating"] in ratingCount:
            ratingCount[rate["rating"]] += 1
        else:
            ratingCount[rate["rating"]] = 1
    # get the most common rating
    finalVerdict = max(ratingCount, key=ratingCount.get)
    for rate in ratingList:
        if rate["rating"] == finalVerdict:
            finalRateData = rate
            break

    # with open("./rate.json", "w") as f:
    #     json.dump(finalRateData, f)

    # finalRateData = json.load(open("./rate.json", "r"))

    # merge ingredients and cooking steps into one dict
    video_info_dict = {
        "steps": tagged_cooking_steps,
        "ingredients": tagged_ingredients,
        "scene_list": video_info_dict,
        "difficulty": finalRateData,
        "transcript": transcript,
    }

    # to json
    with open(f"{video_info_directory}/video_info.json", "w") as f:
        json.dump(video_info_dict, f)


if __name__ == "__main__":
    videoList = [
        # "Steak-GR",
        # "Steak-Wolfgang",
        # "GR-SzechuanChicken",
        # "GR-Branzino",
        # "GR-Souffle",
        # "Shorts-GR-ChilliChicken",
        # 'Shorts-GR-SweetPepperSause',
        # "Shorts-GR-MoroccanLamb",
        # "Shorts-GR-SpicyBlackBeans",
        "GR-FishChips"
    ]
    for video in videoList:
        instructional_cooking_video_knowledge_extraction_computation_pipeline(
            video_file_path="./data/",
            video_name=video,
            video_encoding=".mp4",
            whisper_ASR_model_path="E:/Data(E)/Models/Openai-Whisper",
            glm_token_file="./utils/api_config.json",
            vlm_weight_path="utils/S3D/s3d_howto100m.pth",
            vlm_dictionary_filepath="utils/S3D/s3d_dict.npy",
            shortForm=False,
            persistent_calc=True
        )

    # video = Video(
    #     file_path="./data/Coq_au_vin/",
    #     file_name= "Coq_au_vin_Donnie_Brasco",
    #     encoding=".mp4",
    #     ASR_model_path="E:/Data(E)/Models/Openai-Whisper")

    # agent = Qwen1_8(model_directory="E:/Data(E)/Models/Qwen-1.8B/Qwen-1_8B-Chat-Int4")
    # resp = agent.call(
    #     context=f'''A cooking process can be divided into 3 phases: preparation, cooking, and assembly. \n \
    #                 \n \
    #                 The following is a transcript of a cooking video. First, extract all the subtasks. Secondly, group the subtasks into the 3 phases mentioned before. \n \
    #                 \n \
    #                 ``` \n \
    #                 {transcript}\n
    #                 ```\
    #             ''',
    #     system_instruction=""
    # )
    # print(resp)

    # for t in transcript:
    #     resp = agent.call(
    #         context=f'''Return a list of named entities that are ingredients in the text.\n \
    #             Text: In there, I'm going to add a little touch of garlic. \n \
    #             Named entities: garlic \n \
    #             Text: However you break down your chicken, the next step is to dredge in flour.\n \
    #             Named entities: chicken, flour \n \
    #             Text: Put this on the chopping board. \n \
    #             Named entities: None \n \
    #             Text: {t} \n \
    #             Named entities:''',
    #         system_instruction=""
    #     )
    #     print(resp)
    # resp = agent.call(
    #     context="Extract all the ingredients mentioned in the following transcript. Output the ingredients and separate it with semicolons.\n" + transcript[0],
    # )
    # print(resp)

    # resp = agent.call(
    #     context="Use the form of a Python List to show all the ingredients: " + resp
    # )
    # print(resp)
