import pandas as pd 
import math

# Define the Rockyou passwords
rockyou_passwords = [
    "123456", "12345", "123456789", "password", "iloveyou", "1234567", "nicole", "rockyou", "12345678", "abc123",
    "babygirl", "monkey", "lovely", "jessica", "654321", "qwerty", "111111", "iloveu", "000000", "michelle",
    "tigger", "sunshine", "chocolate", "password1", "soccer", "anthony", "friends", "butterfly", "purple", "angel",
    "jordan", "liverpool", "justin", "loveme", "fuckyou", "123123", "football", "secret", "andrea", "carlos",
    "jennifer", "joshua", "bubbles", "1234567890", "superman", "hannah", "amanda", "loveyou", "pretty", "basketball",
    "andrew", "angels", "tweety", "flower", "playboy", "hello", "elizabeth", "hottie", "tinkerbell", "charlie",
    "samantha", "barbie", "chelsea", "lovers", "teamo", "mememe", "caroline", "susana", "kristen", "baller",
    "lolita", "202020", "gerard", "undertaker", "amistad", "lollol", "edison", "ashanti", "angel12", "rocknroll",
    "cinta", "ROCKYOU", "shanice", "kagome", "sherry", "antony", "allen", "respect", "princess2", "angeleyes",
    "nemesis", "nathalie", "famous", "cedric", "wolverine", "snoopy1", "nelly", "madden", "13579", "shawty",
    "pepito", "naruto1", "lilman", "chelseafc", "blingbling", "sparkles", "honeys", "graham", "flaquita", "dalejr",
    "iforgot", "barbie1", "wisdom", "queenie", "priscilla"
]

# Adjusted entropy calculation (Method B)
def calculate_entropy(password):
    if not password:
        return 0
    charset = len(set(password))  # Unique characters in the password
    entropy = math.log2(charset ** len(password))
    return entropy

# Function to estimate brute-force time (aligned with Method B)
def brute_force_time(password):
    guesses_per_second = 1e9
    charset = len(set(password))
    possible_combinations = charset ** len(password)
    time_seconds = possible_combinations / guesses_per_second
    return time_seconds

# Create a DataFrame to store results
results = []

for password in rockyou_passwords:
    entropy = calculate_entropy(password)
    brute_time = brute_force_time(password)
    results.append({
        "Password": password,
        "Entropy": entropy,
        "Brute-Force Time (s)": brute_time
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV
results_df.to_csv("rockyou_entropy_bruteforce_method_b.csv", index=False)

# Display results
print(results_df)
