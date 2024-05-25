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
    
    complexSceneList = videoPreprocessingModel.get_scene_list()

    transcript = videoPreprocessingModel.get_transcript()[0]

    languageModel_GLM = GLM_langchain(token=getToken(glm_token_file))

    print("- Extracting Cooking Steps")
    milestonedCookingSteps = languageModel_GLM.getCookingSteps(transcript)
    sequentialCookingSteps = languageModel_GLM.getSequentialCookingSteps(transcript)

    # print(milestonedCookingSteps, sequentialCookingSteps)

    # save cooking steps as json
    # with open("./milestonedCookingSteps.json", "w") as f:
    #     json.dump(milestonedCookingSteps, f)


    # load cookingSteps.json
    # with open("./milestonedCookingSteps.json", "r") as f:
    #     milestonedCookingSteps = json.load(f)

    # with open("./seqCookingSteps.json", "r") as f:
    #     sequentialCookingSteps = json.load(f)

    weightGenerator = probabilityWeighting(sequentialCookingSteps, complexSceneList)
    weighted_sequential_steps = weightGenerator.getWeightingVector()
    # weighted_milestoned_steps = {}
    # for key, val in milestonedCookingSteps.items():
    #     tempWG = probabilityWeighting(val, complexSceneList)
    #     weighted_milestoned_steps[key] = tempWG.getWeightingVector()

    cookingStepsTotal = milestonedCookingSteps
    cookingStepsTotal["sequential"] = sequentialCookingSteps

    # cookingStepsTotalWeight = weighted_milestoned_steps
    # cookingStepsTotalWeight["sequential"] = weighted_sequential_steps

    print("- Extracting Food Entities")
    foodEntityRecognition = foodNER()
    ingredientsList = foodEntityRecognition.extractEntityFromSteps(
        cookingSteps=cookingStepsTotal,
        isLemmantize=True)

    visionLanguageModel = MIL_NCE(
        weight_filepath=vlm_weight_path,
        dictionary_filepath=vlm_dictionary_filepath,
        video_filepath=f".cache/{video_name}/")
    
    weightedTags = visionLanguageModel.weighted_instructiontag(weighted_sequential_steps)

    for key, val in tqdm(weightedTags.items()):
        step = val["description"]
        cla = languageModel_GLM.classification(step)
        val["category"] = cla
    
    # write back to default style
    tagged_cooking_steps = {
        "preparation": {},
        "cooking": {},
        "assembly": {},
        "sequential": weightedTags
    }

    i, j, k = 1, 1, 1
    for key, val in weightedTags.items():
        if val["category"] == "preparation":
            tagged_cooking_steps["preparation"][f"step_{i}"] = val
            i += 1
            continue
        elif val["category"] == "cooking":
            tagged_cooking_steps["cooking"][f"step_{k}"] = val
            k += 1
            continue
        elif val["category"] == "assembly":
            tagged_cooking_steps["assembly"][f"step_{j}"] = val
            k += 1
            continue
        else:
            continue

    # tagged_cooking_steps = visionLanguageModel.regrouped_steps_vidtag(cookingStepsTotalWeight)
    
    # tagged_cooking_steps["sequential"] = weightedTags
    
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
        "scene_list": videoPreprocessingModel.read_scene_from_file(),
        "difficulty": finalRateData,
        "transcript": transcript,
    }

    # to json
    with open(f"{video_info_directory}/video_info.json", "w") as f:
        json.dump(video_info_dict, f)


if __name__ == "__main__":
    videoList = [
        # "GR-Branzino",
        # "GR-ShortRibs",
        # "GR-Souffle",
        # "GR-SzechuanChicken",
        # "GR-WellingtonBeef",
        # "GR-FishChips",
        "Steak-GR",
        # "Steak-Wolfgang",

        # "Shorts-GR-ChilliChicken",
        # 'Shorts-GR-SweetPepperSause',
        # "Shorts-GR-MoroccanLamb",
        # "Shorts-GR-SpicyBlackBeans",
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
