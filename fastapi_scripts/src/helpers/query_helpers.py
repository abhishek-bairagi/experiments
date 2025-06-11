from src.constants import  product_extraction_prompt_path
from src.helpers.llm_helpers import generate_text
import re
from logging_conf.logging_helpers import logger

def classify_product_and_subtopic(query, product_data):
    """
    Classify the product and subtopic from the given query using a prompt.

    Args:
        query (str): The user query.
        product_data (str): The product data string.

    Returns:
        dict: The classification result in the specified format.
    """
    function_name = "classify_product_and_subtopic"
    try:
        # Read the prompt from the product_extraction_prompt_path file
        with open(product_extraction_prompt_path, 'r') as prompt_file:
            prompt = prompt_file.read()

        # Read the product data from the product_data file
        full_prompt = prompt.format(product_data=product_data, query=query)
        response = generate_text(full_prompt)

        def parser(response):
            product_match = re.search(r'<product>(.*?)</product>', response)
            subtopic_match = re.search(r'<subtopic>(.*?)</subtopic>', response)
            product = product_match.group(1) if product_match else ""
            subtopic = subtopic_match.group(1) if subtopic_match else ""
            return product, subtopic
        logger.info(f"{function_name}: LLM response - {response}")
        product, subtopic = parser(response)
        logger.info(f"{function_name}: Successfully classified product and subtopic.")
        return {
            "product": product.strip(),
            "subtopic": subtopic.strip()
        }
    except Exception as e:
        logger.error(f"{function_name}: Error occurred - {str(e)}")
        return {
            "product": "",
            "subtopic": ""
        }
# query = "blah blah blah"
# classification_result = classify_product_and_subtopic(query, product_data)

