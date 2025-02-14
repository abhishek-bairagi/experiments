def identify_intent(user_message: str) -> str:
    prompt = """
    You are a supporting agent for Tech-care chatbot, which helps colleagues with different software and product-related issues.
    Identify the intent of the given user message from the following categories: Greeting, Goodbye, Chitchat, Connect to an engineer, Technical query.
    
    Examples:
    User: Hello!
    Intent: Greeting
    
    User: Hi there, how’s your day?
    Intent: Greeting
    
    User: Bye, have a great day!
    Intent: Goodbye
    
    User: See you later!
    Intent: Goodbye
    
    User: What do you think about the weather today?
    Intent: Chitchat
    
    User: Do you like sports?
    Intent: Chitchat
    
    User: I need help from an engineer.
    Intent: Connect to an engineer
    
    User: Can you escalate this to a technician?
    Intent: Connect to an engineer
    
    User: My software is crashing, what should I do?
    Intent: Technical query
    
    User: How do I reset my password?
    Intent: Technical query
    
    User: {user_message}
    Intent:
    """
    
    response = call_llm(prompt)
    return response.strip()

def determine_flag_followup(user_message: str) -> dict:
    prompt = """
    You are a supporting agent for Tech-care chatbot. Your task is to determine whether the user's technical query contains both product and issue details.
    
    Definitions:
    - flag: "complete" if both product and issue are mentioned, otherwise "incomplete".
    - follow_up_message: If complete, respond with a confirmation message. If incomplete, ask for the missing details.
    
    Examples:
    User: My Outlook is not syncing emails.
    Response: {"flag": "complete", "follow_up_message": "Thank you for providing the details, let me search the answer."}
    
    User: I can't log in, please help.
    Response: {"flag": "incomplete", "follow_up_message": "Can you please specify which product you are facing issues with?"}
    
    User: My Zoom audio is not working.
    Response: {"flag": "complete", "follow_up_message": "Thank you for providing the details, let me search the answer."}
    
    User: {user_message}
    Response:
    """
    
    response = call_llm(prompt)
    return response.strip()

def extract_product_issue(user_message: str, product_list: list) -> dict:
    prompt = f"""
    You are a supporting agent for Tech-care chatbot. Your task is to extract the product and issue from a given technical query.
    The product must be selected from the following list: {', '.join(product_list)}.
    
    Definitions:
    - product: The specific software or product mentioned in the query, chosen from the provided list.
    - issue: The problem the user is facing with the product.
    
    Examples:
    User: My Outlook is not syncing emails.
    Response: {"product": "Outlook", "issue": "not syncing emails"}
    
    User: I can't log in to Zoom.
    Response: {"product": "Zoom", "issue": "can't log in"}
    
    User: My Teams call keeps dropping.
    Response: {"product": "Teams", "issue": "call keeps dropping"}
    
    User: {user_message}
    Response:
    """
    
    response = call_llm(prompt)
    return response.strip()

def generate_combined_query(chat_history: list) -> str:
    prompt = """
    You are a supporting agent for Tech-care chatbot. Your task is to consolidate the user's messages into a single, clear technical query.
    
    Given a chat history where the user first provides partial details and then responds to follow-up questions, generate a single comprehensive user message that contains both the product and issue details.
    
    Example:
    Chat history:
    User: I can't log in.
    Bot: Can you please specify which product you are facing issues with?
    User: Zoom.
    
    Consolidated message:
    "I can't log in to Zoom."
    
    Chat history:
    User: My audio is not working.
    Bot: Which product are you facing this issue with?
    User: Teams.
    
    Consolidated message:
    "My Teams audio is not working."
    
    Chat history:
    {chat_history}
    
    Consolidated message:
    """
    
    response = call_llm(prompt)
    return response.strip()

def master_agent(user_message: str, chat_history: list, product_list: list) -> dict:
    intent = identify_intent(user_message)
    
    if intent == "Technical query":
        flag_data = determine_flag_followup(user_message)
        
        if flag_data["flag"] == "complete":
            product_issue_data = extract_product_issue(user_message, product_list)
            return {"product": product_issue_data["product"], "issue": product_issue_data["issue"], "message": "Thank you for providing the details, let me search the answer."}
        else:
            return {"product": None, "issue": None, "message": flag_data["follow_up_message"]}
    
    return {"intent": intent, "message": "Non-technical query detected."}
