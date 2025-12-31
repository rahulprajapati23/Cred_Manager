import streamlit as st
import os
import json
import time
from libs import core

# Page Config (Mobile Friendly)
st.set_page_config(page_title="Brahmos Pass", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for Mobile Feel
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core
if 'cm' not in st.session_state:
    st.session_state.cm = core.ConfigManager()
    st.session_state.is_setup = st.session_state.cm.load()

# Session State for Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'decrypted_creds' not in st.session_state:
    st.session_state.decrypted_creds = {}

def login():
    st.title("🔒 Login")
    
    if not st.session_state.is_setup:
        st.warning("Setup Required. Please run 'python main.py' in CLI to set up encryption keys first.")
        return

    st.write("Enter Authenticator Code")
    code = st.text_input("OTP Code", type="password", help="Check your Microsoft Authenticator")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Unlock"):
            secret = st.session_state.cm.config.get("otp_secret")
            try:
                import pyotp
            except ImportError:
                from libs import pure_otp as pyotp
                
            totp = pyotp.TOTP(secret)
            if totp.verify(code, valid_window=1):
                st.session_state.logged_in = True
                st.success("Unlocked with Biometrics/OTP")
                st.rerun()
            else:
                st.error("Invalid Code")
    
    with col2:
        if st.button("Sync (Pull)"):
            with st.status("Syncing..."):
                core.GitSync.pull_data()
                st.success("Synced")

def get_credentials():
    path = st.session_state.cm.config.get("data_path")
    if not os.path.exists(path):
        # Fallback check
        local = os.path.basename(path)
        if os.path.exists(local): path = local
        else: return {}
        
    with open(path, 'rb') as f:
        encrypted_data = f.read()
    try:
        decrypted = st.session_state.cm.fernet.decrypt(encrypted_data)
        return json.loads(decrypted)
    except Exception:
        return {}

def save_credentials(data):
    path = st.session_state.cm.config.get("data_path")
    # Basic path safety/fallback for verification could be added here
    json_data = json.dumps(data)
    encrypted = st.session_state.cm.fernet.encrypt(json_data.encode())
    with open(path, 'wb') as f:
        f.write(encrypted)

def main_app():
    st.title("🔑 Brahmos Manager")
    
    # Reload creds
    creds = get_credentials()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Search", "Add New", "Settings"])
    
    with tab1:
        search_term = st.text_input("🔎 Search Services")
        
        filtered = {k:v for k,v in creds.items() if search_term.lower() in k.lower()} if search_term else creds
        
        if not filtered:
            st.info("No credentials found.")
        
        for service, password in filtered.items():
            with st.expander(f"🔐 {service}"):
                # Security Challenge before show? 
                # On mobile app, usually biometric or just show. 
                # Let's add a "Reveal" tolerance or button.
                
                if st.checkbox(f"Reveal Password for {service}", key=f"rev_{service}"):
                    st.code(password, language=None)
                else:
                    st.text("••••••••")
                
                if st.button("Copy", key=f"cpy_{service}"):
                    st.toast(f"Password for {service} copied! (Simulated)")
                    # Streamlit can't write to client clipboard easily without components
                    # but we can show it in a copyable text area
    
    with tab2:
        st.subheader("Add Credential")
        new_svc = st.text_input("Service Name")
        new_pass = st.text_input("Password", type="password")
        
        if st.button("Save Credential"):
            if new_svc and new_pass:
                creds[new_svc] = new_pass
                save_credentials(creds)
                st.success(f"Saved {new_svc}")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Fields cannot be empty")
                
    with tab3:
        st.subheader("Cloud Sync")
        if st.button("☁️ Push Changes to Git"):
            with st.spinner("Pushing..."):
                core.GitSync.push_data()
            st.success("Data Pushed to Cloud")
            
        if st.button("☁️ Pull Changes from Git"):
            with st.spinner("Pulling..."):
                core.GitSync.pull_data()
            st.success("Data Pulled from Cloud")
            
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    if st.session_state.logged_in:
        main_app()
    else:
        login()
