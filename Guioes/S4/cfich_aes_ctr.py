import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_file(input_filename, key_filename):
    with open(key_filename, 'rb') as fkey_file:
        key = fkey_file.read()

    nonce = os.urandom(16)  

    with open(input_filename, 'rb') as infile:
        plaintext = infile.read()

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))  
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)

    with open(input_filename + '.enc', 'wb') as outfile:
        outfile.write(nonce + ciphertext)

def decrypt_file(input_filename, key_filename):
    with open(key_filename, 'rb') as fkey_file:
        key = fkey_file.read()

    with open(input_filename, 'rb') as infile:
        file_contents = infile.read()
        nonce = file_contents[:16]
        ciphertext = file_contents[16:]

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce)) 
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext)

    with open(input_filename + '.dec', 'wb') as outfile:
        outfile.write(plaintext)

def main():
    if len(sys.argv) < 3:
        print("Uso: cfich_chacha20.py [setup|enc|dec] <filename> [<keyfile>]")
        sys.exit(1)

    operation = sys.argv[1]

    if operation == "setup":
        if len(sys.argv) != 3:
            print("Uso: cfich_chacha20.py setup <keyfile>")
            sys.exit(1)
        key_filename = sys.argv[2]
        key = os.urandom(16)  
        with open(key_filename, 'wb') as fkey_file:
            fkey_file.write(key)
    elif operation == "enc":
        if len(sys.argv) != 4:
            print("Uso: cfich_chacha20.py enc <filename> <keyfile>")
            sys.exit(1)
        input_filename = sys.argv[2]
        key_filename = sys.argv[3]
        encrypt_file(input_filename, key_filename)
    elif operation == "dec":
        if len(sys.argv) != 4:
            print("Uso: cfich_chacha20.py dec <filename> <keyfile>")
            sys.exit(1)
        input_filename = sys.argv[2]
        key_filename = sys.argv[3]
        decrypt_file(input_filename, key_filename)
    else:
        print("Operação não reconhecida.")
        sys.exit(1)

if __name__ == "__main__":
    main()
