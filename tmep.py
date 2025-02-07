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


from rank_bm25 import BM25Okapi
from collections import Counter
import string

def get_top_words(corpus, top_n=100):
    # Tokenize the corpus into words and remove punctuation
    def tokenize(text):
        text = text.lower()
        return [word.strip(string.punctuation) for word in text.split() if word.strip(string.punctuation)]

    # Tokenize all documents in the corpus
    tokenized_corpus = [tokenize(doc) for doc in corpus]
    
    # Initialize BM25 with the tokenized corpus
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Create a Counter to store word frequencies
    word_scores = Counter()

    # Calculate the BM25 scores for all words in the corpus
    for doc in tokenized_corpus:
        for word in set(doc):  # Avoid counting the same word multiple times in the same document
            word_scores[word] += bm25.get_scores(doc)[tokenized_corpus.index(doc)]  # Sum scores for each word
    
    # Get the top N words based on BM25 scores
    top_words = [word for word, _ in word_scores.most_common(top_n)]
    
    return top_words

# Example usage
corpus = [
    "This is a sample document.",
    "This document is another example.",
    "BM25 is a ranking function used in information retrieval."
]

top_words = get_top_words(corpus)
print(top_words)


