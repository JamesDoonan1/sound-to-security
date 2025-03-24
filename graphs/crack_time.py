import matplotlib.pyplot as plt
import numpy as np

# Password types and their estimated crack times in days
password_types = [
    'Lowercase (8 chars)',
    'Lowercase+Digits (8)',
    'Mixed+Digits (8)',
    'Full ASCII (8)',
    'Lowercase (12)',
    'Lowercase+Digits (12)',
    'Mixed+Digits (12)',
    'Full ASCII (12)',
    'Medium Benchmark',
    'Strong Benchmark',
    'AI-Generated (12)'
]

# Theoretical crack times in days (from your results)
crack_times = [
    2.42e-3,   # Lowercase (8)
    3.27e-2,   # Lowercase+Digits (8)
    2.53,      # Mixed+Digits (8)
    7.68e1,    # Full ASCII (8)
    1.10e3,    # Lowercase (12)
    5.48e4,    # Lowercase+Digits (12)
    3.73e7,    # Mixed+Digits (12)
    6.25e9,    # Full ASCII (12)
    1.80e5,    # Medium Benchmark (from your data)
    1.63e6,    # Strong Benchmark (from your data)
    1.0e10     # AI-Generated (estimate based on complexity)
]

# Create a logarithmic bar chart
fig, ax = plt.subplots(figsize=(14, 8))

# Create horizontal bars with log scale
bars = ax.barh(password_types, crack_times)

# Color the bars based on security levels
colors = ['#FF6666', '#FF6666', '#FFCC99', '#FFCC99', 
          '#FFCC99', '#99CCFF', '#99CCFF', '#66CC66',
          '#99CCFF', '#66CC66', '#66CC66']
for bar, color in zip(bars, colors):
    bar.set_color(color)

# Set log scale for x-axis
ax.set_xscale('log')

# Add gridlines
ax.grid(True, which="both", ls="-", alpha=0.2)

# Add value labels beside bars
for i, (bar, time) in enumerate(zip(bars, crack_times)):
    # Format the time based on magnitude
    if time < 1:
        time_str = f"{time:.2e} days"
    elif time < 365:
        time_str = f"{time:.1f} days"
    elif time < 3650:
        time_str = f"{time/365:.1f} years"
    else:
        time_str = f"{time/365:.2e} years"
    
    ax.text(bar.get_width() * 1.1, i, time_str, va='center')

# Add labels and title
ax.set_xlabel('Estimated Time to Crack (Days, Log Scale)')
ax.set_title('Theoretical Password Cracking Time Comparison')

# Add some reference lines
days_in_year = 365
ax.axvline(x=1, color='r', linestyle='--', alpha=0.5, label='1 Day')
ax.axvline(x=days_in_year, color='orange', linestyle='--', alpha=0.5, label='1 Year')
ax.axvline(x=days_in_year*100, color='g', linestyle='--', alpha=0.5, label='100 Years')

# Add legend
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig('password_crack_times.png')
plt.show()