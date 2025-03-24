import matplotlib.pyplot as plt
import numpy as np

# Data from your test results
categories = ['Test Passwords', 'Weak Benchmarks', 'Medium Benchmarks', 'Strong Benchmarks', 'AI-Generated']
cracked = [4, 2, 1, 0, 0]  # Number cracked in each category
total = [5, 2, 2, 2, 20]   # Total in each category

# Calculate percentages
percentages = [100 * c / t for c, t in zip(cracked, total)]

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))

# Create a horizontal bar chart
ax.barh(categories, percentages, color=['#FF9999', '#FF9999', '#FFCC99', '#99CCFF', '#99FF99'])

# Add percentage labels
for i, v in enumerate(percentages):
    ax.text(v + 1, i, f"{v:.1f}%", va='center')

# Add count labels
for i, (c, t) in enumerate(zip(cracked, total)):
    ax.text(1, i, f"{c}/{t}", va='center', ha='left', color='white', fontweight='bold')

ax.set_xlim(0, 105)
ax.set_xlabel('Crack Success Rate (%)')
ax.set_title('Password Cracking Success Rate by Category')
plt.tight_layout()
plt.savefig('crack_success_rate.png')
plt.show()