import torch
from utils.S3D.s3dg import S3D
import cv2
import numpy as np
import torchvision.transforms.functional as F

class MIL_NCE:
    def __init__(self, weight_filepath, dictionary_filepath):
        self.weight_filepath = weight_filepath
        self.dictionary_filepath = dictionary_filepath
        self.net = self.load_model()
    
    def load_model(self):
        net = S3D(self.dictionary_filepath)
        net.load_state_dict(torch.load(self.weight_filepath))
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
        # Convert the list of frames to a PyTorch tensor
        video_tensor = torch.stack(frames)

        # Print the shape of the video tensor
        # switch the first two dimensions, original (T, C, H, W)
        video_tensor = video_tensor.permute(1, 0, 2, 3)
        # print(video_tensor.shape)  # (C, T, H, W)
        # Release the video capture object
        video_capture.release()
        return video_tensor
    
    def get_video_encoding(self, video_clip):
        # video clip is a (C, T, H, W) tensor, add another dimension
        video_clip = video_clip.unsqueeze(0)
        # get the video encoding
        video_output = self.net(video_clip)
        # mixed_5c is for classification
        return video_output['video_embedding'], video_output["mixed_5c"]
    
    def get_text_encoding(self, text_input):
        text_output = self.net.text_module([text_input])
        return text_output['text_embedding']
    
    def calc_similarity(self, video_encoding, text_encoding):
        # Calculate the cosine similarity between the video encoding and the text encoding
        similarity = torch.matmul(text_encoding, video_encoding.t())
        return similarity