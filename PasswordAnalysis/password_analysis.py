"""
This script analyzes the strength of audio-generated passwords compared to
candidate passwords from the fine-tuned model.
"""

from password_analysis_utils import (
    load_audio_passwords, load_security_test_results, analyze_passwords,
    get_project_paths, save_json_results, save_plot
)
import matplotlib.pyplot as plt
import numpy as np

def plot_entropy_comparison(original_analysis, candidate_analysis, output_path):
    """Create visualizations comparing entropy between original and candidate passwords."""
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
    
    # Save the figure
    save_plot(fig, output_path)

def main():
    # Get paths
    paths = get_project_paths()
    audio_data_file = paths["audio_data_path"]
    security_test_file = paths["security_test_path"]
    output_json = "password_analysis_results.json"
    output_image = "password_security_analysis.png"
    
    print(f"Using audio data from: {audio_data_file}")
    print(f"Using security test results from: {security_test_file}")
    
    # Load and analyze passwords
    original_passwords = load_audio_passwords(audio_data_file)
    if not original_passwords:
        print(f"No passwords found in {audio_data_file}")
        return
    
    original_analysis = analyze_passwords(original_passwords, "Original Generated Passwords")
    
    # Load and analyze candidate passwords
    security_results = load_security_test_results(security_test_file)
    candidate_analysis = analyze_passwords(security_results["candidate_passwords"], "Candidate Passwords")
    candidate_analysis["edit_distances"] = security_results["edit_distances"]
    
    # Print summary results
    print_summary_results(original_analysis, candidate_analysis)
    
    # Create visualizations
    plot_entropy_comparison(original_analysis, candidate_analysis, output_image)
    
    # Save results
    save_json_results({
        "original": original_analysis,
        "candidates": candidate_analysis
    }, output_json)

def print_summary_results(original_analysis, candidate_analysis):
    """Print a summary of the analysis results to the console."""
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

if __name__ == "__main__":
    main()