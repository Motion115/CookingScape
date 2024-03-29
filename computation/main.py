from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM_langchain, Qwen1_8
from utils.zhipu.generateToken import getToken
from utils.foodNER import ingredientsNER
import json, os

# This is a test for the system backend

if __name__ == "__main__":
    video = Video(
        file_path="./data/",
        file_name="Steak-GR", 
        encoding=".mp4",
        ASR_model_path="E:/Data(E)/Models/Openai-Whisper")
    # video = Video(
    #     file_path="./data/Coq_au_vin/",
    #     file_name= "Coq_au_vin_Donnie_Brasco", 
    #     encoding=".mp4",
    #     ASR_model_path="E:/Data(E)/Models/Openai-Whisper")
    transcript = video.get_transcript()
    transcript = transcript[0]
    # print(transcript)

    # glm_api = GLM("./utils/api_config.json")

    glm4 = GLM_langchain(token=getToken("./utils/api_config.json"))
    # cookingSteps = glm4.call(transcript)

    # # save cooking steps as json
    # with open("./cookingSteps.json", "w") as f:
    #     json.dump(cookingSteps, f)

    # load cookingSteps.json
    with open("./cookingSteps.json", "r") as f:
        cookingSteps = json.load(f)

    # print(cookingSteps)
    print("- Extracting Food Entities")

    # foodEntities = set()
    # for key, value in cookingSteps.items():
    #     for sentence in value:
    #         foodEntities = set(ingredientsNER(sentence)) | foodEntities
    
    # print(foodEntities)


    visual_language_grounding = MIL_NCE(
        weight_filepath="utils/S3D/s3d_howto100m.pth",
        dictionary_filepath="utils/S3D/s3d_dict.npy")
    
    videos = os.listdir(".cache/Steak-GR/clip/")
    if len(videos) > 999:
        print("Clips exceeding 1000, check sorting of clips to avoid wrong mapping!")
        exit()
        
    print("- Extracting Video Features")
    vid_encoding = visual_language_grounding.get_stacked_encoding(".cache/Steak-GR/clip/", videos)
    print(vid_encoding.shape)

    # preparation stage
    text_prep_mat = visual_language_grounding.get_stacked_text_encoding(cookingSteps["preparation"])
    print(text_prep_mat.shape)

    # calculation of similarity
    sim_prep_mat = visual_language_grounding.calc_similarity(text_mat=text_prep_mat, vid_mat=vid_encoding)
    print(sim_prep_mat.shape)

    # get maximum id for each row
    # test = sim_prep_mat.argmax(axis=1)


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