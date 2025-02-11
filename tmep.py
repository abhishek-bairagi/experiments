prompt1= """You are an expert query classifier for a technical support chatbot. Users typically ask questions about various software applications or platforms when they encounter issues or need assistance.  

Your task is to classify each query into one of the following categories:  

### Classes:  

1. **relevant_and_complete** – The query is technical, related to the chatbot's support domain, and contains sufficient details about both:  
   - **The product or platform being referred to.**  
   - **The problem the user is facing.**  
   - **Examples:**  
     - "How do I reset the view in Outlook?"  
     - "How do I schedule a meeting in Webex?"  
     - "My VPN is not connecting. How can I fix it?"  
   - **Expected Output:**  
     ```plaintext
     <class>relevant_and_complete</class>
     ```

2. **relevant_but_needs_clarity** – The query is technical and relevant but lacks essential details about **either**:  
   - **The product/software name** (e.g., "How do I reset the view?" → Product missing)  
   - **The specific issue** (e.g., "I need help with Outlook." → Issue missing)  
   - **Examples:**  
     - "I need help with Outlook." _(Missing issue details)_  
     - "How do I reset the view?" _(Missing product name)_  
     - "I'm facing an issue. Please help." _(No product or issue mentioned)_  
   - **Expected Output:** Along with classification, provide a follow-up question to get the missing information.  
     ```plaintext
     <class>relevant_but_needs_clarity</class>  
     <followup>Could you please specify what issue you're facing with Outlook?</followup>  
     ```

### Additional Important Instructions:  

1. **Handling Vague Queries with a Product Name but No Issue:**  
   - Example:  
     - "I need help with Webex." _(Lacks issue details)_  
     - Output:  
       ```plaintext
       <class>relevant_but_needs_clarity</class>  
       <followup>What specific issue are you facing with Webex?</followup>  
       ```

2. **Handling Queries Where the Issue is Stated but Product is Missing:**  
   - Example:  
     - "How do I reset the view?" _(Lacks product name)_  
     - Output:  
       ```plaintext
       <class>relevant_but_needs_clarity</class>  
       <followup>Which software are you referring to for resetting the view?</followup>  
       ```

3. **Handling Queries With No Clear Product or Issue:**  
   - Example:  
     - "I have a problem. Please help." _(Lacks both product and issue)_  
     - Output:  
       ```plaintext
       <class>relevant_but_needs_clarity</class>  
       <followup>Could you please specify which software or platform you need help with and what issue you are facing?</followup>  
       ```

---

### Format Instructions:  
- Always return the classification inside `<class>` tags.  
- If the classification is **relevant_but_needs_clarity**, include a `<followup>` tag with a clarifying question.  

---

### Query:  
**{question}**  

### Output:  
```plaintext
<class>[CLASS]</class>  
<followup>[FOLLOWUP QUESTION, IF APPLICABLE]</followup>  
"""


prompt2 = """You are an expert product classifier for a technical support chatbot. Users typically ask questions about various software applications or platforms when they encounter issues or need assistance.  

Your task is to determine which product the query is referring to, based on a given list of products.  

### Instructions:  

1. **You will be provided with:**  
   - A **list of products** (variable) that the chatbot supports.  
   - A **user query** containing a question or issue.  

2. **Your task is to:**  
   - Identify the **most relevant product** from the given list that matches the query.  
   - If no product from the list is clearly mentioned or inferred, classify it as **none**.  

### Classification Rules:  

1. **Exact Product Match:** If the query explicitly mentions a product from the provided list, classify it under that product.  
   - **Example:**  
     - Query: "How do I reset my view in Outlook?"  
     - Given Product List: `[Outlook, Webex, VPN, Zoom]`  
     - **Output:**  
       ```plaintext
       <product>Outlook</product>
       ```

2. **Implicit Product Match:** If the query does not explicitly mention a product but strongly implies one, classify it under that product.  
   - **Example:**  
     - Query: "How do I schedule a meeting?"  
     - Given Product List: `[Outlook, Webex, VPN, Zoom]`  
     - Webex is inferred (since scheduling meetings is a common Webex feature).  
     - **Output:**  
       ```plaintext
       <product>Webex</product>
       ```

3. **Multiple Product Mentions:** If a query mentions multiple products from the list, classify based on the **primary intent** of the question.  
   - **Example:**  
     - Query: "How do I integrate Outlook with Webex?"  
     - Given Product List: `[Outlook, Webex, VPN, Zoom]`  
     - Outlook and Webex are both mentioned, but the main action is **integration with Webex**.  
     - **Output:**  
       ```plaintext
       <product>Webex</product>
       ```

4. **None Classification:** If the query does not match any product in the provided list, classify it as **none** and provide a polite clarification response.  
   - **Example:**  
     - Query: "How do I check my internet speed?"  
     - Given Product List: `[Outlook, Webex, VPN, Zoom]`  
     - No relevant product match.  
     - **Output:**  
       ```plaintext
       <product>none</product>  
       <followup>I'm sorry, but I couldn't determine a supported product from your query. Could you specify which software or platform you are referring to?</followup>  
       ```

### Guardrails:  

- **Do not assume products outside the provided list.** If a query references an unsupported product, classify it as **none**.  
- **Avoid misclassification based on generic keywords.** Example: "My microphone is not working" should not be classified under Zoom unless Zoom is mentioned or strongly implied.  
- **If a query is too vague**, classify it as **none** and ask for clarification. Example:  
  - Query: "I need help with my software."  
  - **Output:**  
    ```plaintext
    <product>none</product>  
    <followup>Could you specify which software you need help with?</followup>  
    ```

---

### Input Variables:  
- **{products}** → A dynamic list of supported products.  
- **{query}** → The user’s query.  

### Output Format:  
```plaintext
<product>[CLASSIFIED PRODUCT OR NONE]</product>  
<followup>[FOLLOWUP QUESTION, IF APPLICABLE]</followup>  
"""
