import os
import json
import random
import time
import datetime
import io
import getpass
import csv

# Imports are already correct at the top.
# The previous edit pasted code into the global scope.
# This replacement effectively removes the broken lines 7-21.
try:
    import pyotp
    import qrcode
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Standard libraries not found. Attempting to use local pure-python fallbacks...")
    try:
        from libs import pure_otp as pyotp
        from libs.pure_fernet import Fernet
        qrcode = None # Optional for Termux
        print("Success: Using local pure-python libraries (Portable Mode).")
    except ImportError as e:
        print(f"Error: Missing dependency {e}. Please run 'pip install -r requirements.txt'")
        exit(1)


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

class Utils:
    @staticmethod
    def get_secure_input(prompt_text):
        return getpass.getpass(prompt_text)

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

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
        return True

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as k:
            k.write(key)
        self.fernet = Fernet(key)

class App:
    def __init__(self):
        self.cm = ConfigManager()
        self.is_setup = self.cm.load()

    def run_railfence_challenge(self):
        print("\n--- SECURITY CHALLENGE ---")
        challenge_text = SentenceGenerator.generate()
        # Ensure it's long enough or pad if needed, but generator is usually fine
        # Rail Fence with depth 4 needs enough chars to make sense
        
        encrypted = RailFence.encrypt(challenge_text, depth=4)
        print(f"Decrypt this Ciphertext")
        print(f"[{encrypted}]")
        
        user_input = input("Enter the decrypted Plaintext (This acts as your dynamic key): ").strip()
        
        # Verify
        if user_input == challenge_text:
            print("Challenge Passed.")
            return True
        else:
            # Maybe user made a typo? Let's try matching standardized strings
            if user_input.lower().replace(" ", "") == challenge_text.lower().replace(" ", ""):
                 print("Challenge Passed (loose match).")
                 return True
                 
            print("Challenge FAILED.")
            print(f"Expected: {challenge_text}")
            return False

    def verify_otp(self):
        secret = self.cm.config.get("otp_secret")
        if not secret:
            print("Error: OTP secret not found in config.")
            print("Hint: If running on a new device, ensure you have copied 'pm_config.json' from the original device.")
            return False
            
        totp = pyotp.TOTP(secret)
        user_code = input("Enter OTP from Authenticator: ")
        if totp.verify(user_code, valid_window=1):
            print("OTP Verified.")
            return True
        else:
            print("Invalid OTP.")
            return False

    def initial_setup(self):
        Utils.clear_screen()
        print("=== INITIAL SETUP ===")
        
        # 1. Setup Authenticator
        print("\n[1] Authenticator Setup")
        print("!!! IMPORTANT: A NEW Key is generated every time you run this setup. !!!")
        print("!!! You MUST add this NEW key to your App. Old entries will NOT work. !!!")
        
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR Code
        uri = totp.provisioning_uri(name=getpass.getuser(), issuer_name="PasswordManager")
        
        print("\nScan this QR Code in your Microsoft Authenticator App:")
        if qrcode:
            qr = qrcode.QRCode()
            qr.add_data(uri)
            qr.make(fit=True)
            f = io.StringIO()
            qr.print_ascii(out=f, invert=True)
            f.seek(0)
            print(f.read())
        else:
             print("[QR Code library missing. Please enter secret manually]")
        
        print(f"Or enter manually: Secret Key: {secret}")
        input("Press Enter after you have added this NEW account to your Authenticator app...")
        
        # Verify immediately
        print("Let's verify your authenticator setup.")
        print(f"Current PC Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        totp = pyotp.TOTP(secret)
        current_otp = totp.now()
        
    #    print(f"DEBUG/SYNC CHECK: The PC expects the code: [ {current_otp} ]")
        print("Check your phone. If it matches, great! If it's different, your PC clock is likely out of sync.")
        print("You can enter the code from your phone OR the code shown above to verify.")
        
        while True:
            code = input("Enter the code: ").strip()
            
            # valid_window=8 allows for +/- 4 minutes of drift
            if totp.verify(code, valid_window=8):
                print("Authenticator verified successfully!")
                break
            elif code == current_otp:
                 print("Authenticator verified (Manual Sync Match)!")
                 break
            else:
                print(f"Invalid code. Expected close to {current_otp}. Please try again.")

        # 2. Storage Location
        print("\n[2] Storage Setup")
        default_path = "credentials.dat"
        storage_path = input(f"Enter path to save encrypted passwords [default: {default_path}]: ").strip()
        if not storage_path:
            storage_path = default_path
            
        # 3. Rail Fence Challenge
        print("\n[3] Rail Fence Challenge Test")
        print("To verify you understand the challenge logic...")
        if not self.run_railfence_challenge():
            print("You failed the initial challenge. Setup aborted.")
            return

        # Save configuration
        self.cm.generate_key()
        self.cm.config = {
            "otp_secret": secret,
            "data_path": storage_path,
            "setup_complete": True
        }
        self.cm.save()
        
        # Initialize empty data file
        self.save_credentials({})
        
        print("\nSetup Complete!")
        time.sleep(2)
        self.is_setup = True

    def get_credentials(self):
        path = self.cm.config.get("data_path")
        if not os.path.exists(path):
            return {}
        
        with open(path, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cm.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception as e:
            print("Error decrypting data file:", e)
            return {}

    def save_credentials(self, data):
        path = self.cm.config.get("data_path")
        json_data = json.dumps(data)
        encrypted_data = self.cm.fernet.encrypt(json_data.encode())
        with open(path, 'wb') as f:
            f.write(encrypted_data)

    def add_credential(self):
        if not self.verify_otp(): # Standard says "encryption" but let's secure write access
             return
             
        creds = self.get_credentials()
        username = input("Enter Username/Service Name: ")
        password = getpass.getpass("Enter Password: ")
        
        if username in creds:
             if input("Credential exists. Overwrite? (y/n): ").lower() != 'y':
                 return
        
        creds[username] = password
        self.save_credentials(creds)
        print("Credential saved.")

    def update_authenticator(self):
        print("Requesting Rail Fence Challenge verification before change...")
        if not self.run_railfence_challenge():
            return
            
        print("Warning: This will invalidate your old OTP codes.")
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR Code
        uri = totp.provisioning_uri(name=getpass.getuser(), issuer_name="PasswordManager")
        
        print("\nScan this QR Code in your Microsoft Authenticator App:")
        if qrcode:
            qr = qrcode.QRCode()
            qr.add_data(uri)
            qr.make(fit=True)
            f = io.StringIO()
            qr.print_ascii(out=f, invert=True)
            f.seek(0)
            print(f.read())
        else:
            print("[QR Code library missing. Please enter secret manually]")
        
        print(f"Or enter manually: Secret Key: {secret}")
        input("Press Enter after adding to Microsoft Authenticator...")
        
        totp = pyotp.TOTP(secret)
        if totp.verify(input("Verify new code: "), valid_window=1):
            self.cm.config["otp_secret"] = secret
            self.cm.save()
            print("Authenticator updated.")
        else:
            print("Verification failed. No changes made.")

    def update_credentials(self):
        print("Verify Identity to Edit Credentials...")
        if not self.verify_otp():
            return
            
        self.add_credential() # Reuse logic

    def update_path_location(self):
        if not self.run_railfence_challenge():
            return
            
        current_data = self.get_credentials()
        new_path = input("Enter new path location: ")
        
        # Save to new location
        self.cm.config["data_path"] = new_path
        self.cm.save()
        self.save_credentials(current_data)
        print(f"Data moved to {new_path}")

    def get_password(self):
        search_query = input("Enter username or service to search: ")
        
        # 1. First Challenge
        if not self.run_railfence_challenge():
            return
            
        # 2. Second Challenge (OTP)
        if not self.verify_otp():
            return
            
        creds = self.get_credentials()
        found = False
        for k, v in creds.items():
            if search_query.lower() in k.lower():
                print(f"Found: {k} -> {v}") # In real app, maybe copy to clipboard
                found = True
        
        if not found:
            print("No matching credentials found.")

    def bulk_import(self):
        print("Verify Identity to Import Credentials...")
        if not self.verify_otp():
            return

        default_csv = "credentials_import.csv"
        csv_path = input(f"Enter path to CSV file [default: {default_csv}]: ").strip()
        if not csv_path:
            csv_path = default_csv
            
        if not os.path.exists(csv_path):
             print("Error: File not found.")
             return
             
        try:
            current_creds = self.get_credentials()
            count = 0
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Handle case where file might not have headers or different headers
                # We expect "Service,Password" based on the task
                
                # Check fieldnames if possible, fallback to assuming row content
                if not reader.fieldnames:
                     print("Error: CSV appears empty or malformed.")
                     return
                     
                for row in reader:
                    # Try to find key/value from likely column names
                    key = row.get("Service") or row.get("Username") or row.get("Key")
                    value = row.get("Password") or row.get("Value")
                    
                    if not key or not value:
                        # Fallback for simple headerless read if DictReader fails? 
                        # But we wrote the CSV with headers "Service,Password" so it should work.
                        continue
                        
                    current_creds[key] = value
                    count += 1
            
            self.save_credentials(current_creds)
            print(f"Successfully imported {count} credentials.")
            
        except Exception as e:
            print(f"Error importing CSV: {e}")

    def list_usernames(self):
        print("Verify Identity to List Services...")
        # Since listing usernames is less sensitive than passwords, 
        # but still private, we should at least check they have access.
        # User said "show usernames only if user want to show" implying a toggle or action.
        if not self.verify_otp():
            return
            
             
        creds = self.get_credentials()    
        if not creds:
             print("No credentials stored.")
             return
             
        sorted_keys = sorted(creds.keys())
        print("\n=== Stored Services / Usernames ===")
        for i, service in enumerate(sorted_keys, 1):
            print(f"{i}. {service}")
        print("===================================")
        
        choice = input("\nEnter tag number to reveal password (or 0/Enter to go back): ").strip()
        if not choice or choice == '0':
            return
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sorted_keys):
                selected_service = sorted_keys[idx]
                
                # Security Check before revealing password
                # They already passed OTP to see the list via verify_otp() above.
                # Let's verify Knowledge (Rail Fence) now to match get_password security level.
                if not self.run_railfence_challenge():
                    return
                
                print(f"\nServiceName: {selected_service}")
                print(f"Password:    {creds[selected_service]}")
                input("\nPress Enter to clear screen and continue...")
                Utils.clear_screen()
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input.")

    def export_csv(self):
        print("Verify Identity to Export Credentials...")
        if not self.verify_otp():
            return
            
        default_path = "exported_credentials.csv"
        path = input(f"Enter path to save CSV [default: {default_path}]: ").strip()
        if not path:
            path = default_path
            
        creds = self.get_credentials()
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Service", "Password"])
                for service, password in creds.items():
                    writer.writerow([service, password])
            print(f"Successfully exported {len(creds)} credentials to {path}")
        except Exception as e:
             print(f"Error exporting CSV: {e}")

    def remove_credential(self):
        print("Verify Identity to Remove Credentials...")
        if not self.verify_otp():
            return
            
        print("\n=== REMOVE OPTIONS ===")
        print("1. Remove Single Credential")
        print("2. Remove ALL Credentials")
        
        choice = input("Select Option: ").strip()
        
        creds = self.get_credentials()
        
        if choice == '1':
            if not creds:
                print("No credentials to remove.")
                return
                
            sorted_keys = sorted(creds.keys())
            print("\n=== Select Service to Remove ===")
            for i, service in enumerate(sorted_keys, 1):
                print(f"{i}. {service}")
            
            sel = input("\nEnter tag number (or 0 to cancel): ").strip()
            if not sel or sel == '0':
                 return
                 
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(sorted_keys):
                    target = sorted_keys[idx]
                    if input(f"Are you sure you want to delete '{target}'? (type 'yes' to confirm): ").lower() == 'yes':
                        del creds[target]
                        self.save_credentials(creds)
                        print("Credential removed.")
                    else:
                        print("Cancelled.")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Invalid input.")
                
        elif choice == '2':
            print("\n!!! DANGER: THIS WILL WIPE ALL SAVED CREDENTIALS !!!")
            # Require higher security verification for this destructive action
            if not self.run_railfence_challenge():
                print("Verification failed. Aborting wipe.")
                return
                
            confirm = input("Type 'DELETE ALL' to confirm: ")
            if confirm == 'DELETE ALL':
                 self.save_credentials({})
                 print("All credentials have been wiped.")
            else:
                 print("Incorrect confirmation string. Aborted.")
        else:
            print("Invalid option.")

    def main_menu(self):
        while True:
            Utils.clear_screen()
            print("=== PASSWORD MANAGER MAIN MENU ===")
            print("1. Manage Credentials (Add / Update / Remove)")
            print("2. Retrieve Credentials (Get Password / List All)")
            print("3. Data Management (Import / Export)")
            print("4. Settings & Setup")
            print("5. Cloud Sync (Git)")
            print("q. Quit")
            
            choice = input("\nSelect Option: ").lower()
            
            if choice == '1':
                while True:
                    Utils.clear_screen()
                    print("=== MANAGE CREDENTIALS ===")
                    print("a. Add New Credential")
                    print("b. Update Existing Credential")
                    print("c. Remove Credential")
                    print("d. Back to Main Menu")
                    
                    sub = input("\nSelect Option: ").lower()
                    if sub == 'a': self.add_credential()
                    elif sub == 'b': self.update_credentials()
                    elif sub == 'c': self.remove_credential()
                    elif sub == 'd' or sub == 'back': break
                    else: break 
                    input("Press Enter to continue...")

            elif choice == '2':
                 while True:
                    Utils.clear_screen()
                    print("=== RETRIEVE CREDENTIALS ===")
                    print("a. Get Password (Search by Name)")
                    print("b. List All Services (Interactive)")
                    print("c. Back to Main Menu")
                    
                    sub = input("\nSelect Option: ").lower()
                    if sub == 'a': self.get_password()
                    elif sub == 'b': self.list_usernames()
                    elif sub == 'c': break
                    else: break
                    input("Press Enter to continue...")

            elif choice == '3':
                while True:
                    Utils.clear_screen()
                    print("=== DATA MANAGEMENT ===")
                    print("a. Bulk Import (from CSV)")
                    print("b. Export to CSV")
                    print("c. Back to Main Menu")
                    
                    sub = input("\nSelect Option: ").lower()
                    if sub == 'a': self.bulk_import()
                    elif sub == 'b': self.export_csv()
                    elif sub == 'c': break
                    else: break
                    input("Press Enter to continue...")

            elif choice == '4':
                while True:
                    Utils.clear_screen()
                    print("=== SETTINGS & SETUP ===")
                    print("a. New Initial Setup")
                    print("b. Update Authenticator")
                    print("c. Update Storage Path")
                    print("d. Back to Main Menu")
                    
                    sub = input("\nSelect Option: ").lower()
                    if sub == 'a':
                         if input("This will wipe existing config. Continue? (y/n): ") == 'y':
                            self.initial_setup()
                    elif sub == 'b': self.update_authenticator()
                    elif sub == 'c': self.update_path_location()
                    elif sub == 'd': break
                    else: break
                    input("Press Enter to continue...")
            
            elif choice == '5':
                print("Select Mode:")
                print("1. Push (Upload Local Changes)")
                print("2. Pull (Download Cloud Changes)")
                syn = input("Choice: ")
                if syn == '1': GitSync.push_data()
                elif syn == '2': GitSync.pull_data()
            
            elif choice == 'q':
                break
            else:
                input("Invalid option. Press Enter to continue...")
                continue

    def start(self):
        # User requested to remove automatic setup.
        # It is now accessible via the Main Menu (Option a).
        self.main_menu()

if __name__ == "__main__":
    app = App()
    app.start()
