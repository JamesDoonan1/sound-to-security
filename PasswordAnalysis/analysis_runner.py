"""
Run all password analysis scripts with a single command.
"""
import argparse
import time

# Import analysis modules
import comparative_analysis
import brute_force_analysis
import password_analysis
import audio_feature_correlations
import execution_time_analysis
import password_strength_analysis

def run_all_analyses():
    """Run all analysis scripts in sequence."""
    start_time = time.time()
    
    modules = [
        comparative_analysis,
        brute_force_analysis,
        password_analysis,
        audio_feature_correlations,
        execution_time_analysis,
        password_strength_analysis
    ]
    
    for i, module in enumerate(modules):
        print(f"\n[{i+1}/{len(modules)}] Running {module.__name__}...")
        module_start = time.time()
        try:
            module.main()
            print(f"Completed {module.__name__} in {time.time() - module_start:.2f} seconds")
        except Exception as e:
            print(f"Error running {module.__name__}: {str(e)}")
    
    end_time = time.time()
    print(f"\nAll analyses completed in {end_time - start_time:.2f} seconds")

def run_selected_analysis(analysis_name):
    """Run a specific analysis by name."""
    analysis_map = {
        "comparative": comparative_analysis,
        "brute_force": brute_force_analysis,
        "password": password_analysis,
        "audio_feature": audio_feature_correlations,
        "execution_time": execution_time_analysis,
        "password_strength": password_strength_analysis
    }
    
    if analysis_name not in analysis_map:
        print(f"Unknown analysis: {analysis_name}")
        print(f"Available analyses: {', '.join(analysis_map.keys())}")
        return
    
    module = analysis_map[analysis_name]
    print(f"Running {module.__name__}...")
    start_time = time.time()
    try:
        module.main()
        print(f"Completed {module.__name__} in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error running {module.__name__}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Run password analysis scripts")
    parser.add_argument(
        "--analysis", 
        choices=["all", "comparative", "brute_force", "password", 
                "audio_feature", "execution_time", "password_strength"],
        default="all", 
        help="Which analysis to run"
    )
    
    args = parser.parse_args()
    
    if args.analysis == "all":
        run_all_analyses()
    else:
        run_selected_analysis(args.analysis)

if __name__ == "__main__":
    main()