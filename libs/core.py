import os
import json
import random
import datetime
import getpass
from . import pure_fernet
from . import pure_otp

# Try standard imports, fallback to locals is handled by the importer of this module usually, 
# but core.py needs to be robust. 
# Actually, since we are in 'libs', we should check if we can import from standard 
# or if we should use the sibling modules.
# For simplicity, we assume the environment is set up (standard or local).
# But wait, main.py did the patching.
# We will replicate the import logic here to be safe, or assume main.py patches it? 
# Better to be explicit:

try:
    import pyotp
    import qrcode
    from cryptography.fernet import Fernet
except ImportError:
    from . import pure_otp as pyotp
    from . import pure_fernet as Fernet
    qrcode = None

class GitSync:
    @staticmethod
    def push_data():
        print("Syncing: Uploading changes to Cloud (Git)...")
        try:
            # Stage everything
            os.system("git add .")
            # Commit
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            os.system(f'git commit -m "Auto-Sync: {timestamp}"')
            # Push
            if os.system("git push") == 0:
                print("Success: Data uploaded.")
            else:
                print("Error: Push failed. Check your internet or git config.")
        except Exception as e:
            print(f"Sync Error: {e}")

    @staticmethod
    def pull_data():
        print("Syncing: Downloading changes from Cloud (Git)...")
        try:
            if os.system("git pull") == 0:
                print("Success: Data updated.")
            else:
                print("Error: Pull failed.")
        except Exception as e:
            print(f"Sync Error: {e}")

class RailFence:
    @staticmethod
    def encrypt(text, depth=4):
        rail = [['\n' for i in range(len(text))]
                for j in range(depth)]
        
        dir_down = False
        row, col = 0, 0
        
        for i in range(len(text)):
            if (row == 0) or (row == depth - 1):
                dir_down = not dir_down
            
            rail[row][col] = text[i]
            col += 1
            
            if dir_down:
                row += 1
            else:
                row -= 1
                
        result = []
        for i in range(depth):
            for j in range(len(text)):
                if rail[i][j] != '\n':
                    result.append(rail[i][j])
        return("" . join(result))

    @staticmethod
    def decrypt(cipher, depth=4):
        rail = [['\n' for i in range(len(cipher))]
                for j in range(depth)]
        
        dir_down = None
        row, col = 0, 0
        
        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == depth - 1:
                dir_down = False
            
            rail[row][col] = '*'
            col += 1
            
            if dir_down:
                row += 1
            else:
                row -= 1
                
        index = 0
        for i in range(depth):
            for j in range(len(cipher)):
                if ((rail[i][j] == '*') and
                   (index < len(cipher))):
                    rail[i][j] = cipher[index]
                    index += 1
                    
        result = []
        row, col = 0, 0
        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == depth - 1:
                dir_down = False
                
            if rail[row][col] != '*':
                result.append(rail[row][col])
                col += 1
                
            if dir_down:
                row += 1
            else:
                row -= 1
        return("".join(result))

class SentenceGenerator:
    @staticmethod
    def generate():
        subjects = ["The cat", "The dog", "A bird", "The main system", "My server", "The hacker", "A robot"]
        verbs = ["jumps over", "runs inside", "encrypts", "hacks", "calculates", "secures", "defends"]
        objects = ["the lazy fox", "the database", "the firewall", "the quantum computer", "the password", "the key"]
        
        return f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}"

class ConfigManager:
    def __init__(self, config_path="pm_config.json", key_path="key.key"):
        self.config_path = config_path
        self.key_path = key_path
        self.config = {}
        self.fernet = None

    def load(self):
        if not os.path.exists(self.config_path):
            return False
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as k:
                key = k.read()
                self.fernet = Fernet(key)
        else:
            # Try finding key in current dir if not found at path
            if os.path.exists("key.key"):
                with open("key.key", 'rb') as k:
                    key = k.read()
                    self.fernet = Fernet(key)
        return True

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as k:
            k.write(key)
        self.fernet = Fernet(key)
