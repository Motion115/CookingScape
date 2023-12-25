from utils.video import Video
from utils.qwen_1_8 import Qwen1_8
from utils.MIL_NCE import MIL_NCE
import os

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
    transcript = video.get_transcript(separator=".")
    # print(transcript)

    visual_language_grounding = MIL_NCE(
        weight_filepath="utils/S3D/s3d_howto100m.pth",
        dictionary_filepath="utils/S3D/s3d_dict.npy")
    
    videos = os.listdir(".cache/Steak-GR/clip/")
    for vid in videos:
        vid_tensor = visual_language_grounding._transform_video(".cache/Steak-GR/clip/" + vid)
        text_input = "Sear steak"
        tv = visual_language_grounding.get_text_encoding(text_input)
        vv, v_long = visual_language_grounding.get_video_encoding(vid_tensor)
        sim = visual_language_grounding.calc_similarity(vv, tv)
        print(vid, sim)


    # agent = Qwen1_8(model_directory="E:/Data(E)/Models/Qwen-1.8B/Qwen-1_8B-Chat-Int4")
    # for t in transcript:
    #     resp = agent.call(
    #         context=f'''Extract ingredients from a sentence.\
    #         Eg.1: <Input>: We have garlic, and thyme.\n \
    #         <Output>: garlic, thyme \n \
    #         Eg.2 <Input>: Today, we are cooking steak.\n \
    #         <Output>: steak \n \
    #         Eg.3 <Input>: Turn the heat up to 140 degrees. \n \
    #         <Output>: \n \
    #         \n \
    #         <Input>: {t} \n \
    #         <Output>:
    #         ''',
    #         system_instruction=""
    #     )
    #     print(resp)
    # resp = agent.call(
    #     context="Extract all the ingredients mentioned in the following transcript. Output the ingredients and separate it with semicolons.\n" + transcript,
    # )
    # print(resp)

    # resp = agent.call(
    #     context="Order the extracted ingredients into a python list: " + resp
    # )
    # print(resp)