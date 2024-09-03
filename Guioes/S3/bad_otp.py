import sys
import random

def bad_prng(n):
    """ an INSECURE pseudo-random number generator """
    random.seed(random.randbytes(2))
    return random.randbytes(n)

def encrypt(message_file, key_file):
    with open(message_file, 'rb') as mf, open(key_file, 'rb') as kf:    
        message = mf.read()                                             
        key = kf.read()                                                 

        encrypted_message = b''
        for m, k in zip(message, key):                                                       
            encrypted_message += bytes([m ^ k])                         

        output_filename = message_file + ".enc"                        
        with open(output_filename, 'wb') as ef:                       
            ef.write(encrypted_message)                               

def decrypt(ciphertext_file, key_file):                                
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
        print("  For generating random bytes: python otp.py setup <num_bytes> <output_file>")
        print("  For encryption: python otp.py enc <message_file>")
        print("  For decryption: python otp.py dec <ciphertext_file> <key_file>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "setup":
        if len(sys.argv) != 4:
            print("Usage: python otp.py setup <num_bytes> <output_file>")
            sys.exit(1)
        num_bytes = int(sys.argv[2])
        output_file = sys.argv[3]
        with open(output_file, 'wb') as f: # a unica diferença do otp.py é que aqui é usado o bad_prng e é escrito no ficheiro na main
            f.write(bad_prng(num_bytes))

    elif command == "enc":
        if len(sys.argv) != 4:
            print("Usage: python otp.py enc <message_file>")
            sys.exit(1)
        message_file = sys.argv[2]
        key_file = sys.argv[3]
        encrypt(message_file, key_file)

    elif command == "dec":
        if len(sys.argv) != 4:
            print("Usage: python otp.py dec <ciphertext_file> <key_file>")
            sys.exit(1)
        ciphertext_file = sys.argv[2]
        key_file = sys.argv[3]
        decrypt(ciphertext_file, key_file)

    else:
        print("Unknown command")
        sys.exit(1)

# Exemplo de uso
'''
inputs:
python3 bad_otp.py setup 30 bad_otp.key    
echo "Mensagem a cifrar" > bad_ptxt.txt     (serve para criar o ficheiro com a mensagem a ser cifrada)
python3 bad_otp.py enc bad_ptxt.txt bad_otp.key
python3 bad_otp.py dec bad_ptxt.txt.enc bad_otp.key
cat bad_ptxt.txt.enc.dec                    (serve para mostrar a mensagem decifrada)

output: Mensagem a cifrar
'''