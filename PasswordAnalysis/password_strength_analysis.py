"""
This script analyzes the strength of audio-generated passwords compared to
dictionary-based passwords and identifies any patterns or vulnerabilities.
"""

from password_analysis_utils import (
    get_project_paths, load_audio_passwords, calculate_entropy, save_json_results, save_plot
)

import os
import numpy as np
import matplotlib.pyplot as plt
import string
import random
from collections import Counter

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
    results["theoretical_max_entropy"] = np.log2(95) * avg_length  # 95 printable ASCII chars
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

def calculate_adjusted_entropy(passwords):
    """
    Calculate entropy that accounts for observed character distributions
    at each position in the passwords.
    """
    if not passwords:
        return {"total": 0, "by_position": [], "average_per_position": 0}
    
    # Get password length (assuming similar lengths)
    avg_length = int(np.mean([len(p) for p in passwords if p]))
    
    # Count character frequencies at each position
    position_entropy = []
    for pos in range(avg_length):
        char_counts = {}
        valid_count = 0
        
        for pw in passwords:
            if len(pw) > pos:
                char = pw[pos]
                char_counts[char] = char_counts.get(char, 0) + 1
                valid_count += 1
        
        # Calculate entropy for this position
        entropy = 0
        for count in char_counts.values():
            prob = count / valid_count
            entropy -= prob * np.log2(prob)
        
        position_entropy.append(entropy)
    
    # Total entropy is sum of positional entropies
    total_adjusted_entropy = sum(position_entropy)
    
    return {
        "total": total_adjusted_entropy,
        "by_position": position_entropy,
        "average_per_position": np.mean(position_entropy)
    }

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

def visualize_strength_comparison(comparison_results, audio_patterns, output_path="password_strength_comparison.png"):
    """Create visualizations comparing password strength metrics."""
    # Extract key metrics for each system
    all_systems = comparison_results["password_types"]
    
    # Filter to keep only audio and basic dictionary
    systems_to_keep = ["audio", "dictionary"]
    indices_to_keep = [all_systems.index(system) for system in systems_to_keep if system in all_systems]
    
    # Create filtered systems list
    systems = [all_systems[i] for i in indices_to_keep]
    
    # Calculate pattern-adjusted entropy for audio passwords
    audio_passwords = audio_patterns.get("passwords", [])
    
    # If we don't have passwords, use an approximation
    if not audio_passwords:
        pattern_adjusted_entropy = comparison_results["metrics"]["entropy_bits"][0] * 0.85  # Approximate 15% reduction
    else:
        # Calculate actual adjusted entropy
        adjusted = calculate_adjusted_entropy(audio_passwords)
        pattern_adjusted_entropy = adjusted["total"]
    
    # Create a new system entry for the adjusted entropy
    systems_with_adjusted = systems.copy()
    systems_with_adjusted.insert(1, "audio_adjusted")  # Insert after "audio"
    
    # Prepare filtered data for key metrics
    metrics = {
        "Entropy (bits)": [comparison_results["metrics"]["entropy_bits"][i] for i in indices_to_keep],
        "Entropy/Char (bits)": [comparison_results["metrics"]["entropy_per_char"][i] for i in indices_to_keep],
        "Password Length": [comparison_results["metrics"]["length"][i] for i in indices_to_keep],
    }
    
    # Filter other metrics too
    filtered_metrics = {}
    for metric_name, values_list in comparison_results["metrics"].items():
        filtered_metrics[metric_name] = [values_list[i] for i in indices_to_keep]
    
    # Add adjusted entropy values
    metrics_with_adjusted = {}
    for metric_name, values in metrics.items():
        if metric_name == "Entropy (bits)":
            # Insert the adjusted entropy after the audio entry
            adjusted_values = values.copy()
            adjusted_values.insert(1, pattern_adjusted_entropy)
            metrics_with_adjusted[metric_name] = adjusted_values
        else:
            # For other metrics, just duplicate the audio value as placeholder
            adjusted_values = values.copy()
            adjusted_values.insert(1, values[0])
            metrics_with_adjusted[metric_name] = adjusted_values
    
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Password Strength Comparison', fontsize=16)
    
    # Plot entropy with special handling for the adjusted value
    ax1 = axs[0, 0]
    x = np.arange(len(systems_with_adjusted))
    width = 0.35
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    special_colors = ['#1f77b4', '#d62728', '#2ca02c']
    
    # Plot total entropy bars
    bars1 = ax1.bar(x - width/2, metrics_with_adjusted["Entropy (bits)"], width, color=special_colors, label='Total Entropy')
    
    # Add hatching to the adjusted bar
    bars1[1].set_hatch('////')
    
    # Plot entropy per character bars with orange color
    bars2 = ax1.bar(x + width/2, metrics_with_adjusted["Entropy/Char (bits)"], width, color='orange', label='Entropy/Char')
    
    # Set appropriate scale
    max_entropy = max(metrics_with_adjusted["Entropy (bits)"])
    ax1.set_ylim(0, max(80, max_entropy * 1.2))
    
    ax1.set_title('Password Entropy')
    ax1.set_xticks(x)
    labels = [s.capitalize() if s != "audio_adjusted" else "Audio (Adjusted)" for s in systems_with_adjusted]
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.legend()
    
    # Add values on top of bars
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9, color='black')
    
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9, color='black')
    
    # Plot 2: Complexity Score (using filtered systems)
    ax2 = axs[0, 1]
    complexity_values = [filtered_metrics["complexity_score"][i] for i in range(len(systems))]
    bars = ax2.bar(systems, complexity_values, color=colors[:len(systems)])
    ax2.set_title('Password Complexity Score (NIST-based)')
    ax2.set_ylim(0, 15)  # Score ranges from 0-15
    
    # Add values on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.1f}', 
                ha='center', va='bottom')
    
    # Plot 3: Character Class Distribution (using filtered systems)
    ax3 = axs[1, 0]
    char_classes = ['Uppercase', 'Lowercase', 'Digits', 'Symbols']
    char_data = np.array([
        filtered_metrics["uppercase_pct"],
        filtered_metrics["lowercase_pct"],
        filtered_metrics["digits_pct"],
        filtered_metrics["symbols_pct"]
    ]).T  # Transpose to get the right shape
    
    x = np.arange(len(systems))
    width = 0.2
    
    # Plot each character class as a group of bars
    for i, class_name in enumerate(char_classes):
        ax3.bar(x + (i - 1.5) * width, char_data[:, i], width, label=class_name)
    
    ax3.set_title('Character Class Distribution')
    ax3.set_xticks(x)
    ax3.set_xticklabels([t.capitalize() for t in systems], rotation=45, ha='right')
    ax3.set_ylabel('Percentage (%)')
    ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)
    
    # Plot 4: Vulnerability Analysis
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
    
    # Add information about the pattern-adjusted entropy
    theoretical = comparison_results["metrics"]["entropy_bits"][0]
    vulnerability_text += f"\nEntropy Analysis:\n"
    vulnerability_text += f"- Theoretical: {theoretical:.2f} bits\n"
    vulnerability_text += f"- Pattern-Adjusted: {pattern_adjusted_entropy:.2f} bits\n"
    vulnerability_text += f"- Reduction: {theoretical - pattern_adjusted_entropy:.2f} bits ({(theoretical - pattern_adjusted_entropy)/theoretical*100:.1f}%)"
    
    ax4.text(0.05, 0.95, vulnerability_text, fontsize=10, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Fix text overlap
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust to leave room for suptitle
    
    # Save the figure
    save_plot(fig, output_path)

def main():
    # Get paths
    paths = get_project_paths()
    audio_data_path = paths["audio_data_path"]
    
    # Path to dictionary file (try multiple locations)
    current_dir = paths["current_dir"]
    parent_dir = paths["parent_dir"]
    root_dir = paths["root_dir"]
    
    dictionary_path = os.path.join(current_dir, "common_words.txt")
    
    # Check alternative locations if the file isn't found
    if not os.path.exists(dictionary_path):
        alternative_paths = [
            os.path.join(root_dir, "rockyou.txt"),
            os.path.join(parent_dir, "rockyou.txt")
        ]
        
        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                dictionary_path = alt_path
                print(f"Found dictionary file: {dictionary_path}")
                break
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
    audio_patterns["passwords"] = audio_passwords  # Store the actual passwords for entropy calculation
    
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
    save_json_results({
        "strength_comparison": strength_comparison, 
        "audio_patterns": audio_patterns, 
        "dict_patterns": dict_patterns
    }, "password_strength_analysis.json")
    
    # Print summary
    print_summary_results(strength_comparison, audio_patterns)

def print_summary_results(strength_comparison, audio_patterns):
    """Print a summary of strength analysis results to the console."""
    print("\n=== Password Strength Analysis Summary ===")
    print(f"\nAudio-generated passwords ({strength_comparison['password_types'][0]} analyzed):")
    print(f"  Average Entropy: {strength_comparison['metrics']['entropy_bits'][0]:.2f} bits")
    print(f"  Theoretical Maximum Entropy: {strength_comparison['metrics']['theoretical_max_entropy'][0]:.2f} bits")
    print(f"  Entropy Utilization Ratio: {strength_comparison['metrics']['entropy_ratio'][0]:.2f}")
    print(f"  Entropy per Character: {strength_comparison['metrics']['entropy_per_char'][0]:.2f} bits/char")
    print(f"  Complexity Score: {strength_comparison['metrics']['complexity_score'][0]:.2f}/15")
    
    # Calculate and print pattern-adjusted entropy
    if audio_patterns.get("passwords"):
        adjusted = calculate_adjusted_entropy(audio_patterns["passwords"])
        pattern_adjusted_entropy = adjusted["total"]
        theoretical = strength_comparison['metrics']['entropy_bits'][0]
        reduction = theoretical - pattern_adjusted_entropy
        reduction_pct = (reduction / theoretical) * 100
        
        print(f"  Pattern-Adjusted Entropy: {pattern_adjusted_entropy:.2f} bits")
        print(f"  Entropy Reduction: {reduction:.2f} bits ({reduction_pct:.1f}%)")
    
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

if __name__ == "__main__":
   import os  # Import here for alternative path checking
   main()