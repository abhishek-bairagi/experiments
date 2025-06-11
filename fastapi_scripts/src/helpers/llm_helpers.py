from google import genai
client = genai.Client(api_key="")
import json

def generate_text(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    # print(response.text)
    return response.text[7:-3]  if '```json' in response.text  else  response.text

# generate_text('hi')