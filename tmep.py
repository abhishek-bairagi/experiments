import pandas as pd
import scipy.stats as stats
import numpy as np
from statsmodels.stats.power import GofChisquarePower
from collections import Counter

# Function to count word occurrences per article
def count_word_article(df, top_words):
    word_article_counts = {}
    articles_set = set(df['kb_id_1']).union(set(df['kb_id_2'])).union(set(df['kb_id_3']))
    
    for _, row in df.iterrows():
        articles = [row['kb_id_1'], row['kb_id_2'], row['kb_id_3']]
        words = set(row['user_text'].split())  # Unique words in the query
        
        for word in words:
            if word in top_words:
                for article in articles:
                    if article in articles_set:  # Only consider articles present in both quarters
                        if (word, article) not in word_article_counts:
                            word_article_counts[(word, article)] = 0
                        word_article_counts[(word, article)] += 1
    
    return word_article_counts

# Compute word-article counts for both quarters
word_article_counts_q1 = count_word_article(df_new, top_words_second_half)
word_article_counts_q2 = count_word_article(df_new1, top_words_second_half)

# Collect all (word, article) pairs present in both quarters
all_pairs = set(word_article_counts_q1.keys()).intersection(set(word_article_counts_q2.keys()))

# Prepare results
data = []

for word, article in all_pairs:
    count_q1 = word_article_counts_q1.get((word, article), 0)
    count_q2 = word_article_counts_q2.get((word, article), 0)
    total_q1 = sum(word_article_counts_q1.values())
    total_q2 = sum(word_article_counts_q2.values())
    
    # Ensure non-zero total counts for valid statistical tests
    if total_q1 == 0 or total_q2 == 0:
        continue
    
    # Chi-square contingency table
    contingency_table = [[count_q1, count_q2], [total_q1 - count_q1, total_q2 - count_q2]]
    chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
    
    # Cohen's h effect size
    p1 = count_q1 / total_q1 if total_q1 > 0 else 0
    p2 = count_q2 / total_q2 if total_q2 > 0 else 0
    cohen_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
    
    # Compute statistical power
    power_analysis = GofChisquarePower()
    effect_size = abs(cohen_h)
    power = power_analysis.solve_power(effect_size=effect_size, nobs1=total_q1 + total_q2, alpha=0.05)
    
    data.append((word, article, count_q1, count_q2, p_value, cohen_h, power))

# Convert to DataFrame
p_values_df = pd.DataFrame(data, columns=['Word', 'Article', 'Count_Q1', 'Count_Q2', 'P_Value', 'Cohen_h', 'Power'])

# Sort by p-value
p_values_df = p_values_df.sort_values(by='P_Value')

# Display significant concept drift (p < 0.05)
print(p_values_df[p_values_df['P_Value'] < 0.05])
