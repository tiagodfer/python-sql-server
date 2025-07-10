from argon2 import PasswordHasher

# Initialize the Argon2 password hasher
ph = PasswordHasher()

# The password to hash
password = 'teste123'

# Hash the password
hashed_password = ph.hash(password)

print("Original password:", password)
print("Argon2 hash:", hashed_password)
