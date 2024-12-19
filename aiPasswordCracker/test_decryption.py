from database_control import get_encrypted_password
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import decrypt_password

# Hardecoded hash obtained from a processed file
test_audio_hash = "be57b3b83719a851fffac1968b22cc73" 

encrypted_pw = get_encrypted_password(test_audio_hash)
if encrypted_pw:
    key = derive_key_from_hash(test_audio_hash)
    password = decrypt_password(encrypted_pw, key)
    print(f"\nDecrypted Password for hash {test_audio_hash}: {password}\n")
else:
    print(f"No password found for hash: {test_audio_hash}")
