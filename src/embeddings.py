from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the Sentence-BERT model.
        """
        # We process on CPU by default for broader compatibility in this demo, 
        # but 'device="cuda"' can be used if available.
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Converts text into a normalized dense vector embedding.
        
        Args:
            text (str): The input message.
            
        Returns:
            np.ndarray: A normalized 1D embedding vector.
        """
        # encode returns a numpy array by default
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Normalize the embedding (L2 normalization)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
