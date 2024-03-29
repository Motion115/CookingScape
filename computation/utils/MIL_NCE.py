import gc
import time
import torch
from utils.S3D.s3dg import S3D
import cv2
import numpy as np
import torchvision.transforms.functional as F
import os
from tqdm import tqdm

class MIL_NCE:
    def __init__(self, weight_filepath, dictionary_filepath):
        self.weight_filepath = weight_filepath
        self.dictionary_filepath = dictionary_filepath
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = self.load_model()

    def load_model(self):
        net = S3D(self.dictionary_filepath)
        net.load_state_dict(torch.load(self.weight_filepath))
        # Move the model to the GPU
        net = net.to(self.device)
        # Evaluation mode
        net = net.eval()
        return net
    
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
            frames = frames[:32]
        # check if there is 32 tensors, if not, repeat the last one, else, truncate
        # if len(frames) < 16:
        #     for i in range(16 - len(frames)):
        #         frames.append(frames[-1])
        # else:
        #     frames = frames[:16]

        # Convert the list of frames to a PyTorch tensor
        video_tensor = torch.stack(frames)

        # Print the shape of the video tensor
        # switch the first two dimensions, original (T, C, H, W)
        video_tensor = video_tensor.permute(1, 0, 2, 3)
        # print(video_tensor.shape)  # (C, T, H, W)
        # Release the video capture object
        video_capture.release()
        return video_tensor
    
    def get_stacked_encoding(self, base_dir, video_clips_paths):
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
        # load video_clip to gpu
        video_clip = video_clip.to(self.device)
        with torch.no_grad():
            # get the video encoding
            video_output = self.net(video_clip)
            video_clip = video_clip.to("cpu")
            video_clip = None
            del video_clip
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        # offload video_output to cpu
        video_embedding = video_output['video_embedding'].cpu()
        video_mixed_5c = video_output["mixed_5c"].cpu()
        # mixed_5c is for classification
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
        topk_values, topk_indices = torch.topk(similarity, 10, dim=1)
        print(topk_values)
        print("---")
        print(topk_indices)
        return similarity