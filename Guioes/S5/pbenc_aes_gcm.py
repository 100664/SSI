import os
import sys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file_aes_gcm(input_filename, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # Adjust the number of iterations as needed
    )
    derive_key = kdf.derive(password.encode())
    cipher = AESGCM(derive_key)
    nonce = os.urandom(12)

    with open(input_filename, 'rb') as infile:
        plaintext = infile.read()

    ct = cipher.encrypt(nonce, plaintext, None)

    with open(input_filename + '.enc', 'wb') as outfile:
        outfile.write(salt + nonce + ct)

def decrypt_file_aes_gcm(input_filename, password):
    
    with open(input_filename, 'rb') as infile:
        file_contents = infile.read()
        salt = file_contents[:16]
        nonce = file_contents[16:28]
        ct = file_contents[28:]
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # Adjust the number of iterations as needed
    )
    derive_key = kdf.derive(password.encode())
    cipher = AESGCM(derive_key)
    plaintext = cipher.decrypt(nonce, ct, None)

    with open(input_filename + '.dec', 'wb') as outfile:
        outfile.write(plaintext)

def main():
    if len(sys.argv) < 4:
        print("Usage: pbenc_aes_gcm.py [enc|dec] <filename> sua_senha")
        sys.exit(1)

    operation = sys.argv[1]
    input_filename = sys.argv[2]
    senha = sys.argv[3]

    if operation == "enc":
        encrypt_file_aes_gcm(input_filename, senha)
    elif operation == "dec":
        decrypt_file_aes_gcm(input_filename, senha)
    else:
        print("Operation not recognized.")
        sys.exit(1)

if __name__ == "__main__":
    main()