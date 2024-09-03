import sys
import os

def generate_random_bytes(num_bytes, output_file):
    with open(output_file, 'wb') as f:                   #abre o arquivo e escreve os bytes aleatórios    
        random_bytes = os.urandom(num_bytes)             #os.urandom() retorna uma string de bytes aleatórios do tamanho especificado
        f.write(random_bytes)                            #escreve os bytes aleatórios no arquivo                       

def encrypt(message_file, key_file):
    with open(message_file, 'rb') as mf, open(key_file, 'rb') as kf:    #abre os arquivos e lê os bytes
        message = mf.read()                                             #lê os bytes do arquivo da mensagem (ptxt.txt)
        key = kf.read()                                                 #lê os bytes do arquivo da chave (otp.key)

        encrypted_message = b''
        for m, k in zip(message, key):                                  #percorre os bytes da mensagem e da chave                     
            encrypted_message += bytes([m ^ k])                         #faz a operação XOR entre os bytes da mensagem e da chave, 
                                                                        #o zip() junta os bytes da mensagem e da chave em pares

        output_filename = message_file + ".enc"                         #cria o nome do arquivo de saída
        with open(output_filename, 'wb') as ef:                         #abre o arquivo de saída
            ef.write(encrypted_message)                                 #escreve a mensagem cifrada no arquivo

def decrypt(ciphertext_file, key_file):                                 #mesma ideia que o encrypt, mas agora para decifrar
    with open(ciphertext_file, 'rb') as cf, open(key_file, 'rb') as kf:
        ciphertext = cf.read()
        key = kf.read()

        decrypted_message = b''
        for c, k in zip(ciphertext, key):
            decrypted_message += bytes([c ^ k])

        output_filename = ciphertext_file + ".dec"
        with open(output_filename, 'wb') as df:
            df.write(decrypted_message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  For generating random bytes: python otp.py setup <num_bytes> <output_file>") # otp.py setup 100 keyfile
        print("  For encryption: python otp.py enc <message_file> <key_file>")                # otp.py enc messagefile keyfile
        print("  For decryption: python otp.py dec <ciphertext_file> <key_file>")             # otp.py dec messagefile.enc keyfile
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        if len(sys.argv) != 4:
            print("Usage: python otp.py setup <num_bytes> <output_file>")
            sys.exit(1)
        num_bytes = int(sys.argv[2])                             
        output_file = sys.argv[3]
        generate_random_bytes(num_bytes, output_file)                                         #responsável por gerar os bytes aleatórios

    elif command == "enc":
        if len(sys.argv) != 4:
            print("Usage: python otp.py enc <message_file> <key_file>")
            sys.exit(1)
        message_file = sys.argv[2]
        key_file = sys.argv[3]
        encrypt(message_file, key_file)                                                        #responsável por cifrar a mensagem

    elif command == "dec":
        if len(sys.argv) != 4:
            print("Usage: python otp.py dec <ciphertext_file> <key_file>")
            sys.exit(1)
        ciphertext_file = sys.argv[2]
        key_file = sys.argv[3]
        decrypt(ciphertext_file, key_file)                                                      #responsável por decifrar a mensagem

    else:
        print("Unknown command")
        sys.exit(1)

# Exemplo de uso
'''
inputs:
python3 otp.py setup 30 otp.key    
echo "Mensagem a cifrar" > ptxt.txt     (serve para criar o ficheiro com a mensagem a ser cifrada)
python3 otp.py enc ptxt.txt otp.key
python3 otp.py dec ptxt.txt.enc otp.key
cat ptxt.txt.enc.dec                    (serve para mostrar a mensagem decifrada)

output: Mensagem a cifrar
'''
