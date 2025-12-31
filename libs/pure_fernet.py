import base64
import hmac
import time
import os
import struct
import hashlib
from . import aes

class InvalidToken(Exception):
    pass

class Fernet:
    def __init__(self, key):
        if isinstance(key, str):
            key = key.encode()
        
        # Decode the 32-byte url-safe base64 key
        try:
            key = base64.urlsafe_b64decode(key)
        except Exception:
            raise ValueError("Fernet key must be 32 base64-encoded bytes.")
            
        if len(key) != 32:
             raise ValueError("Fernet key must be 32 bytes.")

        self._signing_key = key[:16]
        self._encryption_key = key[16:]

    def encrypt(self, data):
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes.")

        current_time = int(time.time())
        iv = os.urandom(16)
        
        # Format: Version (0x80) | Timestamp (8 bytes) | IV (16 bytes) | Ciphertext | HMAC (32 bytes)
        
        # 1. Encrypt Data (AES-128-CBC)
        ciphertext = aes.encrypt_cbc(data, self._encryption_key, iv)
        
        # 2. Construct Basic Token
        basic_parts = (
            b"\x80" +
            struct.pack(">Q", current_time) +
            iv +
            ciphertext
        )
        
        # 3. Calculate HMAC
        h = hmac.new(self._signing_key, basic_parts, hashlib.sha256).digest()
        
        # 4. Final Token
        return base64.urlsafe_b64encode(basic_parts + h)

    def decrypt(self, token, ttl=None):
        if not isinstance(token, bytes):
            token = token.encode()

        try:
            data = base64.urlsafe_b64decode(token)
        except Exception:
             raise InvalidToken

        if len(data) < 57: # min length check
             raise InvalidToken
             
        # Verify HMAC
        # Version(1) + TS(8) + IV(16) + Cipher(...) = Length - 32
        h_expected = data[-32:]
        payload = data[:-32]
        
        h_calc = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        
        # Constant time compare recommended, but for this context == is likely acceptable
        # or use hmac.compare_digest
        if not hmac.compare_digest(h_calc, h_expected):
             raise InvalidToken

        # Check Version
        if payload[0] != 0x80:
             raise InvalidToken

        # Check Timestamp (TTL)
        if ttl:
             ts = struct.unpack(">Q", payload[1:9])[0]
             current_time = int(time.time())
             if ts + ttl < current_time or current_time + 60 < ts:
                  raise InvalidToken
        
        # Decrypt
        iv = payload[9:25]
        ciphertext = payload[25:]
        
        try:
             return aes.decrypt_cbc(ciphertext, self._encryption_key, iv)
        except Exception:
             raise InvalidToken

    @staticmethod
    def generate_key():
        return base64.urlsafe_b64encode(os.urandom(32))
