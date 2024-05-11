import gc
import math
import torch
from utils.S3D.s3dg import S3D
import cv2
import numpy as np
import torchvision.transforms.functional as F
import os
from tqdm import tqdm

class MIL_NCE:
    def __init__(self, weight_filepath, dictionary_filepath, video_filepath):
        self.weight_filepath = weight_filepath
        self.dictionary_filepath = dictionary_filepath
        self.video_filepath = video_filepath
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = self._load_model()
        self.video_embedding = self._load_video_encoding()

    def _load_model(self):
        net = S3D(self.dictionary_filepath)
        net.load_state_dict(torch.load(self.weight_filepath))
        # Move the model to the GPU
        net = net.to(self.device)
        # Evaluation mode
        net = net.eval()
        return net
    
    def _load_video_encoding(self):
        # check if the video embedding file exists
        file_path = os.path.join(self.video_filepath, "video_embedding.npy")
        clips_path = os.path.join(self.video_filepath, "clip")
        clips_file = os.listdir(clips_path)
        if len(clips_file) > 999:
            print("Clips exceeding 1000, check sorting of clips to avoid wrong mapping!")
            exit()

        if os.path.exists(file_path):
            print("- Load Video Features")
            # load the video embedding from the file
            video_embedding = np.load(file_path)
            # to torch
            video_embedding = torch.from_numpy(video_embedding)
            return video_embedding
        else:
            print("- Extracting Video Features")
            video_embedding = self._get_stacked_video_encoding(base_dir=clips_path, video_clips_paths=clips_file)
            # store this video embedding to file
            np.save(file_path, video_embedding)
            return video_embedding

    def _get_intra_frame_similarity(self):
        # use the existing video embedding to calculate the intra-frame similarity
        video_embedding = self.video_embedding

        similarity_mat = torch.matmul(video_embedding, video_embedding.t())
        print(similarity_mat)

        topk_values, topk_indices = torch.topk(similarity_mat, 5, dim=1)
        print(topk_indices)
        return

        # shift up video embedding matrix, leave the last one the same
        upshift_embedding = torch.cat((video_embedding[1:], video_embedding[-1].unsqueeze(0)), dim=0)
        print(upshift_embedding.shape)
        # calculate the similarity between video and its next frame
        intra_frame_similarity = torch.matmul(video_embedding, upshift_embedding.t())
        print(intra_frame_similarity)
        print(intra_frame_similarity.shape)
        # real similarity
        intra_frame_similarity = torch.diag(intra_frame_similarity)
        print(intra_frame_similarity)
        return intra_frame_similarity
    
    def ingredients_vidtag(self, ingredients_list):
        """
        Input:
         - ingredients_list: list of ingredients from NER

        Output:
         - similarity_dict: a key-value pair, key is the ingredient, value is the similarity list
        """
        # get the text embedding
        text_mat = self.get_stacked_text_encoding(ingredients_list)
        # calculate the similarity between video and text
        similarity = self.calc_similarity(text_mat, self.video_embedding)
        # tag ingredients with the similarity vector in dict
        similarity_dict = {}
        for i in range(0, len(ingredients_list)):
            similarity_dict[ingredients_list[i]] = similarity[i].tolist()
        return similarity_dict

    def regrouped_steps_vidtag(self, steps_dict):
        """
        Input:
         - steps_dict: containing three stages (preparation, cooking, assembly) as key & sequential as key, the value is a list of the steps

        Output:
         - steps_dict_new: containing the same stages, but the value is a dict also:
            1. Key is the step number
            2. Value is another dict containing step description and the top-3 matched clip_id (start from 1)
        """

        # regroup the cookingSteps
        steps_dict_new = {
            "preparation": {},
            "cooking": {},
            "assembly": {},
            "sequential": {}
        }
        # determine the k value
        if 10 < self.video_embedding.shape[0]:
            k_val = 10
        else:
            k_val = self.video_embedding.shape[0]

        for key, steps_in_stage in steps_dict.items():
            # get the text embedding
            text_mat = self.get_stacked_text_encoding(steps_in_stage)
            # calculate the similarity between video and text
            similarity = self.calc_similarity(text_mat, self.video_embedding)
            # get the top-k similarity
            topk_values, topk_indices = torch.topk(similarity, k_val, dim=1)
            # add 1 on all elements to match indexing
            topk_indices = topk_indices + 1
            for i in range(0, len(steps_in_stage)):
                # key is step{i}, value include description and top_3 clip id
                steps_dict_new[key][f"step_{i+1}"] = {
                    "description": steps_in_stage[i],
                    "clip_id": topk_indices[i].tolist()
                }
                # include the similarity values also?
        return steps_dict_new
    
    def _transform_video(self, video_clip_path):
        # Open the video using OpenCV
        video_capture = cv2.VideoCapture(video_clip_path)
        # Read the frames and resize them
        frames = []
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break
            resized_frame = cv2.resize(frame, (224, 224))  # Resize the frame to the desired shape
            resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # Convert to RGB format
            # normalize to (0, 1)
            resized_frame = resized_frame.astype(np.float32) / 255.0
            tensor_frame = F.to_tensor(resized_frame)  # Convert the frame to a PyTorch tensor
            frames.append(tensor_frame)
        
        # check if there is 32 tensors, if not, repeat the last one, else, truncate
        if len(frames) < 32:
            for i in range(32 - len(frames)):
                frames.append(frames[-1])
        else:
            # get the minimun multiple of 32
            min_multiple = math.floor(len(frames) / 32) * 32
            # min_multiple = 32
            frames = frames[:min_multiple]

        # Convert the list of frames to a PyTorch tensor
        video_tensor = torch.stack(frames)

        # Print the shape of the video tensor
        # switch the first two dimensions, original (T, C, H, W)
        video_tensor = video_tensor.permute(1, 0, 2, 3)
        # print(video_tensor.shape)  # (C, T, H, W)
        # Release the video capture object
        video_capture.release()
        return video_tensor
    
    def _get_stacked_video_encoding(self, base_dir, video_clips_paths):
        def generate_video_clips():
            for video_clip_path in tqdm(video_clips_paths):
                video_clip = self._transform_video(os.path.join(base_dir, video_clip_path))
                vec, vec_classification = self._get_video_encoding(video_clip)
                yield vec
                del video_clip, vec, vec_classification
                # collect the memory allocated, each tensor for 32 frames is approx. 800MB
                gc.collect()

        # stack the video clips on the first dimension
        video_clips = torch.cat(list(generate_video_clips()))
        return video_clips
    
    def _get_video_encoding(self, video_clip):
        # ensure net on gpu
        self.net = self.net.to(self.device)
        # video clip is a (C, T, H, W) tensor, add another dimension
        # channels, frames, height, width
        video_clip = video_clip.unsqueeze(0)
        # check if there is multiple rounds
        periods = video_clip.shape[2] // 32
        video_embedding = []
        video_mixed_5c = []
        for i in range(periods):
            # get the start and end index of the current round
            start_index = i * 32
            end_index = (i + 1) * 32
            # get the current round
            current_round = video_clip[:, :, start_index:end_index, :, :]
            # get the video encoding
            current_round = current_round.to(self.device)
            with torch.no_grad():
                # get the video encoding
                current_round_output = self.net(current_round)
                # offload current_round_output to cpu
                current_round = current_round.to("cpu")
                current_round = None
                del current_round
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                # offload current_round_output to cpu
                video_embedding_cur = current_round_output['video_embedding'].cpu()
                video_mixed_5c_cur = current_round_output["mixed_5c"].cpu()
                
                video_embedding.append(video_embedding_cur)
                video_mixed_5c.append(video_mixed_5c_cur)
        # use torch to take the average of the video_embedding and video_mixed_5c
        video_embedding = torch.cat(video_embedding, dim=0)
        video_mixed_5c = torch.cat(video_mixed_5c, dim=0)
        video_embedding = torch.mean(video_embedding, dim=0, keepdim=True)
        video_mixed_5c = torch.mean(video_mixed_5c, dim=0, keepdim=True)
        return video_embedding, video_mixed_5c
    
    def get_stacked_text_encoding(self, text_list):
        def generate_text_input():
            for text_input in tqdm(text_list):
                vec = self._get_text_encoding(text_input)
                yield vec
                del vec
                # collect the memory allocated
                gc.collect()
                
        # stack the video clips on the first dimension
        text_mat = torch.cat(list(generate_text_input()))
        return text_mat

    def _get_text_encoding(self, text_input):
        # put net on cpu
        self.net = self.net.to("cpu")
        with torch.no_grad():
            text_output = self.net.text_module([text_input])    
        # offload text_output to cpu
        text_output_vec = text_output['text_embedding'].cpu()
        return text_output_vec
    
    def calc_similarity(self, text_mat, vid_mat):
        # calculate the similarity between video and text
        similarity = torch.matmul(text_mat, vid_mat.t())
        # text_norm = torch.norm(text_mat, dim=1)
        # vid_norm = torch.norm(vid_mat, dim=1)
        # norm_product = torch.outer(text_norm, vid_norm)
        # cosine_similarity = similarity / norm_product

        # note here do not calculate cosine similarity due to MIL-NCE is optimize on pair-wise similarity
        return similarity