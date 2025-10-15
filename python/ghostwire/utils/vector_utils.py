"""
Vector utilities for GhostWire Refractory
"""

import numpy as np


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to unit length
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm
