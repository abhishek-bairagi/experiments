class MasterAgent:
    def __init__(self, product_list: list):
        self.product_list = product_list
        self.chat_history = []
        self.attempts = 0

    def identify_intent(self, user_message: str) -> str:
        prompt = f"""
        You are a supporting agent for Tech-care chatbot, which helps colleagues with different software and product-related issues.
        Identify the intent of the given user message from the following categories: Greeting, Goodbye, Chitchat, Connect to an engineer, Technical query.
        
        User: {user_message}
        Intent:
        """
        response = call_llm(prompt)
        return response.strip()

    def determine_flag_followup(self, user_message: str) -> dict:
        prompt = f"""
        You are a supporting agent for Tech-care chatbot. Determine whether the user's technical query contains both product and issue details.
        
        User: {user_message}
        Response:
        """
        response = call_llm(prompt)
        return response.strip()

    def extract_product_issue(self, user_message: str) -> dict:
        prompt = f"""
        You are a supporting agent for Tech-care chatbot. Extract the product and issue from the given technical query.
        Select the product from the following list: {', '.join(self.product_list)}.
        
        User: {user_message}
        Response:
        """
        response = call_llm(prompt)
        return response.strip()

    def generate_combined_query(self) -> str:
        prompt = f"""
        You are a supporting agent for Tech-care chatbot. Consolidate the chat history into a single, clear technical query.
        
        Chat history:
        {self.chat_history}
        
        Consolidated message:
        """
        response = call_llm(prompt)
        return response.strip()

    def handle_user_message(self, user_message: str) -> dict:
        self.chat_history.append(f"User: {user_message}")
        
        flag_data = self.determine_flag_followup(user_message)
        
        if flag_data["flag"] == "complete":
            product_issue_data = self.extract_product_issue(user_message)
            return {"product": product_issue_data["product"], "issue": product_issue_data["issue"], "message": "Thank you for providing the details, let me search the answer."}
        
        if self.attempts < 2:
            self.attempts += 1
            follow_up = flag_data["follow_up_message"]
            self.chat_history.append(f"Bot: {follow_up}")
            return {"product": None, "issue": None, "message": follow_up}
        
        consolidated_query = self.generate_combined_query()
        product_issue_data = self.extract_product_issue(consolidated_query)
        return {"product": product_issue_data.get("product"), "issue": product_issue_data.get("issue"), "message": "Unable to determine the product and issue after multiple attempts."}
