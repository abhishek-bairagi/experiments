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

