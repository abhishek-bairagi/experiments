import re
import json

def sanitize_json(json_str):
    return re.sub(r'\x00', '', json_str)  # Remove null characters or other invalid control chars

def extract_json_dict(s):
    pattern = re.compile(r'\{(?:[^{}]*|\{[^{}]*\})*\}')
    match = pattern.search(s)
    if match:
        json_str = sanitize_json(match.group())
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

# Example Usage
s = "Some text before {\"key\": \"value\", \"num\": 42} some text after"
parsed_dict = extract_json_dict(s)
print(parsed_dict)
