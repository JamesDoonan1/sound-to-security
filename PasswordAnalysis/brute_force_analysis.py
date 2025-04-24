"""
This script analyzes the resistance of your audio-generated passwords to brute force attacks
by calculating theoretical attack times and simulating attack attempts.
"""

from password_analysis_utils import (
    get_project_paths, load_audio_passwords, load_security_test_results,
    calculate_entropy, save_json_results,
    save_plot, format_time_estimate
)
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import string
import time
from collections import Counter
from tqdm import tqdm

def analyze_password_character_space(passwords):
    """
    Analyze the character space used by the passwords to estimate brute force complexity.
    """
    if not passwords:
        return {"error": "No passwords provided"}
    
    # Collect all unique characters used across all passwords
    all_chars = set()
    for password in passwords:
        if password:
            all_chars.update(set(password))
    
    # Count character types
    uppercase = sum(1 for c in all_chars if c.isupper())
    lowercase = sum(1 for c in all_chars if c.islower())
    digits = sum(1 for c in all_chars if c.isdigit())
    symbols = sum(1 for c in all_chars if not c.isalnum())
    
    # Get average password length
    avg_length = np.mean([len(p) for p in passwords if p])
    
    # Calculate character space size
    char_space_size = len(all_chars)
    
    # Calculate theoretical combinations based on character space and average length
    theoretical_combinations_char_space = char_space_size ** avg_length
    
    # Calculate theoretical combinations based on full ASCII printable space (95 chars)
    theoretical_combinations_full_space = 95 ** avg_length
    
    # Calculate theoretical combinations based on character class division
    class_based_space = (uppercase + lowercase + digits + symbols) ** avg_length
    
    # Calculate theoretical maximum entropy based on character space and average length
    theoretical_max_entropy = math.log2(char_space_size) * avg_length
    
    # Calculate average true entropy of the passwords
    average_entropy = np.mean([calculate_entropy(p) for p in passwords if p])
    
    return {
        "unique_characters": list(all_chars),
        "character_space_size": char_space_size,
        "average_password_length": avg_length,
        "character_class_counts": {
            "uppercase": uppercase,
            "lowercase": lowercase,
            "digits": digits,
            "symbols": symbols
        },
        "theoretical_combinations": {
            "using_observed_character_space": theoretical_combinations_char_space,
            "using_full_ascii_printable": theoretical_combinations_full_space,
            "using_character_class_counts": class_based_space
        },
        "theoretical_entropy": {
            "maximum": theoretical_max_entropy,
            "per_character": math.log2(char_space_size)
        },
        "average_actual_entropy": average_entropy
    }

def estimate_brute_force_times(character_space_analysis):
    """
    Estimate the time required for different types of brute force attacks.
    """
    if "error" in character_space_analysis:
        return {"error": character_space_analysis["error"]}
    
    # Define different cracking speeds (attempts per second)
    cracking_speeds = {
        "online_attack": 10,                 # 10 attempts per second (limited by server)
        "offline_slow": 1e3,                 # 1,000 attempts per second (basic PC)
        "offline_fast": 1e6,                 # 1 million attempts per second (dedicated PC)
        "offline_gpu": 1e9,                  # 1 billion attempts per second (GPU cluster)
        "offline_specialized": 1e12,         # 1 trillion attempts per second (specialized hardware)
        "quantum_computer": 1e15             # 1 quadrillion attempts per second (theoretical quantum)
    }
    
    # Calculate time estimates for each attack method and combination space
    results = {}
    
    for space_type, combinations in character_space_analysis["theoretical_combinations"].items():
        results[space_type] = {}
        
        for attack_type, speed in cracking_speeds.items():
            seconds = combinations / speed
            results[space_type][attack_type] = seconds
    
    # Add time estimates based on actual entropy
    if "average_actual_entropy" in character_space_analysis:
        entropy = character_space_analysis["average_actual_entropy"]
        results["using_actual_entropy"] = {}
        
        for attack_type, speed in cracking_speeds.items():
            # Time = 2^entropy / speed
            seconds = (2 ** entropy) / speed
            results["using_actual_entropy"][attack_type] = seconds
    
    return results

def simulate_brute_force_attacks(passwords, num_attempts=1000, strategy="random"):
    """
    Simulate different brute force attack strategies and measure success rate.
    
    Strategies:
    - random: completely random characters
    - smart: biased toward character distributions in the passwords
    - pattern: tries to replicate patterns seen in passwords
    """
    if not passwords:
        return {"error": "No passwords provided"}
    
    results = {
        "strategies": {},
        "character_stats": {}
    }
    
    # Analyze character frequency in the real passwords
    all_chars = ""
    for password in passwords:
        if password:
            all_chars += password
    
    char_freq = Counter(all_chars)
    total_chars = len(all_chars)
    char_prob = {c: count/total_chars for c, count in char_freq.items()}
    
    # Store character stats
    results["character_stats"] = {
        "most_common": char_freq.most_common(10),
        "character_probabilities": char_prob
    }
    
    # Get average password length
    avg_length = int(np.mean([len(p) for p in passwords if p]))
    
    # For each strategy
    strategies = ["random", "smart", "pattern"]
    
    for strategy_name in strategies:
        print(f"Simulating {strategy_name} brute force strategy...")
        matches = 0
        start_time = time.time()
        
        # Generate attempt passwords
        attempts = []
        
        if strategy_name == "random":
            # Completely random characters from ASCII printable
            all_printable = string.ascii_letters + string.digits + string.punctuation
            for _ in tqdm(range(num_attempts)):
                attempt = ''.join(random.choice(all_printable) for _ in range(avg_length))
                attempts.append(attempt)
        
        elif strategy_name == "smart":
            # Biased toward character distributions in the real passwords
            chars_list = list(char_prob.keys())
            weights = list(char_prob.values())
            
            for _ in tqdm(range(num_attempts)):
                attempt = ''.join(random.choices(chars_list, weights=weights, k=avg_length))
                attempts.append(attempt)
        
        elif strategy_name == "pattern":
            # Try to replicate patterns seen in passwords
            # Look at first 2 chars, last 2 chars, and character class patterns
            
            # Get most common starting and ending patterns
            starts = Counter([p[:2] for p in passwords if len(p) >= 2])
            ends = Counter([p[-2:] for p in passwords if len(p) >= 2])
            
            # Get character class patterns (simplified as a string of U, L, D, S)
            class_patterns = []
            for password in passwords:
                if not password:
                    continue
                pattern = ""
                for char in password:
                    if char.isupper():
                        pattern += "U"
                    elif char.islower():
                        pattern += "L"
                    elif char.isdigit():
                        pattern += "D"
                    else:
                        pattern += "S"
                class_patterns.append(pattern)
            
            common_patterns = Counter(class_patterns).most_common(5)
            
            # Generate attempts based on patterns
            for _ in tqdm(range(num_attempts)):
                if random.random() < 0.7:  # 70% chance to use common start
                    common_start = random.choice([s for s, _ in starts.most_common(3)])
                    password_start = common_start
                else:
                    password_start = ''.join(random.choices(chars_list, weights=weights, k=2))
                
                if random.random() < 0.7:  # 70% chance to use common end
                    common_end = random.choice([e for e, _ in ends.most_common(3)])
                    password_end = common_end
                else:
                    password_end = ''.join(random.choices(chars_list, weights=weights, k=2))
                
                # Fill middle section
                if avg_length > 4:
                    middle_length = avg_length - 4
                    middle = ''.join(random.choices(chars_list, weights=weights, k=middle_length))
                    attempt = password_start + middle + password_end
                else:
                    attempt = password_start + password_end
                    attempt = attempt[:avg_length]  # Ensure correct length
                
                attempts.append(attempt)
        
        # Check for matches
        for attempt in attempts:
            if attempt in passwords:
                matches += 1
        
        end_time = time.time()
        
        # Store results
        results["strategies"][strategy_name] = {
            "attempts": num_attempts,
            "matches": matches,
            "success_rate": matches / num_attempts * 100,
            "execution_time_seconds": end_time - start_time,
            "attempts_per_second": num_attempts / (end_time - start_time)
        }
    
    return results

def analyze_edit_distances(security_test_results):
    """
    Analyze the edit distances between actual passwords and guessed candidates.
    """
    if not security_test_results or "edit_distances" not in security_test_results or not security_test_results["edit_distances"]:
        return {"error": "No edit distance data available"}
    
    edit_distances = security_test_results["edit_distances"]
    
    analysis = {
        "count": len(edit_distances),
        "min": min(edit_distances),
        "max": max(edit_distances),
        "mean": np.mean(edit_distances),
        "median": np.median(edit_distances),
        "std": np.std(edit_distances),
        "distribution": Counter(edit_distances)
    }
    
    # Calculate the percentage of passwords within certain edit distances
    for dist in range(1, 6):
        analysis[f"within_distance_{dist}"] = sum(1 for d in edit_distances if d <= dist) / len(edit_distances) * 100
    
    return analysis

def calculate_average_attempts_needed(edit_distance_analysis, avg_password_length):
    """
    Estimate the average number of attempts needed to guess a password based on edit distances.
    
    This is a rough approximation based on the probability of correctly guessing
    a character at each position and the average edit distance.
    """
    if "error" in edit_distance_analysis:
        return {"error": edit_distance_analysis["error"]}
    
    # Average number of positions that need to be changed
    avg_edit_distance = edit_distance_analysis["mean"]
    
    # Probability of guessing a single character correctly
    # Assuming 95 possible characters per position (ASCII printable)
    p_correct = 1/95
    
    # Probability of guessing the entire password correctly
    p_correct_password = (p_correct) ** avg_edit_distance
    
    # Expected number of attempts needed
    expected_attempts = 1 / p_correct_password
    
    return {
        "average_edit_distance": avg_edit_distance,
        "probability_correct_guess_per_character": p_correct,
        "probability_correct_password": p_correct_password,
        "expected_attempts_needed": expected_attempts
    }

def visualize_brute_force_analysis(character_space_analysis, time_estimates, simulation_results, edit_distance_analysis, expected_attempts):
    """
    Create visualizations of brute force analysis results.
    """
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Brute Force Attack Resistance Analysis', fontsize=16)
    
    # Plot 1: Character Space Distribution
    char_classes = character_space_analysis["character_class_counts"]
    ax1 = axs[0, 0]
    ax1.pie([char_classes["uppercase"], char_classes["lowercase"], char_classes["digits"], char_classes["symbols"]],
            labels=["Uppercase", "Lowercase", "Digits", "Symbols"],
            autopct='%1.1f%%', startangle=90)
    ax1.set_title('Character Space Distribution')
    
    # Add real entropy information
    if "average_actual_entropy" in character_space_analysis:
        real_entropy = character_space_analysis["average_actual_entropy"]
        theoretical_max = character_space_analysis["theoretical_entropy"]["maximum"]
        ax1.text(-0.5, -1.2, f"Actual Entropy: {real_entropy:.2f} bits\nMax Theoretical: {theoretical_max:.2f} bits", 
                fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
    
    # Plot 2: Brute Force Time Estimates (log scale)
    ax2 = axs[0, 1]
    attack_types = list(time_estimates["using_observed_character_space"].keys())
    
    # Convert times to log years for better visualization
    log_years = []
    for attack in attack_types:
        seconds = time_estimates["using_observed_character_space"][attack]
        years = seconds / 31536000  # seconds to years
        log_years.append(np.log10(max(1e-10, years)))  # avoid log(0)
    
    bars = ax2.barh(attack_types, log_years)
    ax2.set_title('Time to Brute Force (Log₁₀ Years)')
    ax2.set_xlabel('Log₁₀(Years)')
    
    # Add actual time estimates as text
    # Add actual time estimates as text
    for i, bar in enumerate(bars):
        seconds = time_estimates["using_observed_character_space"][attack_types[i]]
        time_str = format_time_estimate(seconds)
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, time_str, va='center')
    
    # Plot 3: Simulation Success Rates
    ax3 = axs[1, 0]
    if simulation_results and "strategies" in simulation_results:
        strategies = list(simulation_results["strategies"].keys())
        success_rates = [simulation_results["strategies"][s]["success_rate"] for s in strategies]
        
        bars = ax3.bar(strategies, success_rates)
        ax3.set_title('Brute Force Simulation Success Rates')
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_ylim(0, max(0.1, max(success_rates) * 1.2))  # Set y-limit with some padding
        
        # Add values on bars
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.6f}%', ha='center', va='bottom')
    else:
        ax3.text(0.5, 0.5, 'No simulation data available', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot 4: Edit Distance Distribution
    ax4 = axs[1, 1]
    if "error" not in edit_distance_analysis:
        distances = list(edit_distance_analysis["distribution"].keys())
        counts = list(edit_distance_analysis["distribution"].values())
        
        # Sort by distance
        sorted_data = sorted(zip(distances, counts))
        distances = [d for d, _ in sorted_data]
        counts = [c for _, c in sorted_data]
        
        ax4.bar(distances, counts)
        ax4.set_title('Edit Distance Distribution')
        ax4.set_xlabel('Edit Distance')
        ax4.set_ylabel('Frequency')
        
        # Add expected attempts text
        if "error" not in expected_attempts:
            ax4.text(0.5, 0.9, f'Expected attempts needed: {expected_attempts["expected_attempts_needed"]:.2e}', 
                     transform=ax4.transAxes, ha='center', bbox=dict(facecolor='white', alpha=0.8))
    else:
        ax4.text(0.5, 0.5, 'No edit distance data available', 
                horizontalalignment='center', verticalalignment='center')
    
    # Save the figure
    save_plot(fig, 'brute_force_analysis.png')

def main():
    # Get paths
    paths = get_project_paths()
    audio_data_path = paths["audio_data_path"]
    security_test_path = paths["security_test_path"]
    
    print("Starting brute force resistance analysis...")
    
    # Load passwords and security test results
    audio_passwords = load_audio_passwords(audio_data_path)
    security_test_results = load_security_test_results(security_test_path)
    
    if not audio_passwords:
        print("Error: No audio passwords found. Check the path to your audio_data.json file.")
        return
    
    # Analyze password character space
    print("Analyzing password character space...")
    character_space_analysis = analyze_password_character_space(audio_passwords)
    
    # Estimate brute force times
    print("Estimating brute force attack times...")
    time_estimates = estimate_brute_force_times(character_space_analysis)
    
    # Simulate brute force attacks
    try:
        num_attempts = int(input("How many brute force attempts to simulate? (default: 10000): ") or "10000")
    except ValueError:
        num_attempts = 10000
        print("Invalid input. Using default value of 10000 attempts.")
    
    simulation_results = simulate_brute_force_attacks(audio_passwords, num_attempts)
    
    # Analyze edit distances from security tests
    print("Analyzing edit distances from security tests...")
    edit_distance_analysis = analyze_edit_distances(security_test_results)
    
    # Calculate expected attempts needed
    expected_attempts = calculate_average_attempts_needed(
        edit_distance_analysis, 
        character_space_analysis["average_password_length"]
    )
    
    # Save all results
    results = {
        "character_space_analysis": character_space_analysis, 
        "time_estimates": time_estimates, 
        "simulation_results": simulation_results, 
        "edit_distance_analysis": edit_distance_analysis, 
        "expected_attempts": expected_attempts
    }
    save_json_results(results, "brute_force_analysis_results.json")
    
    # Create visualizations
    print("Creating visualizations...")
    visualize_brute_force_analysis(
        character_space_analysis, 
        time_estimates, 
        simulation_results,
        edit_distance_analysis,
        expected_attempts
    )
    
    # Print summary
    print_summary_results(character_space_analysis, time_estimates, simulation_results, 
                         edit_distance_analysis, expected_attempts)

def print_summary_results(character_space_analysis, time_estimates, simulation_results, 
                         edit_distance_analysis, expected_attempts):
    """Print a summary of brute force analysis results to the console."""
    print("\n=== Brute Force Resistance Analysis Summary ===")
    
    print(f"\nCharacter Space:")
    print(f"  Unique characters used: {character_space_analysis['character_space_size']}")
    print(f"  Average password length: {character_space_analysis['average_password_length']:.2f} characters")
    
    print(f"\nTheoretical Entropy Analysis:")
    print(f"  Maximum possible entropy: {character_space_analysis['theoretical_entropy']['maximum']:.2f} bits")
    print(f"  Maximum bits per character: {character_space_analysis['theoretical_entropy']['per_character']:.2f} bits/char")
    
    print(f"\nTime Estimates (using observed character space):")
    for attack_type, seconds in time_estimates["using_observed_character_space"].items():
        time_str = format_time_estimate(seconds)
        print(f"  {attack_type}: {time_str}")
    
    if "error" not in simulation_results:
        print(f"\nSimulation Results ({simulation_results['strategies']['random']['attempts']} attempts):")
        for strategy, results in simulation_results["strategies"].items():
            print(f"  {strategy} strategy: {results['matches']} matches ({results['success_rate']:.6f}%)")
    
    if "error" not in edit_distance_analysis:
        print(f"\nEdit Distance Analysis:")
        print(f"  Mean edit distance: {edit_distance_analysis['mean']:.2f}")
        print(f"  Min edit distance: {edit_distance_analysis['min']}")
        print(f"  Max edit distance: {edit_distance_analysis['max']}")
        print(f"  % within distance 3: {edit_distance_analysis.get('within_distance_3', 0):.2f}%")
    
    if "error" not in expected_attempts:
        print(f"\nExpected Brute Force Attempts Needed:")
        print(f"  {expected_attempts['expected_attempts_needed']:.2e} attempts")

if __name__ == "__main__":
    main()