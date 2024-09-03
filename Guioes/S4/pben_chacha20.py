# Importando as bibliotecas necessárias

#Perugunta: é necessário o salt ser guardado no ficheiro.enc? Não o usamos para nada, pois o salt é gerado aleatoriamente. SIM PRECISAMOS

import os
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidKey

def encrypt_file(input_filename, password):

    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    key = kdf.derive(password.encode())         # o derivo so recebe bytes, por esse motivo é necessário usar o encode

    nonce = os.urandom(16)

    with open(input_filename, 'rb') as infile:
        plaintext = infile.read()

    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    ct = encryptor.update(plaintext)

    with open(input_filename + '.enc', 'wb') as outfile:
        outfile.write(salt + nonce + ct)                            

def decrypt_file(input_filename, password):

    with open(input_filename, 'rb') as infile:
        file_contents = infile.read()
        salt_file = file_contents[:16]        
        nonce = file_contents[16:32] 
        ciphertext = file_contents[32:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt= salt_file,               
        iterations=480000
    )
    key_derived = kdf.derive(password.encode()) # é preciso derivar a chave dada no input para verificar a senha com a chave derivada do arquivo
 
    kdf_verify = PBKDF2HMAC(        #foi necessário criar um novo objeto para verificar a senha pois o objeto kdf já foi usado para derivar a chave
        algorithm=hashes.SHA256(),
        length=32,
        salt= salt_file,               
        iterations=480000
    )

    try:
        kdf_verify.verify(password.encode(), key_derived) #verifica se a senha está correta com o input fornceido
        print("Senha correta.")
        algorithm = algorithms.ChaCha20(key_derived, nonce)
        cipher = Cipher(algorithm, mode=None)
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext)

        with open(input_filename + '.dec', 'wb') as outfile:
            outfile.write(plaintext)

    except InvalidKey:
        print("Senha incorreta.")


def main():
    if len(sys.argv) < 3:
        print("Uso: cfich_chacha20.py [setup|enc|dec] <filename> [<password>]")
        sys.exit(1)

    operation = sys.argv[1]

    if operation == "enc":
        if len(sys.argv) != 4:
            print("Uso: cfich_chacha20.py enc <filename> <password>")
            sys.exit(1)
        input_filename = sys.argv[2]
        password = sys.argv[3]
        encrypt_file(input_filename, password)
    elif operation == "dec":
        if len(sys.argv) != 4:
            print("Uso: cfich_chacha20.py dec <filename> <keyfile>")
            sys.exit(1)
        input_filename = sys.argv[2]
        password = sys.argv[3]
        decrypt_file(input_filename, password)
    else:
        print("Operação não reconhecida.")
        sys.exit(1)

if __name__ == "__main__":
    main()
