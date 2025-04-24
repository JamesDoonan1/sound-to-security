"""
This script compares your audio-based password generation system with traditional
password generation methods and other authentication approaches.
"""

from password_analysis_utils import (
    get_project_paths, load_audio_passwords, calculate_entropy,
    ensure_test_results_dir, save_json_results, save_plot, format_time_estimate
)
import numpy as np
import matplotlib.pyplot as plt
import string
import secrets
import random
import pandas as pd
import seaborn as sns
import os

def generate_traditional_password(length=12):
    """Generate a traditional random password using Python's secrets module."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_readable_password(length=12):
    """Generate a more readable password with patterns (like those from password managers)."""
    words = ["apple", "banana", "orange", "grape", "melon", "cherry", "peach", "lemon", 
             "plum", "berries", "kiwi", "mango", "lime", "coconut", "fig", "date"]
    
    digits = "0123456789"
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Choose a random word
    word = random.choice(words).capitalize()
    
    # Add some digits
    word += ''.join(random.choice(digits) for _ in range(3))
    
    # Add a symbol
    word += random.choice(symbols)
    
    # Pad to required length if needed
    while len(word) < length:
        word += random.choice(string.ascii_lowercase)
    
    # Truncate if too long
    return word[:length]

def generate_diceware_password(num_words=4):
    """Generate a diceware-style password (word-based)."""
    words = ["apple", "banana", "orange", "grape", "melon", "cherry", "peach", "lemon", 
             "plum", "berries", "kiwi", "mango", "lime", "coconut", "fig", "date",
             "cat", "dog", "bird", "fish", "lion", "tiger", "bear", "wolf", "fox",
             "red", "blue", "green", "black", "white", "purple", "yellow", "orange"]
    
    selected_words = [random.choice(words) for _ in range(num_words)]
    
    # Add a number and symbol
    password = "-".join(selected_words)
    password += str(random.randint(0, 999))
    password += random.choice("!@#$%^&*")
    
    return password

def analyze_password_security(passwords):
    """Analyze various security aspects of a set of passwords."""
    if not passwords:
        return {"error": "No passwords provided"}
    
    # Remove any None or empty passwords
    valid_passwords = [p for p in passwords if p]
    
    results = {
        "count": len(valid_passwords),
        "length": {
            "mean": np.mean([len(p) for p in valid_passwords]),
            "min": min([len(p) for p in valid_passwords]),
            "max": max([len(p) for p in valid_passwords])
        },
        "entropy": {
            "individual": [calculate_entropy(p) for p in valid_passwords],
            "mean": np.mean([calculate_entropy(p) for p in valid_passwords]),
            "per_char": np.mean([calculate_entropy(p) / len(p) for p in valid_passwords])
        },
        "character_classes": {
            "uppercase_pct": np.mean([sum(1 for c in p if c.isupper()) / len(p) * 100 for p in valid_passwords]),
            "lowercase_pct": np.mean([sum(1 for c in p if c.islower()) / len(p) * 100 for p in valid_passwords]),
            "digits_pct": np.mean([sum(1 for c in p if c.isdigit()) / len(p) * 100 for p in valid_passwords]),
            "symbols_pct": np.mean([sum(1 for c in p if not c.isalnum()) / len(p) * 100 for p in valid_passwords])
        },
        "uniqueness": len(set(valid_passwords)) / len(valid_passwords) * 100,
        "patterns": {}
    }
    
    # Add total entropy metrics and theoretical maximum
    avg_length = results["length"]["mean"]
    results["entropy"]["total"] = results["entropy"]["mean"]  # Already calculated, just rename for clarity
    results["entropy"]["theoretical_max"] = np.log2(95) * avg_length
    results["entropy"]["ratio_to_max"] = results["entropy"]["total"] / results["entropy"]["theoretical_max"]
    
    # Calculate theoretical password space
    # Use 2^entropy for possible combinations based on actual entropy
    results["theoretical_combinations"] = 2 ** results["entropy"]["mean"]
    
    # Calculate time to crack estimates
    cracking_speeds = {
        "slow": 1e3,       # 1 thousand attempts per second
        "moderate": 1e6,    # 1 million attempts per second
        "fast": 1e9,        # 1 billion attempts per second
        "extreme": 1e12     # 1 trillion attempts per second
    }
    
    results["crack_time_seconds"] = {}
    for speed_name, attempts_per_second in cracking_speeds.items():
        seconds = results["theoretical_combinations"] / attempts_per_second
        results["crack_time_seconds"][speed_name] = seconds
    
    return results

def compare_password_systems(audio_passwords, num_comparison_passwords=500):
    """Compare audio-based passwords with other password generation approaches."""
    print("Generating comparison passwords...")
    
    # Generate comparison password sets
    traditional_passwords = [generate_traditional_password() for _ in range(num_comparison_passwords)]
    readable_passwords = [generate_readable_password() for _ in range(num_comparison_passwords)]
    diceware_passwords = [generate_diceware_password() for _ in range(num_comparison_passwords)]
    
    print("Analyzing password sets...")
    
    # Sample audio passwords to match comparison size
    if len(audio_passwords) > num_comparison_passwords:
        sampled_audio_passwords = random.sample(audio_passwords, num_comparison_passwords)
    else:
        sampled_audio_passwords = audio_passwords
    
    # Analyze each password set
    results = {
        "audio": analyze_password_security(sampled_audio_passwords),
        "traditional": analyze_password_security(traditional_passwords),
        "readable": analyze_password_security(readable_passwords),
        "diceware": analyze_password_security(diceware_passwords)
    }
    
    return results

def visualize_comparison(comparison_results, output_path="password_system_comparison.png"):
    """Create visualizations comparing different password systems."""
    # Extract key metrics for each system
    systems = list(comparison_results.keys())
    
    # Prepare data for key metrics
    metrics = {
        "Entropy (bits)": [comparison_results[system]["entropy"]["mean"] for system in systems],
        "Entropy/Char (bits)": [comparison_results[system]["entropy"]["per_char"] for system in systems],
        "Password Length": [comparison_results[system]["length"]["mean"] for system in systems],
        "Uniqueness (%)": [comparison_results[system]["uniqueness"] for system in systems],
        "Theoretical Maximum Entropy (bits)": [comparison_results[system]["entropy"]["theoretical_max"] for system in systems],
        "Entropy Utilization Ratio": [comparison_results[system]["entropy"]["ratio_to_max"] for system in systems]
    }
    
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Password System Comparison', fontsize=16)
    
    # Plot key metrics as bar charts
    plot_positions = [(0, 0), (0, 1), (1, 0)]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, (metric, values) in enumerate(list(metrics.items())[:3]):  # First 3 metrics
        row, col = plot_positions[i]
        bars = axs[row, col].bar(systems, values, color=colors)
        axs[row, col].set_title(metric)
        axs[row, col].set_ylabel(metric)
        
        # Set appropriate scale for entropy plots
        if "entropy" in metric.lower():
            max_val = max(values)
            axs[row, col].set_ylim(0, max(80, max_val * 1.2))
        else:
            axs[row, col].set_ylim(bottom=0)
        
        # Add the values on top of the bars
        for bar in bars:
            height = bar.get_height()
            axs[row, col].text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
    
    # Character class distribution as stacked bar chart
    ax_chars = axs[1, 1]
    ax_chars.set_title('Character Class Distribution')
    
    # Prepare character class data
    char_class_data = []
    for system in systems:
        char_class_data.append([
            comparison_results[system]["character_classes"]["uppercase_pct"],
            comparison_results[system]["character_classes"]["lowercase_pct"],
            comparison_results[system]["character_classes"]["digits_pct"],
            comparison_results[system]["character_classes"]["symbols_pct"]
        ])
    
    char_class_data = np.array(char_class_data)
    char_classes = ['Uppercase', 'Lowercase', 'Digits', 'Symbols']
    
    # Create stacked bar chart
    bottom = np.zeros(len(systems))
    for i, class_name in enumerate(char_classes):
        ax_chars.bar(systems, char_class_data[:, i], bottom=bottom, label=class_name)
        bottom += char_class_data[:, i]
    
    ax_chars.set_ylabel('Percentage (%)')
    ax_chars.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
    
    # Save the figure
    save_plot(fig, output_path)

def compare_with_biometric_systems():
    """Provides a qualitative comparison with other biometric authentication methods."""
    # Data from various security research sources (approximate values)
    biometric_comparison = {
        "methods": [
            "Audio Password (Your System)",
            "Fingerprint",
            "Face Recognition",
            "Voice Recognition",
            "Iris Scan",
            "Traditional Password"
        ],
        "metrics": {
            "false_acceptance_rate": [
                "Variable (depends on AI accuracy)",  # Your system
                "0.1% - 1%",                          # Fingerprint
                "0.1% - 5%",                          # Face Recognition
                "2% - 5%",                            # Voice Recognition
                "0.0001% - 0.01%",                    # Iris Scan
                "N/A"                                 # Traditional Password
            ],
            "false_rejection_rate": [
                "Variable (depends on audio similarity)",  # Your system
                "1% - 5%",                                # Fingerprint
                "2% - 15%",                               # Face Recognition
                "5% - 10%",                               # Voice Recognition
                "0.5% - 2%",                              # Iris Scan
                "N/A (except forgotten passwords)"        # Traditional Password
            ],
            "user_convenience": [
                "Medium (requires audio)",       # Your system
                "High",                          # Fingerprint
                "High",                          # Face Recognition
                "Medium",                        # Voice Recognition
                "Low (requires special reader)",  # Iris Scan
                "Low (need to remember)"         # Traditional Password
            ],
            "security_level": [
                "Medium-High",  # Your system
                "Medium",       # Fingerprint
                "Medium",       # Face Recognition
                "Medium-Low",   # Voice Recognition
                "Very High",    # Iris Scan
                "Variable"      # Traditional Password
            ],
            "spoofing_resistance": [
                "High (requires specific audio)",  # Your system
                "Medium-High",                     # Fingerprint
                "Low-Medium",                      # Face Recognition
                "Low",                             # Voice Recognition
                "High",                            # Iris Scan
                "Low-Medium"                       # Traditional Password
            ],
            "privacy_concerns": [
                "Low (audio not stored)",     # Your system
                "High (stored biometric)",    # Fingerprint
                "High (stored biometric)",    # Face Recognition
                "High (stored biometric)",    # Voice Recognition
                "High (stored biometric)",    # Iris Scan
                "Low (if hashed properly)"    # Traditional Password
            ]
        }
    }
    
    # Create a comparison table as a DataFrame
    df = pd.DataFrame(biometric_comparison["metrics"], index=biometric_comparison["methods"])
    
    # Save as CSV
    test_results_dir = ensure_test_results_dir()
    df.to_csv(os.path.join(test_results_dir, "biometric_comparison.csv"))
    
    # Create a visualization
    plt.figure(figsize=(12, 8))
    
    # Convert categorical values to numeric scores for visualization
    security_map = {
        "Very High": 5, "High": 4, "Medium-High": 3.5, "Medium": 3, 
        "Medium-Low": 2.5, "Low": 2, "Very Low": 1, "Variable": 3, "N/A": 0
    }
    
    # Create a new DataFrame with numeric values where possible
    numeric_df = df.copy()
    for col in ["security_level", "spoofing_resistance", "user_convenience", "privacy_concerns"]:
        numeric_df[col] = [security_map.get(val, 3) for val in df[col]]
    
    # Only keep columns that we've converted to numeric
    numeric_cols = ["security_level", "spoofing_resistance", "user_convenience", "privacy_concerns"]
    numeric_df = numeric_df[numeric_cols]
    
    # Create a heatmap
    fig = plt.figure(figsize=(12, 8))
    sns.heatmap(numeric_df, annot=df[numeric_cols], fmt="", cmap="YlGnBu", 
               linewidths=0.5, cbar_kws={"label": "Score (1-5)"})
    plt.title("Comparison with Biometric Authentication Methods")
    
    # Save the figure
    save_plot(fig, "biometric_comparison.png")
    
    return biometric_comparison

def main():
    # Get paths
    paths = get_project_paths()
    audio_data_path = paths["audio_data_path"]
    
    print("Starting comparative analysis of password systems...")
    
    # Load audio-generated passwords
    audio_passwords = load_audio_passwords(audio_data_path)
    
    if not audio_passwords:
        print("Error: No audio passwords found. Check the path to your audio_data.json file.")
        return
    
    # Compare with other password generation systems
    try:
        num_comparison = int(input("How many passwords to generate for comparison? (default: 200): ") or "200")
    except ValueError:
        num_comparison = 200
        print("Invalid input. Using default value of 200 passwords.")
    
    comparison_results = compare_password_systems(audio_passwords, num_comparison)
    
    # Save detailed results
    save_json_results(comparison_results, "password_comparison_results.json")
    
    # Create visualizations
    visualize_comparison(comparison_results)
    
    # Compare with biometric systems
    biometric_comparison = compare_with_biometric_systems()
    
    # Print summary
    print_summary_results(comparison_results)

def print_summary_results(comparison_results):
    """Print a summary of comparison results to the console."""
    print("\n=== Password System Comparison Results ===")
    
    for system, results in comparison_results.items():
        print(f"\n{system.upper()} PASSWORDS:")
        print(f"  Average Total Entropy: {results['entropy']['total']:.2f} bits")
        print(f"  Theoretical Maximum Entropy: {results['entropy']['theoretical_max']:.2f} bits") 
        print(f"  Entropy Utilization Ratio: {results['entropy']['ratio_to_max']:.2f}")
        print(f"  Entropy per Character: {results['entropy']['per_char']:.2f} bits/char")
        print(f"  Average Length: {results['length']['mean']:.2f} characters")
        print(f"  Character Distribution:")
        print(f"    - Uppercase: {results['character_classes']['uppercase_pct']:.1f}%")
        print(f"    - Lowercase: {results['character_classes']['lowercase_pct']:.1f}%")
        print(f"    - Digits: {results['character_classes']['digits_pct']:.1f}%")
        print(f"    - Symbols: {results['character_classes']['symbols_pct']:.1f}%")
        
        # Print crack time estimates
        seconds = results["crack_time_seconds"]["fast"]
        time_str = format_time_estimate(seconds)
        print(f"  Estimated Time to Crack (Fast Attack): {time_str}")

if __name__ == "__main__":
    import os  # Import here for the CSV export
    main()