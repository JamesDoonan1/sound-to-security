import matplotlib.pyplot as plt
import numpy as np

# Attack methods and success rates from your test results
attack_methods = ['Basic Dictionary', 'Enhanced Dictionary', 'Simple Mask', 'Complex Pattern']

# For each category, show how many were cracked by which method
categories = ['Test Passwords', 'Benchmarks', 'AI-Generated']

# This data comes from your detailed_test_results.json
# Format: [method1_success, method2_success, method3_success, method4_success]
success_data = [
    [3, 1, 0, 0],  # Test passwords cracked by each method
    [3, 0, 0, 0],  # Benchmark passwords cracked by each method
    [0, 0, 0, 0]   # AI-generated passwords cracked by each method
]

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 8))

bottom = np.zeros(len(categories))
for i, method in enumerate(attack_methods):
    values = [row[i] for row in success_data]
    ax.bar(categories, values, bottom=bottom, label=method)
    bottom += values

# Add the total number tested for each category
totals = [5, 6, 20]  # Total passwords in each category
for i, total in enumerate(totals):
    ax.text(i, 0.1, f'Total: {total}', ha='center', va='bottom', color='black', fontweight='bold')

ax.set_ylabel('Number of Passwords Cracked')
ax.set_title('Password Cracking Success by Attack Method')
ax.legend()

plt.tight_layout()
plt.savefig('attack_success.png')
plt.show()