import threading
import time
import itertools
import string

class TimeoutException(Exception):
    pass

def brute_force_worker(target_password, max_length, characters, result):
    """
    Worker function for brute force cracking, runs in a separate thread.
    """
    start_time = time.time()
    for length in range(1, max_length + 1):
        for guess in itertools.product(characters, repeat=length):
            guess = ''.join(guess)
            if guess == target_password:
                end_time = time.time()
                result["cracked"] = True
                result["guess"] = guess
                result["time_taken"] = end_time - start_time
                return
    result["cracked"] = False
    result["message"] = "Password not cracked within limits"

def brute_force_crack(target_password, max_length=12, timeout=30):  # Timeout in seconds
    """
    Simulate brute force password cracking with a timeout.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    result = {"cracked": False, "message": "Timeout occurred"}
    
    # Create and start the thread
    thread = threading.Thread(target=brute_force_worker, args=(target_password, max_length, characters, result))
    thread.start()
    
    # Wait for the thread to finish or timeout
    thread.join(timeout)
    
    # If the thread is still alive after timeout, return timeout message
    if thread.is_alive():
        return {"cracked": False, "message": "Brute force timed out"}
    return result

def dictionary_attack(target_password, dictionary_file="common_passwords.txt"):
    """
    Simulate dictionary attack using a file of common passwords.
    """
    print(f"Attempting dictionary attack: {target_password}")
    start_time = time.time()
    try:
        with open(dictionary_file, "r") as f:
            for line in f:
                guess = line.strip()
                if guess == target_password:
                    end_time = time.time()
                    print(f"Password cracked: {guess}")
                    return {"cracked": True, "guess": guess, "time_taken": end_time - start_time}
    except FileNotFoundError:
        return {"cracked": False, "message": "Dictionary file not found"}
    
    return {"cracked": False, "message": "Password not found in dictionary"}
