import numpy as np
import pandas as pd
import pickle
from scipy.stats import chi2_contingency
from collections import Counter

# Load Training Data (Q4 2023)
with open("q4_23_kb_details_new.pkl", "rb") as file:
    df_train = pickle.load(file)  # Load DataFrame

# Load Test Data (Q3+Q4 2024)
with open("q3_24_kb_details_new.pkl", "rb") as file:
    df_test1 = pickle.load(file)  # Load DataFrame
with open("q4_24_kb_details_new.pkl", "rb") as file:
    df_test2 = pickle.load(file)  # Load DataFrame

df_test = pd.concat([df_test1, df_test2])

# Initialize keyword-article count dictionaries
base_words_q4_23 = {}  # Training data keyword-article counts
base_words_second_half = {}  # Test data keyword-article counts

# Extract keyword-article frequencies from Training Data
top_words = set()  # Collect unique keywords

for i, row in df_train.iterrows():
    for word in row['user_text'].split():  # Extract words from user query
        top_words.add(word)  # Store keywords for reference
        if word not in base_words_q4_23:
            base_words_q4_23[word] = Counter()
        for col in ['kb_id_1', 'kb_id_2', 'kb_id_3']:
            if row[col] != '':
                base_words_q4_23[word][row[col]] += 1  # Increment count

# Extract keyword-article frequencies from Test Data
for i, row in df_test.iterrows():
    for word in row['user_text'].split():
        if word not in base_words_second_half:
            base_words_second_half[word] = Counter()
        for col in ['kb_id_1', 'kb_id_2', 'kb_id_3']:
            if row[col] != '':
                base_words_second_half[word][row[col]] += 1  # Increment count

# Compute Total Keyword Counts in Training & Test
total_train_keywords = sum(sum(counter.values()) for counter in base_words_q4_23.values())
total_test_keywords = sum(sum(counter.values()) for counter in base_words_second_half.values())

# Compute p-values for each (keyword, article) pair
results = []

for word in top_words:
    if word not in base_words_q4_23 or word not in base_words_second_half:
        continue  # Skip words missing in either dataset
    
    for article in set(base_words_q4_23[word].keys()).union(base_words_second_half[word].keys()):
        train_count = base_words_q4_23[word].get(article, 0)  # Count in training
        test_count = base_words_second_half[word].get(article, 0)  # Count in test

        remaining_train = total_train_keywords - train_count  # Remaining keyword occurrences
        remaining_test = total_test_keywords - test_count  # Remaining keyword occurrences

        # Construct contingency table
        table = np.array([[train_count, remaining_train], [test_count, remaining_test]])

        # Perform Chi-Square Test
        chi2_stat, p_value, _, _ = chi2_contingency(table)

        # Store results
        results.append((word, article, train_count, test_count, p_value))

# Convert results to DataFrame
df_results = pd.DataFrame(results, columns=['Keyword', 'Article', 'Train Count', 'Test Count', 'p-value'])

# Display Significant Drift Results (p < 0.05)
df_drift = df_results[df_results['p-value'] < 0.05]
print(df_drift)
