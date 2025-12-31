import hmac
import hashlib
import time
import struct
import base64

class TOTP:
    def __init__(self, s, digits=6, digest=hashlib.sha1, interval=30):
        self.digits = digits
        self.digest = digest
        self.interval = interval
        # Handle padding if missing
        missing_padding = len(s) % 8
        if missing_padding != 0:
            s += '=' * (8 - missing_padding)
        self.secret = base64.b32decode(s, casefold=True)

    def generate_otp(self, input_val):
        if input_val < 0:
            raise ValueError("input_val must be positive integer")
        
        # Pack input value into 8 bytes big endian
        val_struct = struct.pack('>Q', input_val)
        
        # HMAC-SHA1
        h = hmac.new(self.secret, val_struct, self.digest).digest()
        
        # Dynamic Truncation
        offset = h[-1] & 0x0F
        binary = struct.unpack('>I', h[offset:offset+4])[0] & 0x7FFFFFFF
        
        token = binary % (10 ** self.digits)
        return str(token).zfill(self.digits)

    def now(self):
        return self.generate_otp(self.timecode(time.time()))

    def timecode(self, for_time):
        return int(for_time) // self.interval

    def verify(self, otp, for_time=None, valid_window=0):
        if for_time is None:
            for_time = time.time()
            
        if valid_window:
            tm = self.timecode(for_time)
            for i in range(-valid_window, valid_window + 1):
                if self.generate_otp(tm + i) == str(otp):
                    return True
            return False
            
        return self.generate_otp(self.timecode(for_time)) == str(otp)

    def provisioning_uri(self, name, issuer_name=None):
        return f"otpauth://totp/{issuer_name}:{name}?secret={base64.b32encode(self.secret).decode().strip('=')}&issuer={issuer_name}"

def random_base32(length=32):
    return base64.b32encode(os.urandom(20)).decode('utf-8')[:length]

import os
