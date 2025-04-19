"""
This script analyzes the strength of audio-generated passwords compared to
dictionary-based passwords and identifies any patterns or vulnerabilities.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import string
import random
from collections import Counter
import math

def ensure_test_results_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_results_dir = os.path.join(current_dir, "TestResults")
    if not os.path.exists(test_results_dir):
        os.makedirs(test_results_dir)
    return test_results_dir

def calculate_entropy(password):
    """
    Calculate true password strength entropy based on character set size and length.
    """
    if not password:
        return 0.0
    
    # Count which character sets are used
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_symbols = any(not c.isalnum() for c in password)
    
    # Determine character set size
    char_set_size = 0
    if has_uppercase: char_set_size += 26
    if has_lowercase: char_set_size += 26
    if has_digits: char_set_size += 10
    if has_symbols: char_set_size += 33  # Approximate for common symbols
    
    # Fall back to ASCII printable if no characters detected
    if char_set_size == 0:
        char_set_size = 95
    
    # Calculate entropy
    return math.log2(char_set_size) * len(password)

def load_audio_passwords(audio_data_path):
    """
    Load passwords from your audio_data.json file.
    """
    try:
        with open(audio_data_path, 'r') as f:
            data = json.load(f)
        
        # Extract passwords
        passwords = [entry.get("password") for entry in data if entry.get("password")]
        print(f"Loaded {len(passwords)} audio-generated passwords")
        return passwords
    except Exception as e:
        print(f"Error loading audio-generated passwords: {e}")
        return []

def load_common_words(dictionary_path, min_length=4, max_length=16, max_words=10000):
    """
    Load common words from a dictionary file to create comparison passwords.
    Simply reads lines from file and filters by length.
    """
    words = []
    word_count = 0
    
    try:
        print(f"Loading words from {dictionary_path}...")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'ascii']
        
        for encoding in encodings:
            try:
                words = []
                with open(dictionary_path, 'r', errors='ignore', encoding=encoding) as f:
                    for line in f:
                        word = line.strip()
                        if min_length <= len(word) <= max_length:
                            words.append(word)
                            word_count += 1
                            
                            if word_count >= max_words:
                                break
                
                # If we got words, break out of the encoding loop
                if words:
                    print(f"Successfully loaded with {encoding} encoding")
                    break
                    
            except UnicodeDecodeError:
                print(f"Failed with {encoding} encoding, trying another...")
                continue
        
        # Check if we managed to load any words
        if not words:
            raise Exception("Failed to load words with any encoding")
        
        print(f"Loaded {len(words)} common words from dictionary")
        return words
        
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        
        # Create some dummy words if loading fails
        dummy_words = ["password", "welcome", "qwerty", "football", "baseball", 
                      "princess", "dragon", "butterfly", "sunshine", "monkey",
                      "letmein", "shadow", "master", "jennifer", "robert",
                      "michael", "thomas", "jessica", "jordan", "daniel",
                      "computer", "internet", "pokemon", "google", "youtube",
                      "soccer", "purple", "orange", "yellow", "banana"]
        print(f"Using {len(dummy_words)} dummy words instead")
        return dummy_words

def generate_comparison_passwords(common_words, count=500):
    """
    Generate different types of passwords based on dictionary words for comparison.
    """
    passwords = {
        "dictionary": [],        # Plain dictionary words
        "dict_with_caps": [],    # Dictionary words with uppercase
        "dict_with_nums": [],    # Dictionary words with numbers
        "dict_with_symbols": [], # Dictionary words with symbols
        "dict_augmented": []     # Dictionary words with caps, numbers, and symbols
    }
    
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure we have enough words
    if len(common_words) < count:
        # Repeat the list if needed
        common_words = common_words * (count // len(common_words) + 1)
    
    # Randomly select words for each category
    selected_words = random.sample(common_words, count * 5)  # We need 5 sets
    
    for i in range(count):
        # Plain dictionary
        passwords["dictionary"].append(selected_words[i])
        
        # Dictionary with capitalization (capitalize first letter)
        cap_word = selected_words[count + i].capitalize()
        passwords["dict_with_caps"].append(cap_word)
        
        # Dictionary with numbers (add 1-3 digits at end)
        num_word = selected_words[2 * count + i] + ''.join(random.choices(string.digits, k=random.randint(1, 3)))
        passwords["dict_with_nums"].append(num_word)
        
        # Dictionary with symbols (add 1-2 symbols)
        sym_word = selected_words[3 * count + i] + ''.join(random.choices(symbols, k=random.randint(1, 2)))
        passwords["dict_with_symbols"].append(sym_word)
        
        # Augmented (capitalization, numbers, and symbols)
        base_word = selected_words[4 * count + i]
        aug_word = base_word.capitalize() + random.choice(symbols) + ''.join(random.choices(string.digits, k=2))
        passwords["dict_augmented"].append(aug_word)
    
    return passwords

def analyze_password_strength(passwords):
    """
    Analyze various strength metrics of a set of passwords.
    """
    results = {
        "count": len(passwords),
        "length": {
            "mean": np.mean([len(p) for p in passwords]),
            "min": min([len(p) for p in passwords]),
            "max": max([len(p) for p in passwords])
        },
        "entropy": {
            "mean": np.mean([calculate_entropy(p) for p in passwords]),
            "per_char": np.mean([calculate_entropy(p)/len(p) for p in passwords]),
            "min": min([calculate_entropy(p) for p in passwords]),
            "max": max([calculate_entropy(p) for p in passwords])
        },
        "character_classes": {
            "uppercase_pct": np.mean([sum(1 for c in p if c.isupper()) / len(p) * 100 for p in passwords]),
            "lowercase_pct": np.mean([sum(1 for c in p if c.islower()) / len(p) * 100 for p in passwords]),
            "digits_pct": np.mean([sum(1 for c in p if c.isdigit()) / len(p) * 100 for p in passwords]),
            "symbols_pct": np.mean([sum(1 for c in p if not c.isalnum()) / len(p) * 100 for p in passwords])
        },
        "complexity_score": 0  # Will be calculated below
    }
    
    # Calculate total entropy (not just per character)
    results["total_entropy"] = {
        "mean": results["entropy"]["mean"],
        "min": results["entropy"]["min"],
        "max": results["entropy"]["max"]
    }
    
    # Calculate theoretical maximum entropy
    avg_length = results["length"]["mean"]
    results["theoretical_max_entropy"] = math.log2(95) * avg_length  # 95 printable ASCII chars
    results["entropy_ratio"] = results["total_entropy"]["mean"] / results["theoretical_max_entropy"]
    
    # Calculate a complexity score based on NIST guidelines (simplified)
    # Length (0-5 points)
    length_score = min(5, results["length"]["mean"] / 2.5)  # 12.5 chars = 5 points
    
    # Character diversity (0-5 points)
    char_classes_used = (results["character_classes"]["uppercase_pct"] > 0) + \
                        (results["character_classes"]["lowercase_pct"] > 0) + \
                        (results["character_classes"]["digits_pct"] > 0) + \
                        (results["character_classes"]["symbols_pct"] > 0)
    diversity_score = char_classes_used * 1.25
    
    # Entropy (0-5 points)
    entropy_score = min(5, results["entropy"]["mean"] / 16)  # 80 bits = 5 points
    
    # Calculate overall complexity score (0-15)
    results["complexity_score"] = length_score + diversity_score + entropy_score
    
    return results

def identify_patterns(passwords):
    """
    Identify common patterns and potential vulnerabilities in the passwords.
    """
    if not passwords:
        return {"error": "No passwords provided"}
    
    patterns = {
        "starting_chars": Counter(),
        "ending_chars": Counter(),
        "starting_pattern": Counter(),
        "ending_pattern": Counter(),
        "character_transitions": Counter(),
        "repeated_sequences": Counter(),
        "character_positions": {},
        "common_substrings": Counter()
    }
    
    # Analyze patterns in each password
    for password in passwords:
        if not password or len(password) < 2:
            continue
        
        # Starting and ending characters
        patterns["starting_chars"][password[0]] += 1
        patterns["ending_chars"][password[-1]] += 1
        
        # Starting and ending patterns (first/last 2 chars)
        if len(password) >= 2:
            patterns["starting_pattern"][password[:2]] += 1
            patterns["ending_pattern"][password[-2:]] += 1
        
        # Character transitions (pairs of adjacent chars)
        for i in range(len(password) - 1):
            patterns["character_transitions"][password[i:i+2]] += 1
        
        # Repeated sequences (sequences that appear more than once)
        for length in range(2, min(len(password), 5)):  # Check sequences of length 2-4
            for i in range(len(password) - length + 1):
                substring = password[i:i+length]
                if password.count(substring) > 1:
                    patterns["repeated_sequences"][substring] += 1
        
        # Character positions (what characters tend to appear in specific positions)
        for i, char in enumerate(password):
            if i not in patterns["character_positions"]:
                patterns["character_positions"][i] = Counter()
            patterns["character_positions"][i][char] += 1
        
        # Find common substrings across passwords (this is computationally expensive for large sets)
        if len(passwords) < 1000:  # Only do this for reasonable-sized sets
            for other_pw in passwords:
                if password == other_pw:
                    continue
                for length in range(3, min(len(password), len(other_pw), 6)):
                    for i in range(len(password) - length + 1):
                        substring = password[i:i+length]
                        if substring in other_pw:
                            patterns["common_substrings"][substring] += 1
    
    # Normalize character positions to get percentages
    position_percentages = {}
    for pos, counter in patterns["character_positions"].items():
        total = sum(counter.values())
        position_percentages[pos] = {char: count/total*100 for char, count in counter.most_common(3)}
    
    patterns["character_position_percentages"] = position_percentages
    
    # Identify potential vulnerabilities
    vulnerabilities = []
    
    # Check for highly predictable starting patterns
    for pattern, count in patterns["starting_pattern"].most_common(3):
        percentage = count / len(passwords) * 100
        if percentage > 50:  # If more than 50% of passwords start with the same pattern
            vulnerabilities.append({
                "type": "predictable_start",
                "pattern": pattern,
                "percentage": percentage,
                "description": f"{percentage:.1f}% of passwords start with '{pattern}'"
            })
    
    # Check for highly predictable character positions
    for pos, percentages in position_percentages.items():
        for char, pct in percentages.items():
            if pct > 70:  # If a character appears in a specific position more than 70% of the time
                vulnerabilities.append({
                    "type": "predictable_position",
                    "position": pos,
                    "character": char,
                    "percentage": pct,
                    "description": f"Character '{char}' appears at position {pos} in {pct:.1f}% of passwords"
                })
    
    # Check for common repeated sequences
    if patterns["repeated_sequences"]:
        most_common = patterns["repeated_sequences"].most_common(1)[0]
        vulnerabilities.append({
            "type": "repeated_sequence",
            "sequence": most_common[0],
            "count": most_common[1],
            "description": f"Sequence '{most_common[0]}' is repeated within {most_common[1]} passwords"
        })
    
    patterns["vulnerabilities"] = vulnerabilities
    
    return patterns

def compare_strength_metrics(audio_passwords, dictionary_passwords):
    """
    Compare strength metrics between audio-generated and dictionary-based passwords.
    """
    # Analyze each set of passwords
    audio_analysis = analyze_password_strength(audio_passwords)
    
    dict_analyses = {}
    for pw_type, passwords in dictionary_passwords.items():
        dict_analyses[pw_type] = analyze_password_strength(passwords)
    
    # Prepare comparison data
    comparison = {
        "password_types": ["audio"] + list(dictionary_passwords.keys()),
        "metrics": {
            "entropy_bits": [audio_analysis["entropy"]["mean"]] + 
                           [dict_analyses[t]["entropy"]["mean"] for t in dictionary_passwords.keys()],
            "entropy_per_char": [audio_analysis["entropy"]["per_char"]] + 
                               [dict_analyses[t]["entropy"]["per_char"] for t in dictionary_passwords.keys()],
            "length": [audio_analysis["length"]["mean"]] + 
                     [dict_analyses[t]["length"]["mean"] for t in dictionary_passwords.keys()],
            "complexity_score": [audio_analysis["complexity_score"]] + 
                               [dict_analyses[t]["complexity_score"] for t in dictionary_passwords.keys()],
            "uppercase_pct": [audio_analysis["character_classes"]["uppercase_pct"]] + 
                            [dict_analyses[t]["character_classes"]["uppercase_pct"] for t in dictionary_passwords.keys()],
            "lowercase_pct": [audio_analysis["character_classes"]["lowercase_pct"]] + 
                            [dict_analyses[t]["character_classes"]["lowercase_pct"] for t in dictionary_passwords.keys()],
            "digits_pct": [audio_analysis["character_classes"]["digits_pct"]] + 
                         [dict_analyses[t]["character_classes"]["digits_pct"] for t in dictionary_passwords.keys()],
            "symbols_pct": [audio_analysis["character_classes"]["symbols_pct"]] + 
                          [dict_analyses[t]["character_classes"]["symbols_pct"] for t in dictionary_passwords.keys()],
            "total_entropy": [audio_analysis["total_entropy"]["mean"]] +
                           [dict_analyses[t]["total_entropy"]["mean"] for t in dictionary_passwords.keys()],
            "theoretical_max_entropy": [audio_analysis["theoretical_max_entropy"]] +
                                     [dict_analyses[t]["theoretical_max_entropy"] for t in dictionary_passwords.keys()],
            "entropy_ratio": [audio_analysis["entropy_ratio"]] +
                           [dict_analyses[t]["entropy_ratio"] for t in dictionary_passwords.keys()]
        }
    }
    
    return comparison

def visualize_strength_comparison(comparison, audio_patterns, output_path="password_strength_comparison.png"):
    """
    Create visualizations comparing password strength metrics.
    """
    # Create a figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Password Strength Comparison: Audio vs. Dictionary-based', fontsize=16)
    
    # Color mapping
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Plot 1: Entropy Comparison
    ax1 = axs[0, 0]
    x = np.arange(len(comparison["password_types"]))
    width = 0.35
    
    ax1.bar(x - width/2, comparison["metrics"]["entropy_bits"], width, label='Total Entropy (bits)')
    ax1.bar(x + width/2, comparison["metrics"]["entropy_per_char"], width, label='Entropy per Char (bits)')
    
    # Set appropriate scale for entropy
    max_entropy = max(comparison["metrics"]["entropy_bits"])
    ax1.set_ylim(0, max(80, max_entropy * 1.2))
    
    ax1.set_title('Password Entropy')
    ax1.set_xticks(x)
    ax1.set_xticklabels([t.capitalize() for t in comparison["password_types"]])
    ax1.legend()
    
    # Plot 2: Complexity Score
    ax2 = axs[0, 1]
    bars = ax2.bar(comparison["password_types"], comparison["metrics"]["complexity_score"], color=colors)
    ax2.set_title('Password Complexity Score (NIST-based)')
    ax2.set_ylim(0, 15)  # Score ranges from 0-15
    
    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.1f}', 
                ha='center', va='bottom')
    
    # Plot 3: Character Class Distribution
    ax3 = axs[1, 0]
    char_classes = ['Uppercase', 'Lowercase', 'Digits', 'Symbols']
    char_data = np.array([
        comparison["metrics"]["uppercase_pct"],
        comparison["metrics"]["lowercase_pct"],
        comparison["metrics"]["digits_pct"],
        comparison["metrics"]["symbols_pct"]
    ]).T  # Transpose to get the right shape
    
    x = np.arange(len(comparison["password_types"]))
    width = 0.2
    
    # Plot each character class as a group of bars
    for i, class_name in enumerate(char_classes):
        ax3.bar(x + (i - 1.5) * width, char_data[:, i], width, label=class_name)
    
    ax3.set_title('Character Class Distribution')
    ax3.set_xticks(x)
    ax3.set_xticklabels([t.capitalize() for t in comparison["password_types"]])
    ax3.set_ylabel('Percentage (%)')
    ax3.legend()
    
    # Plot 4: Vulnerability Analysis (for audio passwords)
    ax4 = axs[1, 1]
    ax4.axis('off')  # Turn off axis
    
    # Create a text box with vulnerability analysis
    vulnerability_text = "Audio Password Pattern Analysis:\n\n"
    
    # Add information about starting patterns
    vulnerability_text += "Top 3 Starting Patterns:\n"
    for pattern, count in audio_patterns["starting_pattern"].most_common(3):
        percentage = count / audio_patterns.get("count", len(audio_patterns.get("starting_pattern", {}))) * 100
        vulnerability_text += f"- '{pattern}': {percentage:.1f}%\n"
    
    vulnerability_text += "\nTop 3 Character Transitions:\n"
    for transition, count in audio_patterns["character_transitions"].most_common(3):
        percentage = count / sum(audio_patterns["character_transitions"].values()) * 100
        vulnerability_text += f"- '{transition}': {percentage:.1f}%\n"
    
    vulnerability_text += "\nVulnerabilities Identified:\n"
    if audio_patterns.get("vulnerabilities"):
        for i, vuln in enumerate(audio_patterns["vulnerabilities"][:3]):  # Show top 3
            vulnerability_text += f"- {vuln['description']}\n"
    else:
        vulnerability_text += "- No significant vulnerabilities identified\n"
    
    ax4.text(0.05, 0.95, vulnerability_text, fontsize=10, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    test_results_dir = ensure_test_results_dir()
    plt.savefig(os.path.join(test_results_dir, output_path))
    print(f"Created visualization: {output_path}")
        
def save_analysis_results(comparison, audio_patterns, dict_patterns, output_file="password_strength_analysis.json"):
    """
    Save analysis results to a JSON file.
    """
    # Convert Counter objects to regular dictionaries for JSON serialization
    for pattern_type, counter in audio_patterns.items():
        if isinstance(counter, Counter):
            audio_patterns[pattern_type] = dict(counter.most_common(10))
    
    for pw_type, patterns in dict_patterns.items():
        for pattern_type, counter in patterns.items():
            if isinstance(counter, Counter):
                dict_patterns[pw_type][pattern_type] = dict(counter.most_common(10))
    
    # Prepare results
    results = {
        "strength_comparison": comparison,
        "audio_password_patterns": audio_patterns,
        "dictionary_password_patterns": dict_patterns
    }
    
    test_results_dir = ensure_test_results_dir()
    with open(os.path.join(test_results_dir, output_file), 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Analysis results saved to {output_file}")

def main():
    # Get the current script directory (PasswordAnalysis folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to parent directory (sound-to-security)
    parent_dir = os.path.dirname(current_dir)
    
    # Navigate to root directory (outside sound-to-security)
    root_dir = os.path.dirname(parent_dir)
    
    # Path to your audio data
    audio_data_path = os.path.join(root_dir, "audio_data.json")
    
    # Path to dictionary file (try multiple locations)
    dictionary_path = os.path.join(current_dir, "common_words.txt")
    
    # Check alternative locations if the file isn't found
    if not os.path.exists(dictionary_path):
        # Try rockyou.txt in the root directory
        root_rockyou = os.path.join(root_dir, "rockyou.txt")
        if os.path.exists(root_rockyou):
            dictionary_path = root_rockyou
            print(f"Found rockyou.txt in root directory: {dictionary_path}")
        else:
            # Try other common locations
            parent_rockyou = os.path.join(parent_dir, "rockyou.txt")
            if os.path.exists(parent_rockyou):
                dictionary_path = parent_rockyou
                print(f"Found rockyou.txt in parent directory: {dictionary_path}")
            else:
                dictionary_path = None
                print("No dictionary file found. Will generate sample dictionary passwords.")
    
    print("Starting password strength and pattern analysis...")
    
    # Load audio-generated passwords
    audio_passwords = load_audio_passwords(audio_data_path)
    
    if not audio_passwords:
        print("Error: No audio passwords found. Check the path to your audio_data.json file.")
        return
    
    # Load or generate dictionary passwords
    common_words = []
    if dictionary_path:
        common_words = load_common_words(dictionary_path)
    
    if not common_words:
        # Create some dummy words if no dictionary is available
        common_words = [
            "password", "welcome", "qwerty", "football", "baseball", 
            "princess", "dragon", "butterfly", "sunshine", "monkey",
            "letmein", "shadow", "master", "jennifer", "robert",
            "michael", "thomas", "jessica", "jordan", "daniel",
            "computer", "internet", "pokemon", "google", "youtube",
            "soccer", "purple", "orange", "yellow", "banana"
        ]
        print(f"Using {len(common_words)} common words for comparison")
    
    # Generate comparison passwords
    try:
        num_comparison = int(input("How many comparison passwords to generate? (default: 200): ") or "200")
    except ValueError:
        num_comparison = 200
        print("Invalid input. Using default value of 200 passwords.")
    
    dictionary_passwords = generate_comparison_passwords(common_words, num_comparison)
    
    # Identify patterns and vulnerabilities in audio passwords
    print("Analyzing password patterns...")
    audio_patterns = identify_patterns(audio_passwords)
    audio_patterns["count"] = len(audio_passwords)  # Add count for percentage calculations
    
    # Identify patterns in dictionary passwords (sample only for performance)
    dict_patterns = {}
    for pw_type, passwords in dictionary_passwords.items():
        sample_size = min(500, len(passwords))
        sample = random.sample(passwords, sample_size)
        dict_patterns[pw_type] = identify_patterns(sample)
        dict_patterns[pw_type]["count"] = len(sample)  # Add count for percentage calculations
    
    # Compare strength metrics
    print("Comparing password strength metrics...")
    strength_comparison = compare_strength_metrics(audio_passwords, dictionary_passwords)
    
    # Create visualizations
    print("Creating visualizations...")
    visualize_strength_comparison(strength_comparison, audio_patterns)
    
    # Save results
    save_analysis_results(strength_comparison, audio_patterns, dict_patterns)
    
    # Print summary to console
    print("\n=== Password Strength Analysis Summary ===")
    print(f"\nAudio-generated passwords ({len(audio_passwords)} analyzed):")
    print(f"  Average Entropy: {strength_comparison['metrics']['entropy_bits'][0]:.2f} bits")
    print(f"  Theoretical Maximum Entropy: {strength_comparison['metrics']['theoretical_max_entropy'][0]:.2f} bits")
    print(f"  Entropy Utilization Ratio: {strength_comparison['metrics']['entropy_ratio'][0]:.2f}")
    print(f"  Entropy per Character: {strength_comparison['metrics']['entropy_per_char'][0]:.2f} bits/char")
    print(f"  Complexity Score: {strength_comparison['metrics']['complexity_score'][0]:.2f}/15")
    
    # Print pattern vulnerabilities
    print("\nPotential pattern vulnerabilities:")
    if audio_patterns.get("vulnerabilities"):
        for vuln in audio_patterns["vulnerabilities"]:
            print(f"  - {vuln['description']}")
    else:
        print("  - No significant vulnerabilities identified")
    
    # Print comparison with best dictionary password type
    best_dict_index = np.argmax(strength_comparison["metrics"]["complexity_score"][1:]) + 1
    best_dict_type = strength_comparison["password_types"][best_dict_index]
    
    print(f"\nCompared to best dictionary-based passwords ({best_dict_type}):")
    entropy_diff = strength_comparison["metrics"]["entropy_bits"][0] - strength_comparison["metrics"]["entropy_bits"][best_dict_index]
    complexity_diff = strength_comparison["metrics"]["complexity_score"][0] - strength_comparison["metrics"]["complexity_score"][best_dict_index]
    
    print(f"  Entropy difference: {entropy_diff:.2f} bits ({'+' if entropy_diff >= 0 else ''}{entropy_diff/strength_comparison['metrics']['entropy_bits'][best_dict_index]*100:.1f}%)")
    print(f"  Complexity difference: {complexity_diff:.2f} points ({'+' if complexity_diff >= 0 else ''}{complexity_diff/strength_comparison['metrics']['complexity_score'][best_dict_index]*100:.1f}%)")
    
    print("\nAnalysis complete. Results and visualizations have been saved.")

if __name__ == "__main__":
    main()