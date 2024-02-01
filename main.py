from utils.video import Video
from utils.MIL_NCE import MIL_NCE
from utils.LM_hook import GLM, Qwen1_8
import os

if __name__ == "__main__":
    video = Video(
        file_path="./data/",
        file_name="Steak-GR", 
        encoding=".mp4",
        ASR_model_path="E:/Data(E)/Models/Openai-Whisper")
    # # video = Video(
    # #     file_path="./data/Coq_au_vin/",
    # #     file_name= "Coq_au_vin_Donnie_Brasco", 
    # #     encoding=".mp4",
    # #     ASR_model_path="E:/Data(E)/Models/Openai-Whisper")
    transcript = video.get_transcript()
    transcript = transcript[0]
    # print(transcript)

    glm_api = GLM("./utils/api_config.json")
    # glm_api.call_once(f'''
                      
    #     ```{transcript}```
    # ''')

    # visual_language_grounding = MIL_NCE(
    #     weight_filepath="utils/S3D/s3d_howto100m.pth",
    #     dictionary_filepath="utils/S3D/s3d_dict.npy")
    
    # videos = os.listdir(".cache/Steak-GR/clip/")
    # for vid in videos:
    #     vid_tensor = visual_language_grounding._transform_video(".cache/Steak-GR/clip/" + vid)
    #     text_input = "Sear steak"
    #     tv = visual_language_grounding.get_text_encoding(text_input)
    #     vv, v_long = visual_language_grounding.get_video_encoding(vid_tensor)
    #     sim = visual_language_grounding.calc_similarity(vv, tv)
    #     print(vid, sim)


    agent = Qwen1_8(model_directory="E:/Data(E)/Models/Qwen-1.8B/Qwen-1_8B-Chat-Int4")
    resp = agent.call(
        context=f'''A cooking process can be divided into 3 phases: preparation, cooking, and assembly. \n \
                    \n \
                    The following is a transcript of a cooking video. First, extract all the subtasks. Secondly, group the subtasks into the 3 phases mentioned before. \n \
                    \n \
                    ``` \n \
                    {transcript}\n
                    ```\
                ''',
        system_instruction=""
    )
    print(resp)

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