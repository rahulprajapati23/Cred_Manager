import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import clipboard
import os
import json
from . import core

class PasswordManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BRAHMOS Password Manager")
        self.root.geometry("600x500")
        
        self.cm = core.ConfigManager()
        self.is_setup = self.cm.load()
        
        if not self.is_setup:
            messagebox.showinfo("Setup Required", "Please run the CLI mode first to perform initial setup.")
            self.root.destroy()
            return

        self.show_login()

    def show_login(self):
        # 1. Clear frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        ttk.Label(frame, text="Security Identity Check", font=("Helvetica", 16)).pack(pady=10)
        
        ttk.Label(frame, text="Enter Authenticator Code:").pack(pady=5)
        self.otp_entry = ttk.Entry(frame)
        self.otp_entry.pack(pady=5)
        self.otp_entry.bind('<Return>', lambda e: self.verify_login())
        
        ttk.Button(frame, text="Verify Identity", command=self.verify_login).pack(pady=20)

    def verify_login(self):
        code = self.otp_entry.get().strip()
        secret = self.cm.config.get("otp_secret")
        
        # Check logic from main.py, but using core libs
        try:
            import pyotp
        except ImportError:
            from . import pure_otp as pyotp

        # The simple verify check
        totp = pyotp.TOTP(secret)
        if totp.verify(code, valid_window=1):
             self.show_main_interface()
        else:
             messagebox.showerror("Access Denied", "Invalid OTP Code.")

    def show_main_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Toolbar
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="Add Credential", command=self.add_credential_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Sync (Push)", command=core.GitSync.push_data).pack(side=tk.RIGHT, padx=5)

        # Treeview
        columns = ("service", "username")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("service", text="Service / Application")
        self.tree.heading("username", text="Username (Hidden)") # We don't store username separately in simple schema, just Key=Service
        
        # In this simple schema, Key IS the service/username combo.
        self.tree = ttk.Treeview(self.root, columns=("key"), show="headings")
        self.tree.heading("key", text="Service Name")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", self.on_item_double_click)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)
        
        self.refresh_list()

    def get_credentials(self):
        # Reusing logic from main.py's get_credentials but through ConfigManager handle?
        # ConfigManager doesn't have get_credentials, it was in App.
        # We need to reimplement or call usage.
        
        path = self.cm.config.get("data_path")
        if not os.path.exists(path):
            # Fallback
            local_name = os.path.basename(path)
            if os.path.exists(local_name):
                 path = local_name
            else:
                 return {}
        
        with open(path, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = self.cm.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except Exception:
            return {}

    def save_credentials(self, data):
        path = self.cm.config.get("data_path")
        # Ensure path uses local simplified name if full path fails check? 
        # For saving, we trust config or default.
        json_data = json.dumps(data)
        encrypted_data = self.cm.fernet.encrypt(json_data.encode())
        with open(path, 'wb') as f:
            f.write(encrypted_data)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        creds = self.get_credentials()
        for key in sorted(creds.keys()):
            self.tree.insert("", tk.END, values=(key,))
        self.status_var.set(f"Loaded {len(creds)} credentials.")

    def add_credential_dialog(self):
        service = simpledialog.askstring("Add Credential", "Enter Service Name:")
        if not service: return
        password = simpledialog.askstring("Add Credential", "Enter Password:", show='*')
        if not password: return
        
        creds = self.get_credentials()
        creds[service] = password
        self.save_credentials(creds)
        self.refresh_list()
        messagebox.showinfo("Success", "Credential Saved.")

    def on_item_double_click(self, event):
        item_id = self.tree.selection()[0]
        service_name = self.tree.item(item_id, "values")[0]
        
        # Security Challenge
        if self.run_railfence_gui():
             creds = self.get_credentials()
             password = creds.get(service_name)
             
             # Show Password Dialog
             self.show_password_dialog(service_name, password)

    def show_password_dialog(self, service, password):
        top = tk.Toplevel(self.root)
        top.title("Password Revealed")
        top.geometry("300x150")
        
        ttk.Label(top, text=f"Service: {service}").pack(pady=10)
        
        entry = ttk.Entry(top)
        entry.insert(0, password)
        entry.pack(pady=5, padx=10, fill=tk.X)
        
        def copy():
            try:
                clipboard.copy(password)
                messagebox.showinfo("Copied", "Password copied to clipboard!")
                top.destroy()
            except:
                messagebox.showerror("Error", "Could not copy to clipboard.")

        ttk.Button(top, text="Copy to Clipboard", command=copy).pack(pady=10)

    def run_railfence_gui(self):
        # A simplified Rail Fence Dialog (Depth 2)
        challenge_text = core.SentenceGenerator.generate()
        encrypted = core.RailFence.encrypt(challenge_text, depth=2)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Security Challenge")
        dialog.geometry("400x300")
        dialog.grab_set() # Modal
        
        ttk.Label(dialog, text="Verify it's you.", font=("Bold", 12)).pack(pady=10)
        ttk.Label(dialog, text="Decrypt this Rail Fence (Depth 2) Cipher:", wraplength=380).pack(pady=5)
        
        msg = tk.Text(dialog, height=3, width=40)
        msg.insert("1.0", encrypted)
        msg.configure(state='disabled')
        msg.pack(pady=5)
        
        ttk.Label(dialog, text="Hint: Read zig-zag (Top-Bottom-Top-Bottom...)").pack()
        
        ans_entry = ttk.Entry(dialog, width=40)
        ans_entry.pack(pady=10)
        ans_entry.focus()
        
        result_container = {"passed": False}
        
        def check():
            user_input = ans_entry.get().strip()
            if user_input.lower().replace(" ", "") == challenge_text.lower().replace(" ", ""):
                result_container["passed"] = True
                dialog.destroy()
            else:
                messagebox.showerror("Failed", f"Incorrect.\nExpected: {challenge_text}")
        
        ttk.Button(dialog, text="Submit", command=check).pack(pady=10)
        
        self.root.wait_window(dialog)
        return result_container["passed"]

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PasswordManagerGUI()
    app.run()
