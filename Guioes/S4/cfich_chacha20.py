# Importando as bibliotecas necessárias
import os
import struct
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_file(input_filename, key_filename):
    with open(key_filename, 'rb') as fkey_file:
        key = fkey_file.read()

    nonce = os.urandom(16)                                      # Gera um NONCE aleatório de 16 bytes

    with open(input_filename, 'rb') as infile:                  # Lê o arquivo de entrada         
        plaintext = infile.read()                               # Lê o arquivo inteiro            

    algorithm = algorithms.ChaCha20(key, nonce)                 # Cria um objeto de algoritmo de criptografia em que o primeiro argumento é a chave e o segundo é o NONCE
    cipher = Cipher(algorithm, mode=None)                       # Cria um objeto de cifra em que o primeiro argumento é o algoritmo e o segundo é o modo, 
                                                                # o mode ser None indica que estamos usando o modo de operação padrão 

    encryptor = cipher.encryptor()                              # Cria um objeto de criptografia
    ct = encryptor.update(plaintext)                            # Criptografa o texto puro

    with open(input_filename + '.enc', 'wb') as outfile:        # Escreve o criptograma no arquivo de saída
        outfile.write(nonce + ct)                               # Escreve o NONCE e o criptograma no arquivo de saída

def decrypt_file(input_filename, key_filename):
    with open(key_filename, 'rb') as fkey_file:
        key = fkey_file.read()

    with open(input_filename, 'rb') as infile:
        file_contents = infile.read()                           # Lê o arquivo inteiro
        nonce = file_contents[:16]                              # Extrai o NONCE que está no início do arquivo
        ciphertext = file_contents[16:]                         # Extrai o criptograma que está no restante do arquivo

    algorithm = algorithms.ChaCha20(key, nonce)                 # Cria um objeto de algoritmo de criptografia em que o primeiro argumento é a chave e o segundo é o NONCE
    cipher = Cipher(algorithm, mode=None)                       # Cria um objeto de cifra em que o primeiro argumento é o algoritmo e o segundo é o modo,
    decryptor = cipher.decryptor()                              # Cria um objeto de descriptografia
    plaintext = decryptor.update(ciphertext)                    # Descriptografa o criptograma

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
        key = os.urandom(32)
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
