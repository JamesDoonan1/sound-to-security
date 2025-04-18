import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  #
    messages=[
        {"role": "system", "content": "You are a helpful assistant that generates secure passwords."},
        {"role": "user", "content": "Generate a secure 12-character password with symbols and numbers."}
    ]
)

# Extract and print the response
password = response['choices'][0]['message']['content'].strip()
print(f"Generated Password: {password}")