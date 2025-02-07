def calculate_power(h, n1, n2, alpha=0.05):
    """Compute power of the test using Cohen's h and sample sizes."""
    pooled_n = (n1 * n2) / (n1 + n2)  # Effective sample size
    z_alpha = norm.ppf(1 - alpha / 2)  # Critical value for two-tailed test (default 0.05 significance)
    z_power = abs(h) * sqrt(pooled_n) - z_alpha  # Compute test statistic for power
    return norm.cdf(z_power)  # Get power from normal distribution
