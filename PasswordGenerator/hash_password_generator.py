import numpy as np
import hashlib

from audio_feature_extraction import extract_features 

def create_hash(features):
    """
    Creates a unique hash based on the extracted features.
    """
    concatenated_features = np.concatenate([value for value in features.values()])
    feature_bytes = concatenated_features.tobytes()
    audio_hash = hashlib.md5(feature_bytes).hexdigest()
    return audio_hash