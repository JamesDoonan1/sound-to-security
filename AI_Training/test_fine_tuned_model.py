from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Try with more explicit instructions
test_features = """
Based on these summarized audio characteristics:
- MFCC mean: 9.409542083740234
- Spectral Centroid mean: 3516.9284224113326
- Spectral Contrast mean: 21.479570879381892
- Tempo mean: 95.33898305084746
- Beats mean: 9222.079872204473
- Harmonic Components mean: 5.636732566927094e-06
- Percussive Components mean: -1.56643072841689e-05
- Zero-Crossing Rate mean: 0.08029233969473108
- Chroma Features (CENS) mean: 0.2650798559188843
Generate the corresponding identifier and secure access code. The access code should be a strong password, not None.
"""

response = client.chat.completions.create(
    model="ft:gpt-4o-2024-08-06:personal::BM4R6u51",
    messages=[{"role": "user", "content": test_features}]
)

print(response.choices[0].message.content)