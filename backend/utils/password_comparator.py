import secrets
import string
import math

# Function to generate a random traditional password
def generate_traditional_password(length=12):
    charset = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(charset) for _ in range(length))

# Function to calculate entropy of a password
def calculate_entropy(password):
    charset = len(set(password))  # Unique characters in the password
    entropy = math.log2(charset ** len(password))
    return entropy

# Function to simulate brute-force difficulty
def brute_force_complexity(password):
    charset_size = len(set(password))  # Unique characters in the password
    possible_combinations = charset_size ** len(password)
    estimated_time = possible_combinations / (10**9)  # Assuming 1 billion guesses per second
    return estimated_time  # In seconds

# Function to compare AI vs. Traditional passwords
def compare_passwords(ai_passwords, num_traditional=10):
    traditional_passwords = [generate_traditional_password() for _ in range(num_traditional)]
    
    results = []
    for pwd in traditional_passwords:
        results.append({
            "Type": "Traditional",
            "Password": pwd,
            "Entropy": calculate_entropy(pwd),
            "Brute-Force Time (s)": brute_force_complexity(pwd)
        })

    for pwd in ai_passwords:
        results.append({
            "Type": "AI-Generated",
            "Password": pwd,
            "Entropy": calculate_entropy(pwd),
            "Brute-Force Time (s)": brute_force_complexity(pwd)
        })

    return results
