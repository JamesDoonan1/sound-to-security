"""
This script analyzes execution times for different stages of the audio-to-password pipeline.
It helps identify performance bottlenecks and benchmark your system.
"""

import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import librosa
import sys

def ensure_test_results_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_results_dir = os.path.join(current_dir, "TestResults")
    if not os.path.exists(test_results_dir):
        os.makedirs(test_results_dir)
    return test_results_dir

# Add parent directory to PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
password_generator_dir = os.path.join(parent_dir, "PasswordGenerator")
sys.path.append(password_generator_dir)

# Import modules
try:
    from audio_feature_extraction import extract_features
    from hash_password_generator import create_hash
    from ai_password_generator import AIPasswordGenerator
    from symmetric_key_generation import derive_key, new_salt
    from encrypt_decrypt_password import encrypt_password
    print("Successfully imported required modules")
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure the paths to your module files are correct")
    sys.exit(1)

def time_audio_processing(audio_files_dir, num_files=10):
    """
    Measures the execution time for each step of audio processing on multiple files.
    """
    timing_results = []
    
    # Initialize the password generator
    password_gen = AIPasswordGenerator()
    
    # Get a list of audio files
    all_files = [f for f in os.listdir(audio_files_dir) if f.endswith(('.mp3', '.wav', '.flac'))]
    files_to_process = all_files[:num_files] if len(all_files) > num_files else all_files
    
    print(f"Testing performance on {len(files_to_process)} audio files...")
    
    for file_name in files_to_process:
        file_path = os.path.join(audio_files_dir, file_name)
        print(f"Processing {file_name}...")
        
        result = {
            "file_name": file_name,
            "file_size_bytes": os.path.getsize(file_path),
            "timing": {}
        }
        
        # Time loading the audio file
        load_start = time.time()
        try:
            y, sr = librosa.load(file_path, sr=None)
            result["timing"]["audio_loading"] = time.time() - load_start
            result["audio_length_seconds"] = len(y) / sr
            
            # Time feature extraction
            feature_start = time.time()
            features = extract_features(y, sr)
            result["timing"]["feature_extraction"] = time.time() - feature_start
            
            if features:
                # Time hash generation
                hash_start = time.time()
                audio_hash = create_hash(features)
                result["timing"]["hash_generation"] = time.time() - hash_start
                
                # Time key derivation
                # Time key derivation (salted PBKDF2)
                salt_bytes = new_salt()
                key_start = time.time()
                key = derive_key(audio_hash, salt_bytes)
                result["timing"]["key_derivation"] = time.time() - key_start
                
                # Time password generation
                password_start = time.time()
                password = password_gen.generate_password(features)
                result["timing"]["password_generation"] = time.time() - password_start
                
                if password:
                    # Time encryption
                    encryption_start = time.time()
                    encrypted_pw = encrypt_password(password, key)
                    result["timing"]["password_encryption"] = time.time() - encryption_start
                    
                    # Calculate total time
                    result["timing"]["total_processing"] = sum(result["timing"].values())
                    
                    # Add to results
                    timing_results.append(result)
                    print(f"  Total processing time: {result['timing']['total_processing']:.4f} seconds")
                else:
                    print(f"  Error: Failed to generate password for {file_name}")
            else:
                print(f"  Error: Failed to extract features from {file_name}")
        except Exception as e:
            print(f"  Error processing {file_name}: {e}")
    
    return timing_results

def analyze_timing_results(timing_results):
    """
    Analyzes timing results to extract meaningful statistics and trends.
    """
    if not timing_results:
        return {"error": "No timing data available"}
    
    # Extract all the timing steps
    steps = list(timing_results[0]["timing"].keys())
    
    # Prepare analysis structure
    analysis = {
        "file_count": len(timing_results),
        "total_audio_seconds": sum(r.get("audio_length_seconds", 0) for r in timing_results),
        "steps": {},
        "correlations": {
            "audio_length_vs_total_time": [],
            "file_size_vs_total_time": []
        }
    }
    
    # Calculate statistics for each timing step
    for step in steps:
        times = [r["timing"].get(step, 0) for r in timing_results]
        analysis["steps"][step] = {
            "mean": np.mean(times),
            "median": np.median(times),
            "min": np.min(times),
            "max": np.max(times),
            "std": np.std(times)
        }
    
    # Gather data for correlation analysis
    for result in timing_results:
        if "audio_length_seconds" in result and "timing" in result and "total_processing" in result["timing"]:
            analysis["correlations"]["audio_length_vs_total_time"].append(
                (result["audio_length_seconds"], result["timing"]["total_processing"])
            )
        
        if "file_size_bytes" in result and "timing" in result and "total_processing" in result["timing"]:
            analysis["correlations"]["file_size_vs_total_time"].append(
                (result["file_size_bytes"] / 1024 / 1024, result["timing"]["total_processing"])  # Convert to MB
            )
    
    # Calculate processing speed (seconds of audio processed per second)
    if analysis["total_audio_seconds"] > 0:
        total_processing_time = sum(r["timing"].get("total_processing", 0) for r in timing_results)
        analysis["processing_speed"] = analysis["total_audio_seconds"] / total_processing_time
    
    return analysis

def visualize_timing_analysis(analysis):
    """
    Creates visualizations of timing analysis results.
    """
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    # Create figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Audio-to-Password Performance Analysis', fontsize=16)
    
    # Plot 1: Mean execution time by processing step
    steps = list(analysis["steps"].keys())
    mean_times = [analysis["steps"][step]["mean"] for step in steps]
    
    # Sort steps by execution time
    sorted_indices = np.argsort(mean_times)[::-1]  # Descending order
    sorted_steps = [steps[i] for i in sorted_indices]
    sorted_mean_times = [mean_times[i] for i in sorted_indices]
    
    bars = axs[0, 0].barh(sorted_steps, sorted_mean_times)
    axs[0, 0].set_title('Mean Execution Time by Processing Step')
    axs[0, 0].set_xlabel('Time (seconds)')
    
    # Add time values on bars
    for i, bar in enumerate(bars):
        axs[0, 0].text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                      f'{sorted_mean_times[i]:.4f}s', 
                      va='center')
    
    # Plot 2: Audio length vs total processing time correlation
    if analysis["correlations"]["audio_length_vs_total_time"]:
        x = [point[0] for point in analysis["correlations"]["audio_length_vs_total_time"]]
        y = [point[1] for point in analysis["correlations"]["audio_length_vs_total_time"]]
        
        axs[0, 1].scatter(x, y)
        axs[0, 1].set_title('Audio Length vs Processing Time')
        axs[0, 1].set_xlabel('Audio Length (seconds)')
        axs[0, 1].set_ylabel('Processing Time (seconds)')
        
        # Add trend line if we have enough data points
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            axs[0, 1].plot(x, p(x), "r--", alpha=0.8)
            axs[0, 1].text(min(x), max(y) * 0.9, f'y = {z[0]:.4f}x + {z[1]:.4f}', color='red')
    
    # Plot 3: Performance bottleneck identification (time distribution)
    labels = steps
    sizes = [analysis["steps"][step]["mean"] for step in steps]
    total = sum(sizes)
    percentages = [time / total * 100 for time in sizes]
    
    axs[1, 0].pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90)
    axs[1, 0].set_title('Processing Time Distribution by Step')
    
    # Plot 4: File size vs processing time correlation
    if analysis["correlations"]["file_size_vs_total_time"]:
        x = [point[0] for point in analysis["correlations"]["file_size_vs_total_time"]]
        y = [point[1] for point in analysis["correlations"]["file_size_vs_total_time"]]
        
        axs[1, 1].scatter(x, y)
        axs[1, 1].set_title('File Size vs Processing Time')
        axs[1, 1].set_xlabel('File Size (MB)')
        axs[1, 1].set_ylabel('Processing Time (seconds)')
        
        # Add trend line if we have enough data points
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            axs[1, 1].plot(x, p(x), "r--", alpha=0.8)
            axs[1, 1].text(min(x), max(y) * 0.9, f'y = {z[0]:.4f}x + {z[1]:.4f}', color='red')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    test_results_dir = ensure_test_results_dir()
    plt.savefig(os.path.join(test_results_dir, "execution_time_analysis.png"))
    print("Created visualization: execution_time_analysis.png")

def save_timing_data(timing_results, analysis, timing_file="timing_data.json", analysis_file="timing_analysis.json"):
    """
    Saves the raw timing data and analysis results to JSON files.
    """
    test_results_dir = ensure_test_results_dir()
    with open(os.path.join(test_results_dir, timing_file), 'w') as f:
        json.dump(timing_results, f, indent=4)
    print(f"Raw timing data saved to {timing_file}")
    
    with open(os.path.join(test_results_dir, analysis_file), 'w') as f:
        # Convert numpy values to regular Python types for JSON serialization
        for step, stats in analysis["steps"].items():
            for stat, value in stats.items():
                if isinstance(value, np.generic):
                    analysis["steps"][step][stat] = value.item()
        
        if "processing_speed" in analysis and isinstance(analysis["processing_speed"], np.generic):
            analysis["processing_speed"] = analysis["processing_speed"].item()
        
        json.dump(analysis, f, indent=4)
    print(f"Analysis results saved to {analysis_file}")

def main():
    # Get the current script directory (PasswordAnalysis folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to parent directory (sound-to-security)
    parent_dir = os.path.dirname(current_dir)
    
    # Navigate to root directory (outside sound-to-security)
    root_dir = os.path.dirname(parent_dir)
    
    audio_files_dir = "/media/sf_VM_Shared_Folder/Audio Files"
    
    # Check if the audio directory exists
    if not os.path.exists(audio_files_dir):
        print(f"Audio directory not found at {audio_files_dir}")
        audio_files_dir = input("Please enter the path to your audio files directory: ")
        if not os.path.exists(audio_files_dir):
            print("Invalid directory. Exiting.")
            return
    
    print(f"Using audio files from: {audio_files_dir}")
    print("This analysis will measure execution time for each step of the audio-to-password pipeline.")
    
    # Ask how many files to process
    try:
        num_files = int(input("How many audio files would you like to process for timing? (default: 10): ") or "10")
    except ValueError:
        num_files = 10
        print("Invalid input. Using default value of 10 files.")
    
    # Perform timing analysis
    timing_results = time_audio_processing(audio_files_dir, num_files)
    
    if not timing_results:
        print("No timing data collected. Exiting.")
        return
    
    # Analyze results
    analysis = analyze_timing_results(timing_results)
    
    # Save data
    save_timing_data(timing_results, analysis)
    
    # Create visualizations
    visualize_timing_analysis(analysis)
    
    # Print summary
    print("\n=== Execution Time Analysis Summary ===")
    print(f"Files processed: {analysis['file_count']}")
    print(f"Total audio duration: {analysis['total_audio_seconds']:.2f} seconds")
    
    # Print step timing
    print("\nAverage processing times:")
    steps = list(analysis["steps"].keys())
    steps.sort(key=lambda x: analysis["steps"][x]["mean"], reverse=True)
    
    for step in steps:
        mean_time = analysis["steps"][step]["mean"]
        percentage = (mean_time / sum(analysis["steps"][s]["mean"] for s in analysis["steps"])) * 100
        print(f"  {step}: {mean_time:.4f} seconds ({percentage:.1f}%)")
    
    # Print processing speed
    if "processing_speed" in analysis:
        print(f"\nProcessing speed: {analysis['processing_speed']:.2f}x real-time")
        print(f"(This means {analysis['processing_speed']:.2f} seconds of audio can be processed per second)")

if __name__ == "__main__":
    main()