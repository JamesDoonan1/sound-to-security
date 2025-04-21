import pandas as pd 
import math
import os

# Use the path of the current script file to stay in tests/ folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "rockyou_entropy_bruteforce_method_b.csv")

# Define the Rockyou passwords
rockyou_passwords = [
    "123456", "12345", "123456789", "password", "iloveyou", "1234567", "nicole", "rockyou", "12345678", "abc123",
    # ... (trimmed for brevity)
    "barbie1", "wisdom", "queenie", "priscilla"
]

# Adjusted entropy calculation (Method B)
def calculate_entropy(password):
    if not password:
        return 0
    charset = len(set(password))
    entropy = math.log2(charset ** len(password))
    return entropy

# Brute-force time estimate (Method B)
def brute_force_time(password):
    guesses_per_second = 1e9
    charset = len(set(password))
    possible_combinations = charset ** len(password)
    return possible_combinations / guesses_per_second

# Collect results
results = []
for password in rockyou_passwords:
    entropy = calculate_entropy(password)
    brute_time = brute_force_time(password)
    results.append({
        "Password": password,
        "Entropy": entropy,
        "Brute-Force Time (s)": brute_time
    })

# Save as CSV inside tests/output_results/
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_FILE, index=False)

print(results_df)
print(f"\nCSV saved to: {OUTPUT_FILE}")
