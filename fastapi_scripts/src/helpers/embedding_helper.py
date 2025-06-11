from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from src.constants import embedding_model_path

def embed(text):
    tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)
    model = AutoModel.from_pretrained(embedding_model_path)
    # model = SentenceTransformer(embedding_model_path)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embedding[0]