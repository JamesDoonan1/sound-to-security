# **From Sound-to-Security: Audio-Based Password Authentication System**

Author: Cormac Geraghty
Institution: Atlantic Technological University (ATU), Galway
Dissertation Type: Minor Dissertation (B.Sc. (Hons) in Software Development)
Repository: JamesDoonan1/sound-to-security
Branch for this project: feature/audio-passwords

- This repository contains an innovative authentication system that uses audio file analysis to generate and retrieve secure passwords. 

- The system extracts stable features from audio files, uses AI to generate strong passwords based on these features, and securely stores encrypted credentials for later authentication.

## **Project Overview**

Sound-to-Security offers a unique alternative to traditional password systems and biometric authentication, providing:

- Strong security without requiring users to memorise complex passwords
- Privacy protection by avoiding the storage of biological identifiers
- Revocability through the ability to change audio files

The system is particularly suited for high-security environments where authentication frequency is limited and security requirements are paramount.

### Demo Video

- https://www.youtube.com/watch?v=jI0g66XIJP0&ab_channel=CormacGeraghty

### Dissertation
The full dissertation PDF is available in the root of this repository: G00409920_FYP_Dissertation.pdf

## **Repository Structure** 

The repository is organised into the following main directories:

### **PasswordGenerator**

Core authentication system components including:

- audio_feature_extraction.py - Extracts stable features from audio files
- hash_password_generator.py - Creates cryptographic hashes from audio features
- ai_password_generator.py - Generates secure passwords using OpenAI's GPT models
- symmetric_key_generation.py - Derives cryptographic keys for encryption/decryption
- encrypt_decrypt_password.py - Handles encryption and decryption of passwords
- database_control.py - Manages SQLite database operations
- ui.py - Graphical user interface for the system

### **AI_Training**

Specialised components for fine-tuning and security evaluation:

- convert_to_jsonl.py - Prepares data for AI fine-tuning
- ai_fine_tune.py - Creates fine-tuned models for security testing
- check_status.py - Monitors fine-tuning job status
- test_fine_tuned_model.py - Evaluates model performance for security assessment

### **PasswordAnalysis**

Analysis tools for security and performance evaluation:

- audio_feature_correlations.py - Analyses relationships between audio features and passwords
- brute_force_analysis.py - Tests password resistance to various attack strategies
- comparative_analysis.py - Compares with traditional authentication methods
- execution_time_analysis.py - Measures performance across system components
- password_strength_analysis.py - Evaluates entropy and structural security
- password_analysis_utils.py - Shared utilities for analysis scripts

## **Installation Prerequisites**

- Python 3.10 or higher
- Oracle VirtualBox with Ubuntu (recommended for consistent environment)
- OpenAI API key (for password generation and fine-tuning)

## **Setup Instructions**

Clone the repository:

- git clone https://github.com/JamesDoonan1/sound-to-security.git
- cd sound-to-security

Create and activate a virtual environment:

- python3 -m venv myenv
- source myenv/bin/activate  # On Windows: myenv\Scripts\activate

Install dependencies:

- pip install -r requirements.txt

Create a .env file in the root directory with your OpenAI API key:

- OPENAI_API_KEY=your_api_key_here

Initialise the SQLite database:

- python PasswordGenerator/database_control.py

Create a shared folder for audio files:

- Create a directory to store your audio files
- If using VirtualBox, set up a shared folder between host and VM



## **Usage**

### Running the Application

Start the graphical user interface:

- python PasswordGenerator/ui.py

### Using the interface:

- Create Account: Enter a username and select an audio file. The system will generate a secure password and store it.
- Login: Enter your username and select the same audio file used during account creation.
- Test Security: Evaluate the system's resistance to password prediction attacks.

### Running Analysis Tools

Each analysis script can be run independently to evaluate different aspects of the system:

From the PasswordAnalysis directory:

- python analysis_runner.py - Runs all analysis scripts
- python brute_force_analysis.py - Runs only brute force testing
- python audio_feature_correlations.py - Analyses feature correlations
- Running AI Fine-Tuning for Security Testing

### To test the system against AI-based attacks:

Convert your audio data to JSONL format:

- python AI_Training/convert_to_jsonl.py

Initiate the fine-tuning job:

- python AI_Training/ai_fine_tune.py

Check the status of your fine-tuning job:

- python AI_Training/check_status.py

Test the system against the fine-tuned model:

- python AI_Training/test_fine_tuned_model.py

Note: Fine-tuning requires an OpenAI API key with sufficient credits. The system uses carefully worded prompts to avoid OpenAI's content moderation filters.

## Security Testing

The system includes comprehensive security testing capabilities:

- Brute Force Analysis: Simulates different attack strategies (random, smart, pattern-based)
- Entropy Analysis: Calculates password strength based on information theory
- AI-Based Attacks: Tests resistance to machine learning prediction attempts
- Pattern Analysis: Identifies potential structural vulnerabilities in generated passwords

## Performance Considerations

- Audio feature extraction is computationally intensive, accounting for approximately 90% of processing time
- Average processing time is 30-35 seconds per audio file
- System achieves approximately 7.26x real-time processing (processes audio faster than its playback length)

## References
For academic citations, testing methodology, and ethical frameworks, see the full dissertation.

## Contributors

Cormac Geraghty - Audio File based password generator system 
James Doonan - Voice-based system
