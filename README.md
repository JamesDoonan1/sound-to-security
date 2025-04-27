# Sound-To-Security
 From Sound to Security: Evaluating Audio-Based Passwords against AI Cracking

## Project Overview
This project explores novel approaches to password authentication by leveraging audio and voice biometrics integrated with AI to generate secure passwords. The system supports two distinct input methods:

1. **Voice-Based System:** Uses vocal inputs such as speech or humming to extract acoustic features, which are then processed by Claude AI to generate high-entropy passwords.

2. **Audio File-Based System:** Processes ambient audio or music files to create structured, deterministic passwords with balanced character distribution.

Both approaches are rigorously tested against brute-force attacks, dictionary attacks, and AI-based cracking attempts, demonstrating significant security advantages over conventional password creation methods.


## Demo Video of Voice-Based Passwords (James Doonan)
https://youtu.be/EU1PWU_Si1w   

## Demo Video of Audio-Based Passwords (Cormac Geraghty)
https://www.youtube.com/watch?v=jI0g66XIJP0&ab_channel=CormacGeraghty

## Demo Video of Final Integration of Both Systems
https://www.youtube.com/watch?v=N_-nwLAFkfE&ab_channel=JamesDoonan

## Project Structure
```
sound-to-security/
├── backend/                # Flask routes and service logic
│   ├── routes/             # API endpoints for voice and password
│   └── services/           # Password cracking and AI integration logic
├── frontend/               # GUI application
├── models/                 # Claude integration and voice recognition
├── vocal_passwords/        # Feature extraction and authentication logic
├── audio_passwords/        # Audio file processing and pattern extraction
├── app.py                  # Flask app entry point
└── main.py                 # App launcher
```

## Features

### Voice-Based System
- Voice Feature Extraction using MFCCs, Spectral Centroid, and Tempo via Librosa
- Speech-to-Text passphrase recognition (Google STT API)
- Password Generation with Claude AI based on extracted features
- Average entropy: 42.52 bits (range: 41.51-43.02)
- Zero pattern detection for enhanced security

### Audio-Based System
- Structured character distribution: 35.4% uppercase, 35.4% lowercase, 15.4% digits, 13.8% symbols
- Deterministic pattern-based implementation
- Entropy measurement ~3.8 bits (vs. dictionary)
- Exceptional brute force resistance (380 days to 13.85T years)
- NIST complexity score: 5.5 (highest baseline)

### Security Testing Framework
- Brute-force attack simulation
- Dictionary-based attacks (RockYou dataset)
- GPT-4 cracking attempts (0% success rate)
- Hashcat integration
- Comprehensive entropy and crack-time analysis

### Authentication
- Voiceprint Authentication using feature similarity
- Audio fingerprinting for audio-based approach
- Multi-modal authentication options

### User Interface
- Graphical User Interface supporting both input methods  
![alt text](<Project Integration.png>)
- Security comparison visualisation
- Test result logging and analysis

## Comparative Analysis
The integrated system leverages the complementary strengths of both approaches:

- **Enhanced Security Profile:** Combines structured character distribution (audio-based) with randomised entropy (voice-based)
- **Flexible Authentication Modalities:** Supports both audio uploads and live voice input
- **Layered Security Model:** Different input types and generation logic create natural resilience through diversity
- **Balanced Defense:** Strong theoretical resistance (audio-based) with proven practical defense against modern threats (voice-based)

## Installation

1. Clone the repository:
```
git clone https://github.com/JamesDoonan1/sound-to-security.git
cd sound-to-security
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure your API keys (for Claude and GPT-4) in `.env`

4. Running the application (requires two terminal windows):

**Terminal 1** - Start the backend server:
```
cd backend
python app.py
```

**Terminal 2** - Start the GUI (from project root):
```
python main.py
```

## Testing
Run unit tests:
```
pytest
```

Note: Most of the comprehensive testing was conducted on individual component branches:

Voice-based system testing: feature/vocal-passwords-new
Audio-based system testing: feature/audio-passwords

## Results Summary

| System | Attack Method | Success Rate | Avg. Crack Time | Notes |
|--------|---------------|--------------|-----------------|-------|
| Voice-Based | Brute Force | 0% | ~7,127s | High entropy resistance |
| Voice-Based | Claude | 0% | N/A | Ethical refusal to crack |
| Voice-Based | GPT-4 | 0/5 guesses | Under 2s per guess | No successful matches |
| Voice-Based | Hashcat | 0% | Timed out | Multiple modes tested |
| Audio-Based | Brute Force | 0% | 380 days to 13.85T years | Exceptional theoretical resistance |
| Audio-Based | Dictionary | 0% | N/A | No matches found |
| Audio-Based | Pattern Analysis | Some vulnerability | N/A | Detectable prefixes in 16% of cases |

Neither system's passwords were successfully cracked in any real-world attack scenario.

## AI and Ethical Considerations
This project includes a critical evaluation of the ethical implications of AI in both generating and cracking passwords:
- Risk of misuse of AI for password cracking
- Privacy concerns related to storing voice and audio data
- Importance of secure handling of biometric inputs
- Ethical boundaries observed in AI models (Claude's refusal to attempt password cracking)

## Contributors
- **James Doonan:** Voice-based system, AI integration, GUI, security testing
- **Cormac Geraghty:** Audio-based password generator system, comparative analysis

## References
For academic citations, testing methodology, and ethical frameworks, see the full dissertation.