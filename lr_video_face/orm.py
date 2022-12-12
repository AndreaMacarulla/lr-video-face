# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_orm.ipynb.

# %% auto 0
__all__ = ['FacePair', 'ScorerModel']

# %% ../nbs/01_orm.ipynb 3
from typing import List

from sql_face.tables import FaceImage

# %% ../nbs/01_orm.ipynb 5
class FacePair:
    def __init__(self,
    first:FaceImage,
    second:FaceImage,
    same_identity:bool
    ):
        self.first = first
        self.second = second
        self.same_identity = same_identity
        self.norm_distance = compute_norm_distance()

    def distance(self, metric):
        img1_representation = np.asarray(self.first.embeddings)
        img2_representation = np.asarray(self.second.embeddings)

        if metric == 'cosine':
            distance = dst.findCosineDistance(img1_representation, img2_representation)
        elif metric == 'euclidean':
            distance = dst.findEuclideanDistance(img1_representation, img2_representation)
        elif metric == 'euclidean_l2':
            distance = dst.findEuclideanDistance(dst.l2_normalize(img1_representation),
                                                 dst.l2_normalize(img2_representation))
        else:
            raise ValueError(f"Invalid distance_metric passed {self.metric}.")

        distance = np.float64(distance)
        return distance

    
    def compute_norm_distance(self):

        emb1 = np.asarray(self.first.embeddings)
        emb2 = np.asarray(self.second.embeddings)
        norm_emb_1 = emb1 / np.linalg.norm(emb1)
        norm_emb_2 = emb2 / np.linalg.norm(emb2)

        return np.linalg.norm(norm_emb_1 - norm_emb_2) / 2

# %% ../nbs/01_orm.ipynb 6
class ScorerModel:
    def __init__(self,
    embeddingModel:str,
    metric:str
    ):
        self.embeddingModel=embeddingModel
        self.metric=metric

    def predict_proba(self, pairs: List[FacePair]):
        distances = [pair.norm_distance for pair in pairs]
        distances = np.reshape(np.asarray(distances), (-1, 1))
        # norm_dist = (distances - np.min(distances)) / (np.max(distances) - np.min(distances))
        p = np.concatenate((distances, 1 - distances), axis=1)

        return p
