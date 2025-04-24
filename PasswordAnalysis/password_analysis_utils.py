import os
import json
import matplotlib.pyplot as plt
import math
from collections import Counter

# Directory management
def ensure_test_results_dir():
    """Create TestResults directory if it doesn't exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_results_dir = os.path.join(current_dir, "TestResults")
    if not os.path.exists(test_results_dir):
        os.makedirs(test_results_dir)
    return test_results_dir

# File loading
def load_audio_passwords(audio_data_path):
    """Load passwords from audio_data.json file."""
    try:
        with open(audio_data_path, 'r') as f:
            data = json.load(f)
        passwords = [entry.get("password") for entry in data if entry.get("password")]
        print(f"Loaded {len(passwords)} audio-generated passwords")
        return passwords
    except Exception as e:
        print(f"Error loading audio-generated passwords: {e}")
        return []

def load_security_test_results(security_test_path):
    """Load security test results containing candidate passwords."""
    try:
        with open(security_test_path, 'r') as f:
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
        print(f"Error loading security test results: {e}")
        return {"base_passwords": [], "candidate_passwords": [], "edit_distances": []}

# Password analysis
def calculate_entropy(password):
    """Calculate true password strength entropy based on character set size and length."""
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

def analyze_character_classes(password):
    """Analyze character class distribution in a password."""
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
    """Comprehensive analysis of a set of passwords."""
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
        theoretical_max = math.log2(95) * length
        
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
    
    # Average length
    results["patterns"]["avg_length"] = sum(results["patterns"]["length"]) / len(valid_passwords)
    
    # Total entropy metrics
    results["entropy"]["average_total_entropy"] = results["entropy"]["avg"]
    results["entropy"]["theoretical_maximum"] = math.log2(95) * results["patterns"]["avg_length"]
    results["entropy"]["utilization_ratio"] = results["entropy"]["average_total_entropy"] / results["entropy"]["theoretical_maximum"]
    
    # Average character class distribution
    for cls in list(results["patterns"]["character_classes"].keys()):
        avg_key = cls + "_avg"
        results["patterns"]["character_classes"][avg_key] = sum(results["patterns"]["character_classes"][cls]) / len(valid_passwords)
    
    # Top start patterns
    results["patterns"]["top_start_patterns"] = results["patterns"]["start_patterns"].most_common(5)
    
    return results

# Visualization helpers
def save_plot(fig, filename):
    """Save a matplotlib figure to the TestResults directory."""
    test_results_dir = ensure_test_results_dir()
    plt.tight_layout()
    plt.savefig(os.path.join(test_results_dir, filename))
    plt.close(fig)
    print(f"Created visualization: {filename}")

def save_json_results(results, filename):
    """Save results to a JSON file in the TestResults directory."""
    test_results_dir = ensure_test_results_dir()
    with open(os.path.join(test_results_dir, filename), 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {filename}")

# Path helpers
def get_project_paths():
    """Get common paths used across analysis scripts."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    root_dir = os.path.dirname(parent_dir)
    
    return {
        "current_dir": current_dir,
        "parent_dir": parent_dir,
        "root_dir": root_dir,
        "audio_data_path": os.path.join(root_dir, "audio_data.json"),
        "security_test_path": os.path.join(parent_dir, "PasswordGenerator", "security_test_results.json")
    }

# Format helpers
def format_time_estimate(seconds):
    """Format a time estimate in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} hours"
    elif seconds < 31536000:
        return f"{seconds/86400:.2f} days"
    elif seconds < 31536000 * 100:
        return f"{seconds/31536000:.2f} years"
    elif seconds < 31536000 * 1e6:
        return f"{seconds/31536000/1000:.2f} thousand years"
    elif seconds < 31536000 * 1e9:
        return f"{seconds/31536000/1e6:.2f} million years"
    elif seconds < 31536000 * 1e12:
        return f"{seconds/31536000/1e9:.2f} billion years"
    else:
        return f"{seconds/31536000/1e12:.2f} trillion years"