import logging
from src.helpers.es_helpers import semantic_search, format_search_results
from src.helpers.kg_helpers import *
from src.constants import vanilla_rag_prompt_path, kg_rag_prompt_path, product_data_path
from src.helpers.llm_helpers import generate_text
from src.helpers.query_helpers import classify_product_and_subtopic
from logging_conf.logging_helpers import logger


def kg_pipeline_query(query, user_id):
    """
    Process a query by performing semantic search, retrieving KG data, and generating responses.

    Args:
        query (str): The user query.
        user_id (str): The user ID.

    Returns:
        dict: A dictionary containing vanilla response, KG+RAG response, retrieved articles, and structured KG output.
    """
    logger.info("Starting pipeline query processing.")
    
    # Reading prompts
    logger.info("Reading prompts from files.")
    with open(vanilla_rag_prompt_path, 'r') as file:
        vanilla_prompt_universal = file.read()
    with open(kg_rag_prompt_path, 'r') as file:
        kg_prompt_universal = file.read()
    
    # Reading product data
    logger.info("Reading product data from file.")
    with open(product_data_path, 'r') as file:
        product_data = file.read()
    
    # Classify product and subtopic from the query
    logger.info("Classifying product and subtopic from the query.")
    classification_result = classify_product_and_subtopic(query, product_data)
    product = classification_result['product']
    subtopic = classification_result['subtopic']
    logger.info(f"Classification result: Product - {product}, Subtopic - {subtopic}")
    
    # Perform semantic search
    logger.info("Performing semantic search.")
    retrieved_articles, titles = semantic_search(query + " " + product + " " + subtopic, top_k=5)
    formatted_retrieved_articles = format_search_results(retrieved_articles)
    logger.info(f"Retrieved {len(retrieved_articles)} articles from semantic search.")
    
    # Retrieve user profile from KG
    logger.info("Retrieving user profile from KG.")
    user_profile = get_user_device_relationship(user_id)
    formatted_user_profile = format_user_details(user_profile, user_id)
    # Log user profile details
    logger.info(f"User profile retrieved: {formatted_user_profile}")
    
    # Retrieve product details with outages from KG
    logger.info("Retrieving product details with outages from KG.")
    product_details_with_outages = get_product_details_with_outages(product)
    logger.info(f"Retrieved product details with outages: {product_details_with_outages}")
    formatted_product_details = format_product_details_with_outages(product_details_with_outages)
    
    # Retrieve subtopic details from KG
    logger.info("Retrieving subtopic details from KG.")
    subtopic_details = get_subtopic_details(product_name=product, subtopic_name=subtopic)
    formatted_subtopic_details = universal_formatting_function(subtopic_details)
    # Log subtopic details
    logger.info(f"Subtopic details retrieved: {formatted_subtopic_details}")
    # Retrieve relevant issues with articles from KG
    logger.info("Retrieving relevant issues with articles from KG.")
    relevant_issues_with_articles = get_relevant_issues_with_articles(
        product_name=product,
        subtopic_name=subtopic,
        query_text=query,
        threshold=0.3,
        top_k=5
    )
    formatted_relevant_issues = format_issues_with_articles(relevant_issues_with_articles)
    # Log relevant issues with articles
    logger.info(f"Relevant issues with articles retrieved: {formatted_relevant_issues}")
    # Generate structured KG output
    logger.info("Generating structured KG output.")
    input_data = {
        "User Profile": formatted_user_profile,
        "Product Details": formatted_product_details,
        "Subtopic Details": formatted_subtopic_details,
        "Relevant Issues": formatted_relevant_issues,
    }
    structured_kg_output = generate_structured_kg_output(input_data)
    
    # Generate G+RAG prompts
    logger.info("Generating  KG+RAG prompt.")
    kg_prompt = kg_prompt_universal.format(user_query=query, kg_input=structured_kg_output, context=formatted_retrieved_articles)
    
    # Generate responses
    logger.info("Generating responses using LLM.")
    kg_response = generate_text(kg_prompt)
    
    logger.info("Pipeline query processing completed.")
    
    # Return results as a dictionary
    return {
        "kg_response": kg_response,
        "retrieved_articles": titles,
        "structured_kg_output": structured_kg_output
    }


def rag_pipeline_query(query, user_id):
    """
    Process a query by performing semantic search, retrieving KG data, and generating responses.

    Args:
        query (str): The user query.
        user_id (str): The user ID.

    Returns:
        dict: A dictionary containing vanilla response, KG+RAG response, retrieved articles, and structured KG output.
    """
    logger.info("Starting pipeline query processing.")
    
    # Reading prompts
    logger.info("Reading prompts from files.")
    with open(vanilla_rag_prompt_path, 'r') as file:
        vanilla_prompt_universal = file.read()
    
    # Perform semantic search
    logger.info("Performing semantic search.")
    retrieved_articles, titles = semantic_search(query, top_k=5)
    formatted_retrieved_articles = format_search_results(retrieved_articles)
    logger.info(f"Retrieved {len(retrieved_articles)} articles from semantic search.")
    
    # Generate vanilla and KG+RAG prompts
    logger.info("Generating vanilla prompt.")
    vanilla_prompt = vanilla_prompt_universal.format(user_query=query, context=formatted_retrieved_articles)
    
    logger.info("Generating responses using LLM.")
    vanilla_response = generate_text(vanilla_prompt)
    
    logger.info("Pipeline query processing completed.")
    
    # Return results as a dictionary
    return {
        "vanilla_response": vanilla_response,
        "retrieved_articles": titles
    }
