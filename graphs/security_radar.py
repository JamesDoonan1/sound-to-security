import matplotlib.pyplot as plt
import numpy as np

# Categories for radar chart
categories = ['Length', 'Entropy', 'Charset Size', 
              'Dictionary Resistance', 'Pattern Resistance', 
              'Brute Force Resistance']

# Data for different password types (normalized to 0-10 scale)
# [length, entropy, charset, dictionary, pattern, brute]
weak_pwd = [5, 2, 3, 1, 2, 1]
medium_pwd = [7, 6, 7, 6, 5, 5]
strong_pwd = [8, 8, 9, 9, 8, 8]
ai_pwd = [9, 9, 10, 10, 9, 10]

# Angle of each axis
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # Close the loop

# Radar chart setup
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Add each password type
def add_to_radar(data, color, label):
    values = data.copy()
    values += values[:1]  # Close the loop
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=color, label=label)
    ax.fill(angles, values, color=color, alpha=0.25)

# Add the data
add_to_radar(weak_pwd, '#FF6666', 'Weak Password')
add_to_radar(medium_pwd, '#FFCC99', 'Medium Password')
add_to_radar(strong_pwd, '#99CCFF', 'Strong Password')
add_to_radar(ai_pwd, '#66CC66', 'AI-Generated Password')

# Set category labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

# Set y-ticks
ax.set_yticks([2, 4, 6, 8, 10])
ax.set_yticklabels(['2', '4', '6', '8', '10'])
ax.set_ylim(0, 10)

# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

plt.title('Password Security Characteristics', size=15, y=1.1)
plt.tight_layout()
plt.savefig('password_radar.png')
plt.show()