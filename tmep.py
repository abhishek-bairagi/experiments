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
