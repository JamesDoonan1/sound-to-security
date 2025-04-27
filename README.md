# From Sound to Security: AI-Powered Voice-Based Password Generation

**Author:** James Doonan  
**Institution:** Atlantic Technological University (ATU), Galway  
**Dissertation Type:** Minor Dissertation (B.Sc. (Hons) in Software Development)  
**Repository:** [JamesDoonan1/sound-to-security](https://github.com/JamesDoonan1/sound-to-security)  
**Branch for this project:** [`feature/vocal-passwords-new`](https://github.com/JamesDoonan1/sound-to-security/tree/feature/vocal-passwords-new)

---

## Project Overview

This project explores a novel approach to password authentication by leveraging voice biometrics and AI to generate secure passwords. Using vocal inputs such as speech or humming, the system extracts acoustic features and feeds them to an AI model (Claude AI) to generate high-entropy passwords that are both secure and tied to the user's voice characteristics. These AI-generated passwords are systematically compared against traditional user-created passwords in terms of entropy, complexity, and memorability. All passwords are then rigorously tested against brute-force, dictionary, and AI-based attacks to assess and compare their relative security strength, demonstrating how the AI-vocal approach offers significant advantages over conventional password creation methods.   

### Demo Video  
https://youtu.be/EU1PWU_Si1w

### Dissertation
The full dissertation PDF is available in the root of this repository: G00310428_FYP_Dissertation.pdf

---

## Project Structure

```
sound-to-security/
├── backend/                # Flask routes and service logic
│   ├── routes/             # API endpoints for voice and password
│   └── services/           # Password cracking and AI integration logic
├── frontend/               # GUI application
├── models/                 # Claude integration and voice recognition
├── vocal_passwords/        # Feature extraction and authentication logic
├── app.py                  # Flask app entry point
└── main.py                 # App launcher
```

---

## Features

- Voice Feature Extraction using MFCCs, Spectral Centroid, and Tempo via Librosa  
- Speech-to-Text passphrase recognition (Google STT API)  
- Password Generation with Claude AI based on extracted features  
- Security Testing:
  - Brute-force attack simulation  
  - Dictionary-based attacks (RockYou dataset)  
  - GPT-4 cracking attempts  
  - Hashcat integration  
- Voiceprint Authentication using feature similarity  
- Graphical User Interface for full user interaction  
- Test Coverage and Analysis (entropy, crack time, test logs)  
- Ethical AI Security Analysis and privacy risk evaluation  

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JamesDoonan1/sound-to-security.git
   cd sound-to-security
   git checkout feature/vocal-passwords-new
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure your API keys (for Claude and GPT-4) in `.env`.

4. Running the application (requires two terminal windows):
   
   Terminal 1 - Start the backend server:
   ```bash
   cd backend
   python app.py
   ```
   
   Terminal 2 - Start the GUI (from project root):
   ```bash
   python main.py
   ```

---

## Testing

- Run unit tests:
  ```bash
  pytest
  ```

- Test coverage:
  Included in Appendix B of the dissertation, covering:
  - Audio recording and feature extraction  
  - Password generation and validation  
  - Cracking method simulations  
  - GUI integration  

---

## Results Summary

| Attack Method | Success Rate | Avg. Crack Time | Notes |
|---------------|--------------|------------------|-------|
| Brute Force   | Less than 5% | ~5–12 seconds    | Limited by entropy |
| Claude    | 0%           | N/A              | Refused to guess password for ethical reasons |
| GPT-4         | 0/5 guesses  | Under 2s per guess | No successful match |
| Hashcat       | 0%           | Timed out        | Tested against multiple modes |

None of the AI-generated passwords were cracked in any scenario.

Passwords showed 41.52–43.02 bits of entropy — significantly stronger than traditional user-generated examples.

---

## AI and Ethical Considerations

This project includes a critical evaluation of the ethical implications of AI in both generating and cracking passwords:

- Risk of misuse of AI for password cracking  
- Privacy concerns related to storing voice data  
- Importance of secure handling of biometric inputs  

---

## References

For academic citations, testing methodology, and ethical frameworks, see the full dissertation or Appendix B (Test Documentation).

---

## Contributors

- James Doonan (Voice-based system, AI integration, GUI)  
- Cormac Geraghty (Audio-based password generator system)  

---

## Appendix

For full code listings, testing scripts, and detailed output logs, see:

- Appendix A — Code Listings  
- Appendix B — Test Documentation (unit tests, cracking logs, coverage)
- Appendix C - GitHub and Video Demonstration URL

---

