import math
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
def compare_passwords(ai_password, traditional_passwords):
    """
    Compare AI-generated password against a list of pre-generated traditional passwords.
    Traditional passwords should be provided, not generated here.
    """
    results = []

    #  Evaluate Traditional Passwords
    for pwd in traditional_passwords:
        results.append({
            "Type": "Traditional",
            "Password": pwd,
            "Entropy": calculate_entropy(pwd),
            "Brute-Force Time (s)": brute_force_complexity(pwd)
        })

    #  Evaluate AI-Generated Password
    results.append({
        "Type": "AI-Generated",
        "Password": ai_password,
        "Entropy": calculate_entropy(ai_password),
        "Brute-Force Time (s)": brute_force_complexity(ai_password)
    })

    return results, traditional_passwords  #  Return both results and the password list
