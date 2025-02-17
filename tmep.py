def determine_flag_followup(self, user_message: str) -> dict:
    prompt = """
    You are a support agent for the Tech-care chatbot. Your task is to determine whether a user's technical query provides enough details to proceed. Specifically, check if the query includes:
    - A product, platform, or service (explicitly named or clearly implied).
    - A specific issue or concern related to it.

    Guidelines:  
    - The chatbot supports various platforms, including but not limited to:  
      'slack', 'webex', 'ads', 'outlook', 'avaya', 'mac', 'virtualdesktop', 'windows', 'clic', 'gsp', 'cvp', 'gdm', 'csp', 'okta', 'cmd', 'byod', 'onedrive', 'peripherals', 'vpn', 'browser', 'genesys', 'opus'.  
      However, do not restrict recognition to this list—other relevant products and services should also be considered valid.
    - Be lenient: If there is a reasonable indication of both a product and an issue, mark the query as complete.
    - If either the product/platform or the issue is missing, mark the query as incomplete and request clarification.

    Response Format:  
    Return a Python dictionary using curly brackets with:  
    - `"flag"`: `"complete"` if both a product/platform and an issue are mentioned; otherwise, `"incomplete"`.  
    - `"follow_up_message"`:  
      - If `"complete"`, confirm receipt of the details.  
      - If `"incomplete"`, ask the user for the missing information.  

    Important: Even though the output is explained with square brackets `[]`, you should respond using curly brackets `{}` to return the dictionary format.

    Examples:  
    {sample_examples}

    User Query:  
    User: {user_message}  
    Response:
    """

    sample_examples = """  
    User: My Outlook is not syncing emails.  
    Response: ["flag": "complete", "follow_up_message": "Thank you for providing the details, let me search for an answer."]  
    (Why? The product 'Outlook' and issue 'not syncing emails' are both mentioned.)  

    User: I can't log in, please help.  
    Response: ["flag": "incomplete", "follow_up_message": "Can you specify which product you're facing issues with?"]  
    (Why? The issue is mentioned, but no product.)  

    User: I'm facing issues with Slack.  
    Response: ["flag": "incomplete", "follow_up_message": "Can you specify what issues you're facing with Slack?"]  
    (Why? The product is mentioned, but the issue is unclear.)  

    User: My Zoom audio is not working.  
    Response: ["flag": "complete", "follow_up_message": "Thank you for providing the details, let me search for an answer."]  
    (Why? The product 'Zoom' and the issue 'audio not working' are both present.)  
    """

    response = call_llm(prompt.format(user_message=user_message, sample_examples=sample_examples))
    return extract_dict(response)
