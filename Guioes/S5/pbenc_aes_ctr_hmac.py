import os
import sys
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

def encrypt_file(input_filename, password):

    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32*2,  
        salt=salt,
        iterations=480000,
    )
    
    key_material = kdf.derive(password.encode())
    key_cipher = key_material[:32]
    key_mac = key_material[32:]

    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key_cipher), modes.CTR(nonce))
    encryptor = cipher.encryptor()

    with open(input_filename, 'rb') as infile:
        plaintext = infile.read()

    ciphertext = encryptor.update(plaintext)

    h = hmac.HMAC(key_mac, hashes.SHA256())
    h.update(ciphertext)
    signature = h.finalize()

    with open(input_filename + '.enc', 'wb') as outfile:
        outfile.write(salt + nonce + ciphertext + signature)

def decrypt_file(input_filename, password):
    with open(input_filename, 'rb') as infile:
        file_contents = infile.read()
        nonce = file_contents[16:32]
        salt_file = file_contents[:16]
        signature = file_contents[-32:]
        ciphertext = file_contents[32:-32]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32*2, 
        salt= salt_file,
        iterations=480000,
    )
    
    key_material = kdf.derive(password.encode())
    key_cipher = key_material[:32]
    key_mac = key_material[32:]

    h = hmac.HMAC(key_mac, hashes.SHA256())
    h.update(ciphertext)
    h_copy = h.copy()

    try:
        h.verify(signature)
        print("Autenticidade verificada.")
        cipher = Cipher(algorithms.AES(key_cipher), modes.CTR(nonce))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext)

        with open(input_filename + '.dec', 'wb') as outfile:
            outfile.write(plaintext)
    except InvalidKey:
        h_copy.verify(b"an incorrect signature")
        print("Autenticidade comprometida. O arquivo pode ter sido alterado.")


def main():
    if len(sys.argv) < 3:
        print("Uso: pbenc_aes_ctr_hmac.py [enc|dec] <filename> <password>")
        sys.exit(1)

    operation = sys.argv[1]

    if operation == "enc":
        if len(sys.argv) != 4:
            print("Uso: pbenc_aes_ctr_hmac.py enc <filename> <password>")
            sys.exit(1)
        input_filename = sys.argv[2]
        password = sys.argv[3]
        encrypt_file(input_filename, password)
    elif operation == "dec":
        if len(sys.argv) != 4:
            print("Uso: pbenc_aes_ctr_hmac.py dec <filename> <password>")
            sys.exit(1)
        input_filename = sys.argv[2]
        password = sys.argv[3]
        decrypt_file(input_filename, password)
    else:
        print("Operação não reconhecida.")
        sys.exit(1)

if __name__ == "__main__":
    main()