from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def generate_candidate_password(features, model_id):
    prompt = """
Based on these summarized audio characteristics:
- MFCC mean: {}
- Spectral Centroid mean: {}
- Spectral Contrast mean: {}
- Tempo mean: {}
- Beats mean: {}
- Harmonic Components mean: {}
- Percussive Components mean: {}
- Zero-Crossing Rate mean: {}
- Chroma Features (CENS) mean: {}
Generate a secure access code. The access code should be a strong password, not None.
""".format(
    features.get("MFCCs_mean", "N/A"),
    features.get("Spectral_Centroid_mean", "N/A"),
    features.get("Spectral_Contrast_mean", "N/A"),
    features.get("Tempo_mean", "N/A"),
    features.get("Beats_mean", "N/A"),
    features.get("Harmonic_Components_mean", "N/A"),
    features.get("Percussive_Components_mean", "N/A"),
    features.get("Zero_Crossing_Rate_mean", "N/A"),
    features.get("Chroma_Features_CENS_mean", "N/A")
    )
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=0.9
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    test_features = {
        "MFCCs_mean": "9.409542083740234",
        "Spectral_Centroid_mean": "3516.9284224113326",
        "Spectral_Contrast_mean": "21.479570879381892",
        "Tempo_mean": "95.33898305084746",
        "Beats_mean": "9222.079872204473",
        "Harmonic_Components_mean": "5.636732566927094e-06",
        "Percussive_Components_mean": "-1.56643072841689e-05",
        "Zero_Crossing_Rate_mean": "0.08029233969473108",
        "Chroma_Features_CENS_mean": "0.2650798559188843"
    }
    model_id = "ft:gpt-4o-2024-08-06:personal::BM4R6u51"
    print(generate_candidate_password(test_features, model_id))