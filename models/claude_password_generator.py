import anthropic

# Set your Claude API key
anthropic_api_key = "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"

def generate_password_with_claude(features):
    """Generate a password using Claude AI based on extracted features."""
    print("Step 4: Sending features to Claude for password generation...")
    
    prompt = (
        f"The following are features extracted from a vocal melody: {features}.\n"
        "Generate a secure, unique password based on these features. The password must:\n"
        "- Be 12 characters long\n"
        "- Include uppercase, lowercase, numbers, and symbols\n"
        "- Avoid common dictionary words\n\n"
        "Return only the password with no explanation or additional text."
    )

    try:
        client = anthropic.Client(api_key=anthropic_api_key)

        response = client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
            max_tokens_to_sample=20,
            temperature=0.7
        )
        password = response.completion.strip()
        print(f"  - Generated password from Claude: {password}")
        return password
    except Exception as e:
        print(f"Error with Claude API: {e}")
        return "Error: Could not generate password"
