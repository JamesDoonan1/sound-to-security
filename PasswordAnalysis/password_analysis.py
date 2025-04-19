"""
This script analyzes the strength of audio-generated passwords compared to
candidate passwords from the fine-tuned model.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import math
from collections import Counter

def ensure_test_results_dir():
    """Create TestResults directory if it doesn't exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_results_dir = os.path.join(current_dir, "TestResults")
    if not os.path.exists(test_results_dir):
        os.makedirs(test_results_dir)
        print(f"Created TestResults directory at: {test_results_dir}")
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

def calculate_theoretical_entropy(password_length, char_set_size=95):
    """
    Calculate theoretical maximum entropy for a password.
    Assumes a character set of specified size (default 95 for printable ASCII)
    """
    return math.log2(char_set_size) * password_length

def analyze_character_classes(password):
    """
    Analyze character class distribution in a password.
    """
    if not password:
        return {
            'uppercase': 0,
            'lowercase': 0, 
            'digits': 0,
            'symbols': 0
        }
    
    classes = {
        'uppercase': 0,
        'lowercase': 0, 
        'digits': 0,
        'symbols': 0
    }
    
    for char in password:
        if char.isupper():
            classes['uppercase'] += 1
        elif char.islower():
            classes['lowercase'] += 1
        elif char.isdigit():
            classes['digits'] += 1
        else:
            classes['symbols'] += 1
    
    # Convert to percentages
    total = len(password)
    for cls in classes:
        classes[cls] = (classes[cls] / total) * 100
    
    return classes

def analyze_passwords(passwords, name="Dataset"):
    """
    Comprehensive analysis of a set of passwords.
    """
    if not passwords:
        return {"error": "No passwords provided"}
    
    # Filter out None or empty passwords
    valid_passwords = [p for p in passwords if p]
    
    if not valid_passwords:
        return {"error": "No valid passwords found"}
    
    results = {
        "name": name,
        "count": len(valid_passwords),
        "entropy": {
            "individual": [],
            "per_character": [],
            "theoretical_max": []
        },
        "patterns": {
            "start_patterns": Counter(),
            "character_classes": {
                "uppercase": [],
                "lowercase": [], 
                "digits": [],
                "symbols": []
            },
            "length": []
        }
    }
    
    # Analyze each password
    for password in valid_passwords:
        # Password length
        length = len(password)
        results["patterns"]["length"].append(length)
        
        # Start patterns (first 2 chars)
        if length >= 2:
            start = password[:2]
            results["patterns"]["start_patterns"][start] += 1
            
        # Entropy calculations
        entropy = calculate_entropy(password)
        entropy_per_char = entropy / length if length > 0 else 0
        theoretical_max = calculate_theoretical_entropy(length)
        
        results["entropy"]["individual"].append(entropy)
        results["entropy"]["per_character"].append(entropy_per_char)
        results["entropy"]["theoretical_max"].append(theoretical_max)
        
        # Character class analysis
        char_classes = analyze_character_classes(password)
        for cls, percentage in char_classes.items():
            results["patterns"]["character_classes"][cls].append(percentage)
    
    # Aggregate calculations
    results["entropy"]["avg"] = sum(results["entropy"]["individual"]) / len(valid_passwords)
    results["entropy"]["avg_per_char"] = sum(results["entropy"]["per_character"]) / len(valid_passwords)
    results["entropy"]["avg_theoretical_max"] = sum(results["entropy"]["theoretical_max"]) / len(valid_passwords)
    results["entropy"]["utilization_percentage"] = (results["entropy"]["avg"] / results["entropy"]["avg_theoretical_max"]) * 100
    
    # Average length - must be calculated BEFORE using it
    results["patterns"]["avg_length"] = sum(results["patterns"]["length"]) / len(valid_passwords)
    
    # Now we can add total entropy metrics based on avg_length
    results["entropy"]["average_total_entropy"] = results["entropy"]["avg"]  # Same value, just renamed for clarity
    results["entropy"]["theoretical_maximum"] = calculate_theoretical_entropy(results["patterns"]["avg_length"])
    results["entropy"]["utilization_ratio"] = results["entropy"]["average_total_entropy"] / results["entropy"]["theoretical_maximum"]
    
    # Average character class distribution
    class_keys = list(results["patterns"]["character_classes"].keys())
    for cls in class_keys:
        avg_key = cls + "_avg"
        results["patterns"]["character_classes"][avg_key] = sum(results["patterns"]["character_classes"][cls]) / len(valid_passwords)
    
    # Top start patterns
    results["patterns"]["top_start_patterns"] = results["patterns"]["start_patterns"].most_common(5)
    
    return results

def load_passwords_from_json(file_path):
    """
    Load passwords from audio_data.json file.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract passwords
        passwords = [entry.get("password") for entry in data if "password" in entry]
        return passwords
    except Exception as e:
        print(f"Error loading passwords from {file_path}: {e}")
        return []

def load_security_test_results(file_path):
    """
    Load security test results containing candidate passwords.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        results = {
            "base_passwords": [],
            "candidate_passwords": [],
            "edit_distances": []
        }
        
        for test in data:
            if "base_password" in test:
                results["base_passwords"].append(test["base_password"])
            
            if "candidates" in test:
                results["candidate_passwords"].extend([c for c in test["candidates"] if c])
            
            if "edit_distances" in test:
                results["edit_distances"].extend(test["edit_distances"])
        
        return results
    except Exception as e:
        print(f"Error loading security test results from {file_path}: {e}")
        return {"base_passwords": [], "candidate_passwords": [], "edit_distances": []}

def plot_entropy_comparison(original_analysis, candidate_analysis, output_path):
    """
    Create visualizations comparing entropy between original and candidate passwords.
    """
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Password Security Analysis', fontsize=16)
    
    # 1. Entropy Distribution Histogram
    bin_edges = np.histogram_bin_edges(np.concatenate([original_analysis["entropy"]["per_character"], 
                                   candidate_analysis["entropy"]["per_character"]]), bins=20)
    bin_width = bin_edges[1] - bin_edges[0]
    axs[0, 0].hist(original_analysis["entropy"]["per_character"], bins=bin_edges, alpha=0.7, 
                label='Original', width=bin_width*0.4, align='left')
    axs[0, 0].hist(candidate_analysis["entropy"]["per_character"], bins=bin_edges, alpha=0.7, 
                label='Candidates', width=bin_width*0.4, align='right')
    axs[0, 0].set_title('Entropy Distribution (bits per character)')
    axs[0, 0].set_xlabel('Bits of Entropy per Character')
    axs[0, 0].set_ylabel('Frequency')
    axs[0, 0].legend()
    
    # 2. Character Class Distribution
    labels = ['Uppercase', 'Lowercase', 'Digits', 'Symbols']
    orig_values = [
        original_analysis["patterns"]["character_classes"]["uppercase_avg"],
        original_analysis["patterns"]["character_classes"]["lowercase_avg"],
        original_analysis["patterns"]["character_classes"]["digits_avg"],
        original_analysis["patterns"]["character_classes"]["symbols_avg"]
    ]
    cand_values = [
        candidate_analysis["patterns"]["character_classes"]["uppercase_avg"],
        candidate_analysis["patterns"]["character_classes"]["lowercase_avg"],
        candidate_analysis["patterns"]["character_classes"]["digits_avg"],
        candidate_analysis["patterns"]["character_classes"]["symbols_avg"]
    ]
    
    x = np.arange(len(labels))
    width = 0.35
    
    axs[0, 1].bar(x - width/2, orig_values, width, label='Original')
    axs[0, 1].bar(x + width/2, cand_values, width, label='Candidates')
    axs[0, 1].set_title('Character Class Distribution')
    axs[0, 1].set_ylabel('Percentage')
    axs[0, 1].set_xticks(x)
    axs[0, 1].set_xticklabels(labels)
    axs[0, 1].legend()
    
    # 3. Entropy Utilization
    labels = ['Original', 'Candidates']
    values = [
        original_analysis["entropy"]["utilization_percentage"],
        candidate_analysis["entropy"]["utilization_percentage"]
    ]
    
    axs[1, 0].bar(labels, values, color=['blue', 'orange'])
    axs[1, 0].set_title('Entropy Utilization (% of Theoretical Maximum)')
    axs[1, 0].set_ylabel('Percentage')
    axs[1, 0].set_ylim(0, 100)
    
    for i, v in enumerate(values):
        axs[1, 0].text(i, v + 1, f"{v:.1f}%", ha='center')
    
    # 4. Edit Distance Distribution (if available)
    if candidate_analysis.get("edit_distances"):
        axs[1, 1].hist(candidate_analysis["edit_distances"], bins=range(max(candidate_analysis["edit_distances"])+2))
        axs[1, 1].set_title('Edit Distance Distribution')
        axs[1, 1].set_xlabel('Levenshtein Distance')
        axs[1, 1].set_ylabel('Frequency')
    else:
        axs[1, 1].set_title('Edit Distance Data Not Available')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    # Save the figure
    test_results_dir = ensure_test_results_dir()
    plt.savefig(os.path.join(test_results_dir, output_path))
    plt.close()
    
    print(f"Created visualization: {output_path}")

def main():
    # Get the current script directory (PasswordAnalysis folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to parent directory (sound-to-security)
    parent_dir = os.path.dirname(current_dir)
    
    # Navigate to root directory (outside sound-to-security)
    root_dir = os.path.dirname(parent_dir)
    
    # File paths based on your directory structure
    audio_data_file = os.path.join(root_dir, "audio_data.json")
    security_test_file = os.path.join(parent_dir, "PasswordGenerator", "security_test_results.json")
    
    # Output files will be saved in the current directory (PasswordAnalysis folder)
    output_json = "password_analysis_results.json"
    output_image = "password_security_analysis.png"
    
    print(f"Using audio data from: {audio_data_file}")
    print(f"Using security test results from: {security_test_file}")
    
    print(f"Analyzing passwords from {audio_data_file}...")
    original_passwords = load_passwords_from_json(audio_data_file)
    
    if not original_passwords:
        print(f"No passwords found in {audio_data_file}")
        return
    
    print(f"Found {len(original_passwords)} original passwords")
    original_analysis = analyze_passwords(original_passwords, "Original Generated Passwords")
    
    # Load security test results
    print(f"Loading security test results from {security_test_file}...")
    security_results = load_security_test_results(security_test_file)
    
    # Analyze candidate passwords
    candidate_analysis = analyze_passwords(security_results["candidate_passwords"], "Candidate Passwords")
    candidate_analysis["edit_distances"] = security_results["edit_distances"]
    
    # Print results
    print("\n=== ORIGINAL PASSWORD ANALYSIS ===")
    print(f"Number of passwords: {original_analysis['count']}")
    print(f"Average length: {original_analysis['patterns']['avg_length']:.2f} characters")
    print(f"Average entropy: {original_analysis['entropy']['avg']:.2f} bits per password")
    print(f"Average entropy per character: {original_analysis['entropy']['avg_per_char']:.2f} bits/char")
    print(f"Theoretical maximum entropy: {original_analysis['entropy']['avg_theoretical_max']:.2f} bits per password")
    print(f"Entropy utilization: {original_analysis['entropy']['utilization_percentage']:.2f}%")
    
    print("\nCharacter Class Distribution:")
    for cls in ["uppercase", "lowercase", "digits", "symbols"]:
        print(f"  {cls.capitalize()}: {original_analysis['patterns']['character_classes'][cls + '_avg']:.2f}%")
    
    print("\nTop 5 Starting Patterns:")
    for pattern, count in original_analysis['patterns']['top_start_patterns']:
        percentage = (count / original_analysis['count']) * 100
        print(f"  '{pattern}': {count} occurrences ({percentage:.2f}%)")
    
    print("\n=== CANDIDATE PASSWORD ANALYSIS ===")
    print(f"Number of passwords: {candidate_analysis['count']}")
    print(f"Average length: {candidate_analysis['patterns']['avg_length']:.2f} characters")
    print(f"Average entropy: {candidate_analysis['entropy']['avg']:.2f} bits per password")
    print(f"Average entropy per character: {candidate_analysis['entropy']['avg_per_char']:.2f} bits/char")
    print(f"Theoretical maximum entropy: {candidate_analysis['entropy']['avg_theoretical_max']:.2f} bits per password")
    print(f"Entropy utilization: {candidate_analysis['entropy']['utilization_percentage']:.2f}%")
    
    print("\nCharacter Class Distribution:")
    for cls in ["uppercase", "lowercase", "digits", "symbols"]:
        print(f"  {cls.capitalize()}: {candidate_analysis['patterns']['character_classes'][cls + '_avg']:.2f}%")
    
    print("\nTop 5 Starting Patterns:")
    for pattern, count in candidate_analysis['patterns']['top_start_patterns']:
        percentage = (count / candidate_analysis['count']) * 100
        print(f"  '{pattern}': {count} occurrences ({percentage:.2f}%)")
    
    print("\n=== Total Entropy Analysis ===")
    print(f"Average total entropy per password: {original_analysis['entropy']['average_total_entropy']:.2f} bits")
    print(f"Theoretical maximum entropy: {original_analysis['entropy']['theoretical_maximum']:.2f} bits")
    print(f"Entropy utilization ratio: {original_analysis['entropy']['utilization_ratio']:.2f}")
    
    # Save detailed results to JSON
    results = {
        "original": original_analysis,
        "candidates": candidate_analysis
    }
    
    test_results_dir = ensure_test_results_dir()
    output_json_path = os.path.join(test_results_dir, output_json)
    with open(output_json_path, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nDetailed results saved to {output_json}")
    
    # Create visualizations
    plot_entropy_comparison(original_analysis, candidate_analysis, output_image)
    
    print(f"Visualization saved to {output_image}")

if __name__ == "__main__":
    main()