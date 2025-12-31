import pyotp
import time

def test_otp_generation():
    print("Testing OTP Generation...")
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    now_code = totp.now()
    print(f"Secret: {secret}")
    print(f"Generated Code: {now_code}")
    
    print("Verifying immediate code...")
    if totp.verify(now_code):
        print("[PASS] Verified successfully.")
    else:
        print("[FAIL] Immediate verification failed.")

if __name__ == "__main__":
    test_otp_generation()
