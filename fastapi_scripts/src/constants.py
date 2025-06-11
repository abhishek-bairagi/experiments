
# Constants for Neo4j connection
kg_password = "strongpass123"
kg_uri = "bolt://localhost:7687"
kg_user = "neo4j"


# Constants for Elasticsearch
es_url = "http://localhost:9200"
es_index_name = "articles_1"


# Constants for Embedding model 
embedding_model_path = './src/models/all-MiniLM-L6-v2'

#Constants for prompt 
vanilla_rag_prompt_path  = './src/prompts/vanilla_rag_prompt.txt'
kg_rag_prompt_path = './src/prompts/kg_rag_prompt.txt'
product_extraction_prompt_path = './src/prompts/product_subtopic_classification_prompt.txt'

#Constants for data
product_data_path ='./src/data/product_data.txt'
kg_data_path = './src/data/synthetic_data.json'