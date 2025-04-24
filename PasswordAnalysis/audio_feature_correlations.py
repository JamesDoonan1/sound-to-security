"""
This script analyzes correlations between audio features and password characteristics
to demonstrate how audio properties influence the generated passwords.
"""

from password_analysis_utils import (
    get_project_paths, save_json_results, save_plot
)
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import pandas as pd

def extract_audio_features(entry):
    """Extracts relevant audio features from a data entry."""
    features = entry.get("features", {})
    
    # Extract key audio features that might influence password generation
    result = {}
    
    # Extract mean values for various audio features
    feature_keys = {
        "Tempo": "tempo",
        "Spectral Centroid": "spectral_centroid",
        "MFCCs": "mfcc_mean",
        "Zero-Crossing Rate": "zero_crossing_rate",
        "Beats": "beats_mean",
        "Spectral Contrast": "spectral_contrast"
    }
    
    for orig_key, new_key in feature_keys.items():
        if orig_key in features and "mean" in features[orig_key]:
            result[new_key] = features[orig_key]["mean"]
    
    return result

def analyze_password_characteristics(password):
    """Extracts various characteristics from a password."""
    if not password:
        return None
    
    # Character class distribution
    uppercase_count = sum(1 for c in password if c.isupper())
    lowercase_count = sum(1 for c in password if c.islower())
    digit_count = sum(1 for c in password if c.isdigit())
    symbol_count = sum(1 for c in password if not c.isalnum())
    
    length = len(password)
    
    def calculate_entropy(s):
        """Calculate Shannon entropy of a string."""
        if not s:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in s:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0
        for count in char_counts.values():
            p_x = count / length
            entropy -= p_x * np.log2(p_x)
        
        return entropy
    
    return {
        "length": length,
        "uppercase_pct": (uppercase_count / length) * 100 if length > 0 else 0,
        "lowercase_pct": (lowercase_count / length) * 100 if length > 0 else 0,
        "digit_pct": (digit_count / length) * 100 if length > 0 else 0,
        "symbol_pct": (symbol_count / length) * 100 if length > 0 else 0,
        "entropy": calculate_entropy(password),
        "uppercase_count": uppercase_count,
        "lowercase_count": lowercase_count,
        "digit_count": digit_count,
        "symbol_count": symbol_count,
        "starts_with_uppercase": password[0].isupper() if password else False,
        "starts_with_symbol": not password[0].isalnum() if password else False
    }

def analyze_audio_feature_correlations(audio_data_path):
    """Analyzes correlations between audio features and password characteristics."""
    print(f"Loading data from {audio_data_path}...")
    
    try:
        with open(audio_data_path, 'r') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} entries from audio data")
        
        # Process each entry
        correlations_data = []
        
        for entry in data:
            password = entry.get("password")
            
            if not password:
                continue
            
            # Extract password characteristics
            password_chars = analyze_password_characteristics(password)
            if not password_chars:
                continue
            
            # Extract audio features
            audio_features = extract_audio_features(entry)
            if not audio_features:
                continue
            
            # Combine into a single entry
            combined_entry = {
                "password": password,
                "hash": entry.get("hash", ""),
                **password_chars,
                **audio_features
            }
            
            correlations_data.append(combined_entry)
        
        print(f"Processed {len(correlations_data)} valid entries")
        
        if not correlations_data:
            return {"error": "No valid data found for correlation analysis"}
        
        return correlations_data
    
    except Exception as e:
        print(f"Error analyzing correlations: {e}")
        return {"error": str(e)}

def calculate_correlation_matrix(correlations_data):
    """Calculates the correlation matrix between audio features and password characteristics."""
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(correlations_data)
    
    # Select audio features
    audio_features = [
        'tempo', 'spectral_centroid', 'mfcc_mean', 'zero_crossing_rate', 
        'beats_mean', 'spectral_contrast'
    ]
    
    # Select password characteristics
    password_chars = [
        'uppercase_pct', 'lowercase_pct', 'digit_pct', 'symbol_pct', 
        'entropy', 'starts_with_uppercase', 'starts_with_symbol'
    ]
    
    # Filter to include only columns that exist in the data
    audio_features = [f for f in audio_features if f in df.columns]
    password_chars = [c for c in password_chars if c in df.columns]
    
    if not audio_features or not password_chars:
        return {"error": "No valid features found for correlation analysis"}
    
    # Calculate correlation matrix
    correlation_matrix = pd.DataFrame(index=audio_features, columns=password_chars)
    p_values_matrix = pd.DataFrame(index=audio_features, columns=password_chars)
    
    for feature in audio_features:
        for char in password_chars:
            if df[feature].dtype == bool or df[char].dtype == bool:
                # Convert boolean to numeric for correlation
                feature_values = df[feature].astype(int) if df[feature].dtype == bool else df[feature]
                char_values = df[char].astype(int) if df[char].dtype == bool else df[char]
            else:
                feature_values = df[feature]
                char_values = df[char]
            
            # Handle non-numeric data
            if not pd.api.types.is_numeric_dtype(feature_values) or not pd.api.types.is_numeric_dtype(char_values):
                correlation_matrix.loc[feature, char] = np.nan
                p_values_matrix.loc[feature, char] = np.nan
                continue
            
            # Remove NaN values
            mask = ~np.isnan(feature_values) & ~np.isnan(char_values)
            if mask.sum() < 2:  # Need at least 2 valid pairs
                correlation_matrix.loc[feature, char] = np.nan
                p_values_matrix.loc[feature, char] = np.nan
                continue
            
            corr, p_value = pearsonr(feature_values[mask], char_values[mask])
            correlation_matrix.loc[feature, char] = corr
            p_values_matrix.loc[feature, char] = p_value
    
    return {
        "correlation_matrix": correlation_matrix,
        "p_values_matrix": p_values_matrix,
        "data_frame": df
    }

def visualize_correlations(correlation_results, output_path="audio_feature_correlations.png"):
    """Creates visualizations of the correlations between audio features and password characteristics."""
    if "error" in correlation_results:
        print(f"Error: {correlation_results['error']}")
        return
    
    correlation_matrix = correlation_results["correlation_matrix"]
    p_values_matrix = correlation_results["p_values_matrix"]
    df = correlation_results["data_frame"]
    
    # Convert correlation matrix to numeric values for visualization
    correlation_matrix_numeric = correlation_matrix.astype(float)
    
    # Create a figure with multiple plots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Correlation Heatmap
    plt.subplot(2, 2, 1)
    sns.heatmap(correlation_matrix_numeric, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, fmt=".2f")
    plt.title('Correlation Between Audio Features and Password Characteristics')
    
    # 2. Significant Correlations (p < 0.05)
    plt.subplot(2, 2, 2)
    # Mark insignificant correlations as NaN
    significant_matrix = correlation_matrix_numeric.copy()
    p_values_numeric = p_values_matrix.astype(float)
    significant_matrix[p_values_numeric >= 0.05] = np.nan
    
    # Ensure no NaN values in the heatmap
    significant_matrix_clean = significant_matrix.fillna(0)
    mask = np.isnan(significant_matrix)
    
    sns.heatmap(significant_matrix_clean, annot=significant_matrix, cmap='coolwarm', 
                vmin=-1, vmax=1, center=0, mask=mask, fmt=".2f")
    plt.title('Statistically Significant Correlations (p < 0.05)')
    
    # Find strongest correlation for detailed plot
    strongest_corr = 0
    strongest_feature = ""
    strongest_char = ""
    
    for feature in correlation_matrix.index:
        for char in correlation_matrix.columns:
            try:
                corr_value = float(correlation_matrix.loc[feature, char])
                if not np.isnan(corr_value) and abs(corr_value) > abs(strongest_corr):
                    strongest_corr = corr_value
                    strongest_feature = feature
                    strongest_char = char
            except (ValueError, TypeError):
                continue
    
    # Plot strongest correlation as scatter
    if strongest_feature and strongest_char:
        plt.subplot(2, 2, 3)
        try:
            # Extract data with safe conversion to numeric
            x = pd.to_numeric(df[strongest_feature], errors='coerce')
            y = pd.to_numeric(df[strongest_char], errors='coerce')
            
            # Remove NaN values
            mask = ~np.isnan(x) & ~np.isnan(y)
            
            if mask.sum() > 1:  # Need at least 2 points for a scatter plot
                sns.scatterplot(x=x[mask], y=y[mask])
                plt.title(f'Strongest Correlation: {strongest_feature} vs {strongest_char} (r={strongest_corr:.2f})')
                plt.xlabel(strongest_feature)
                plt.ylabel(strongest_char)
                
                # Add trend line
                z = np.polyfit(x[mask], y[mask], 1)
                p = np.poly1d(z)
                plt.plot(x[mask], p(x[mask]), "r--", alpha=0.8)
            else:
                plt.text(0.5, 0.5, 'Insufficient data for scatter plot', 
                        horizontalalignment='center', verticalalignment='center')
        except Exception as e:
            plt.text(0.5, 0.5, f'Error creating scatter plot: {str(e)}', 
                    horizontalalignment='center', verticalalignment='center')
    
    # Key Findings Box
    plt.subplot(2, 2, 4)
    plt.axis('off')
    
    # Find top 5 correlations
    correlations_flat = []
    for feature in correlation_matrix.index:
        for char in correlation_matrix.columns:
            try:
                corr_value = float(correlation_matrix.loc[feature, char])
                p_value = float(p_values_matrix.loc[feature, char])
                if not np.isnan(corr_value) and not np.isnan(p_value):
                    correlations_flat.append((feature, char, corr_value, p_value))
            except (ValueError, TypeError):
                continue
    
    # Sort by absolute correlation value
    correlations_flat.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # Create text for key findings
    findings_text = "Key Findings:\n\n"
    
    for i, (feature, char, corr, p_value) in enumerate(correlations_flat[:5]):
        sign = "positively" if corr > 0 else "negatively"
        sig_text = "statistically significant" if p_value < 0.05 else "not statistically significant"
        findings_text += f"{i+1}. {feature.replace('_', ' ').title()} is {sign} correlated with {char.replace('_', ' ').title()}\n"
        findings_text += f"   Correlation: {corr:.2f}, p-value: {p_value:.4f} ({sig_text})\n\n"
    
    # Calculate average correlations for each audio feature
    avg_correlations = {}
    for feature in correlation_matrix.index:
        values = []
        for char in correlation_matrix.columns:
            try:
                val = float(correlation_matrix.loc[feature, char])
                if not np.isnan(val):
                    values.append(val)
            except (ValueError, TypeError):
                continue
        
        if values:
            avg_correlations[feature] = np.mean(np.abs(values))
    
    # Add most influential audio features
    if avg_correlations:
        most_influential = sorted(avg_correlations.items(), key=lambda x: x[1], reverse=True)
        findings_text += "Most Influential Audio Features:\n"
        for feature, avg_corr in most_influential[:3]:
            findings_text += f"- {feature.replace('_', ' ').title()}: Avg. |r| = {avg_corr:.2f}\n"
    
    plt.text(0.05, 0.95, findings_text, fontsize=12, verticalalignment='top')
    
    # Save the figure
    save_plot(fig, output_path)

def main():
    # Get paths
    paths = get_project_paths()
    audio_data_path = paths["audio_data_path"]
    
    print("Starting audio feature correlation analysis...")
    
    # Load and analyze data
    correlations_data = analyze_audio_feature_correlations(audio_data_path)
    
    if isinstance(correlations_data, dict) and "error" in correlations_data:
        print(f"Analysis error: {correlations_data['error']}")
        return
    
    # Calculate correlations
    correlation_results = calculate_correlation_matrix(correlations_data)
    
    # Create a copy for visualization and printing (keeps DataFrames intact)
    visualization_results = correlation_results.copy()
    
    # Convert DataFrames to dictionaries for JSON serialization
    if isinstance(correlation_results["correlation_matrix"], pd.DataFrame):
        correlation_results["correlation_matrix"] = correlation_results["correlation_matrix"].to_dict()
    if isinstance(correlation_results["p_values_matrix"], pd.DataFrame):
        correlation_results["p_values_matrix"] = correlation_results["p_values_matrix"].to_dict()
    if isinstance(correlation_results["data_frame"], pd.DataFrame):
        correlation_results["data_frame"] = correlation_results["data_frame"].to_dict('records')
    
    # Save detailed results
    save_json_results(correlation_results, "audio_feature_correlations.json")
    
    # Create visualizations (using original DataFrames)
    visualize_correlations(visualization_results)
    
    # Print summary (using original DataFrames)
    print_correlation_summary(visualization_results)

def print_correlation_summary(correlation_results):
    """Print a summary of correlation findings to the console."""
    if "error" in correlation_results:
        print(f"Error in correlation analysis: {correlation_results['error']}")
        return
    
    print("\n=== Audio Feature Correlation Analysis Results ===")
    correlation_matrix = correlation_results["correlation_matrix"]
    p_values_matrix = correlation_results["p_values_matrix"]
    
    # Find strongest correlations
    correlations_flat = []
    for feature in correlation_matrix.index:
        for char in correlation_matrix.columns:
            corr_value = correlation_matrix.loc[feature, char]
            p_value = p_values_matrix.loc[feature, char]
            if not np.isnan(corr_value) and not np.isnan(p_value):
                correlations_flat.append((feature, char, corr_value, p_value))
    
    # Sort by absolute correlation value
    correlations_flat.sort(key=lambda x: abs(x[2]), reverse=True)
    
    # Print top 5 correlations
    print("\nTop 5 strongest correlations:")
    for i, (feature, char, corr, p_value) in enumerate(correlations_flat[:5]):
        sig_text = "*statistically significant*" if p_value < 0.05 else "not statistically significant"
        print(f"{i+1}. {feature} → {char}: r={corr:.2f}, p={p_value:.4f} ({sig_text})")
    
    # Calculate which audio features have the strongest influence overall
    feature_influence = {}
    for feature in correlation_matrix.index:
        values = correlation_matrix.loc[feature, :].dropna()
        if len(values) > 0:
            feature_influence[feature] = np.abs(values).mean()
    
    # Print most influential features
    if feature_influence:
        print("\nMost influential audio features (by average absolute correlation):")
        sorted_features = sorted(feature_influence.items(), key=lambda x: x[1], reverse=True)
        for feature, influence in sorted_features:
            print(f"- {feature}: {influence:.2f}")

if __name__ == "__main__":
    main()