from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

class probabilityWeighting():
    def __init__(self, steps, sceneList):        
        self.sentenceBERT = SentenceTransformer("all-MiniLM-L6-v2")
        self.weighted_steps = self.get_weights(steps=steps)
        self.sceneList = sceneList

    def get_weights(self, steps):
        ret_list = []
        print("---Generating step semantic embedding")
        for step in tqdm(steps):
            vec = self.sentenceBERT.encode(step)
            ret_list.append({
                "step": step,
                "embedding": vec
            })
        return ret_list
    
    def concatenateSceneList(self):
        embedding_list = []
        for id, scene in self.sceneList.items():
            # embedding to torch data structure, 2D tensor
            embedding_list.append(torch.tensor(scene["embedding"]))
        return torch.stack(embedding_list)
    
    def getWeightingVector(self):
        scene_embedding = self.concatenateSceneList()
        for step in self.weighted_steps:
            step_vec = torch.tensor(step["embedding"])
            # add one dim
            step_vec = step_vec.unsqueeze(0)
            # calculaate similarity vector between scene_embedding and step_vec
            similarity_vector = torch.cosine_similarity(scene_embedding, step_vec, dim=1)
            step["step_similarity_vector"] = similarity_vector
        return self.weighted_steps
    
