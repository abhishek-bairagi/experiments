from scipy.stats import norm

def power_from_p_value(p_value, alpha=0.05):
    """Estimate power given a p-value using inverse normal transformation."""
    Z_alpha = norm.ppf(1 - alpha / 2)  # Two-tailed test critical value
    Z_p = norm.ppf(1 - p_value / 2)  # Z-score for observed p-value
    power = 1 - norm.cdf(Z_alpha - abs(Z_p))  # Compute power
    return power

# Example p-values
p_values = [0.01, 0.05, 0.10, 0.20]

# Compute power estimates
for p in p_values:
    power = power_from_p_value(p)
    print(f"p-value: {p:.3f} → Estimated Power: {power:.3f}")


import multiprocessing

def clean_text_parallel(text_list):
    """Cleans a list of texts in parallel."""
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        cleaned_texts = pool.map(clean_text, text_list)
    return cleaned_texts

# Example usage
texts = ["Hello, World!", "  Python is great!!! ", "Let's clean this #text?"]
cleaned = clean_text_parallel(texts)
print(cleaned) 

import re
import multiprocessing
from tqdm import tqdm

def clean_text(text):
    """Cleans text by removing special characters and extra spaces."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text

def clean_text_parallel(text_list):
    """Cleans a list of texts in parallel inside a Jupyter Notebook."""
    ctx = multiprocessing.get_context("fork")  # Use 'fork' to avoid Windows issues
    with ctx.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = list(tqdm(pool.imap(clean_text, text_list), total=len(text_list)))
    return results

# Example usage inside a function in a Jupyter Notebook
def process_texts():
    texts = ["Hello, World!", "  Python is great!!! ", "Let's clean this #text?"]
    cleaned = clean_text_parallel(texts)
    print(cleaned)

# Run the function
process_texts()


import nltk
from nltk.corpus import wordnet

# Ensure WordNet is downloaded
nltk.download("wordnet")

def detect_meaningful_words(sentence):
    words = sentence.split()
    meaningful_words = []
    
    for word in words:
        # Check if the word exists in WordNet
        if wordnet.synsets(word):
            meaningful_words.append(word)
    
    return meaningful_words

# Example usage
sentence = "The ticketstatusclassification is irrelevant to this discussion, and Python is awesome."
meaningful_words = detect_meaningful_words(sentence)
print(f"Meaningful words: {meaningful_words}")


 from scipy.stats import norm

def power_from_p_value(p_value, alpha=0.05):
    """Estimate power given a p-value using inverse normal transformation."""
    Z_alpha = norm.ppf(1 - alpha / 2)  # Two-tailed test critical value
    Z_p = norm.ppf(1 - p_value / 2)  # Z-score for observed p-value
    power = 1 - norm.cdf(Z_alpha - abs(Z_p))  # Compute power
    return power

# Example p-values
p_values = [0.01, 0.05, 0.10, 0.20]

# Compute power estimates
for p in p_values:
    power = power_from_p_value(p)
    print(f"p-value: {p:.3f} → Estimated Power: {power:.3f}")


