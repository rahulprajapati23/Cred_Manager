import pyotp
secret = "DQMHWZAWZJ6MSRASMNJRFX6O3ZJ4PVUW"
totp = pyotp.TOTP(secret)
print(totp.now())
