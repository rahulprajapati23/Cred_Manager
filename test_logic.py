import sys
import os

# Add current directory to path so we can import main
sys.path.append(os.getcwd())

from main import RailFence, SentenceGenerator

def test_railfence():
    print("Testing Rail Fence Cipher...")
    plain = "The quick brown fox jumps over the lazy dog"
    cipher = RailFence.encrypt(plain, depth=4)
    decrypted = RailFence.decrypt(cipher, depth=4)
    
    print(f"Original:  {plain}")
    print(f"Encrypted: {cipher}")
    print(f"Decrypted: {decrypted}")
    
    if plain == decrypted:
        print("[PASS] Decryption matches original.")
    else:
        print("[FAIL] Decryption mismatch!")
        exit(1)

def test_sentence_gen():
    print("\nTesting Sentence Generator...")
    sent = SentenceGenerator.generate()
    print(f"Generated: {sent}")
    if len(sent.split()) >= 3:
        print("[PASS] Sentence looks valid.")
    else:
        print("[FAIL] Sentence too short.")
        exit(1)

if __name__ == "__main__":
    test_railfence()
    test_sentence_gen()
