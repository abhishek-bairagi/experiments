import requests
import json
from src.constants import  es_index_name, es_url
from src.helpers.embedding_helper import embed

def semantic_search(query, top_k=5):
    """
    Perform semantic search on Elasticsearch index using query embedding.

    Args:
        query (str): The search query.
        top_k (int): Number of top results to return.

    Returns:
        tuple: A tuple containing:
            - list: List of top matching documents with their scores.
            - str: Formatted string containing all titles.
    """
    query_embedding = embed(query)
    # Generate embedding for the query
    query_embedding = [float(value) for value in embed(query)]
    # Construct the search query for Elasticsearch
    search_query = {
        "_source": ["title", "content", "keywords"],
        "size": top_k,
        "query": {
            "script_score": {
                "query": {"match": {"content": query}},
                "script": {
                    "source": "_score*2 + cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }

    # Perform the search request
    response = requests.post(
        f"{es_url}/{es_index_name}/_search",
        headers={"Content-Type": "application/json"},
        data=json.dumps(search_query)
    )

    # Check for errors
    if response.status_code != 200:
        raise Exception(f"Failed to perform search: {response.text}")

    # Parse the response
    results = response.json()["hits"]["hits"]
    formatted_titles = "\n".join([f"- {hit['_source']['title']}" for hit in results])
    return (
        [{"id": hit["_id"], "score": hit["_score"], "source": hit["_source"]} for hit in results],
        formatted_titles
    )


def format_search_results(results):
    """
    Format the search results into a readable string format.

    Args:
        results (list): List of search result dictionaries.

    Returns:
        str: Formatted string containing search results.
    """
    output = ""
    for result in results:
        output += f"<Doc>\n"
        output += f"Title: {result['source']['title']}\n"
        output += f"Content: {result['source']['content']}\n"
        output += f"</Doc>\n"
        output += "---\n"
    return output



