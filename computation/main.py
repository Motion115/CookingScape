from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM_langchain, Qwen1_8
from utils.zhipu.generateToken import getToken
from utils.foodNER import foodNER
import json, os

def instructional_cooking_video_knowledge_extraction_computation_pipeline(
    video_file_path: str,
    video_name: str, # without encoding
    video_encoding: str,
    whisper_ASR_model_path: str,
    glm_token_file: str,
    persistent_calc = False
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
        ASR_model_path=whisper_ASR_model_path)
    
    transcript = videoPreprocessingModel.get_transcript()[0]

    print("- Extracting Cooking Steps")
    languageModel_GLM = GLM_langchain(token=getToken(glm_token_file))
    # milestonedCookingSteps = languageModel_GLM.getCookingSteps(transcript)

    # # save cooking steps as json
    # with open("./cookingSteps.json", "w") as f:
    #     json.dump(milestonedCookingSteps, f)

    # load cookingSteps.json
    with open("./cookingSteps.json", "r") as f:
        milestonedCookingSteps = json.load(f)

    # print(milestonedCookingSteps)
    print("- Extracting Food Entities")
    foodEntityRecognition = foodNER()
    ingredientsList = foodEntityRecognition.extractEntityFromSteps(milestonedCookingSteps)


    visionLanguageModel = MIL_NCE(
        weight_filepath="utils/S3D/s3d_howto100m.pth",
        dictionary_filepath="utils/S3D/s3d_dict.npy",
        video_filepath=".cache/Steak-GR/")
            
    tagged_cooking_steps = visionLanguageModel.regrouped_steps_vidtag(milestonedCookingSteps)
    tagged_ingredients = visionLanguageModel.ingredients_vidtag(ingredientsList)

    # TODO: get a sequential step version (modify the LM_hook with additional function)
    # TODO: sanity check the ingredients to its raw form (use LM to perform this task)
    # TODO: get the scene interval data into the video_info_dict

    # merge ingredients and cooking steps into one dict
    video_info_dict = {
        "chronological_steps": "",
        "regrouped_steps": tagged_cooking_steps,
        "ingredients": tagged_ingredients
    }

    # to json
    with open(f"{video_info_directory}/video_info.json", "w") as f:
        json.dump(video_info_dict, f)

if __name__ == "__main__":
    instructional_cooking_video_knowledge_extraction_computation_pipeline(
        video_file_path="./data/",
        video_name="Steak-GR",
        video_encoding=".mp4",
        whisper_ASR_model_path="E:/Data(E)/Models/Openai-Whisper",
        glm_token_file="./utils/api_config.json",
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