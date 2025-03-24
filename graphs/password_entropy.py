import matplotlib.pyplot as plt
import numpy as np

# Password categories and their entropy values from your results
categories = ['Weak1\n(password123)', 'Weak2\n(123456)', 'Medium1\n(P@ssw0rd!)', 
              'Medium2\n(Summer2021!)', 'Strong1\n(xT5$9pL#2qR@7)', 
              'Very Strong\n(K8^p2L!...)', 'AI-Generated\n(Average)']

# Entropy values (bits) - estimate the average AI-generated based on your data
entropy_values = [56.9, 19.9, 59.1, 72.3, 85.4, 131.4, 90.0]  # Replace 90.0 with actual average

# Status (cracked or not)
cracked_status = [True, True, True, False, False, False, False]

# Create custom colors based on cracked status
colors = ['#FF6666' if status else '#66CC66' for status in cracked_status]

# Create the bar chart
fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.bar(categories, entropy_values, color=colors)

# Add value labels above bars
for bar, value in zip(bars, entropy_values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 5,
            f'{value:.1f}', ha='center', va='bottom')

# Add a horizontal line for recommended minimum entropy (about 70 bits)
ax.axhline(y=70, color='r', linestyle='--', label='Recommended Minimum (70 bits)')

# Customize the chart
ax.set_ylabel('Entropy (bits)')
ax.set_title('Password Entropy Comparison')
ax.legend()

# Add cracked/uncracked indicator
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#FF6666', markersize=15, label='Cracked'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#66CC66', markersize=15, label='Uncracked')
]
ax.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig('password_entropy.png')
plt.show()