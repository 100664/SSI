import sys
import itertools

def xor_bytes(bytes1, bytes2):
    """Perform XOR operation between two bytes objects."""
    return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])

def decrypt_with_key(ciphertext, key):
    """Decrypt ciphertext using the given key."""
    print("Ciphertext:", ciphertext)
    print("Key:", key)
    decrypted_message = xor_bytes(ciphertext, key)
    print("Decrypted message:", decrypted_message)
    return decrypted_message


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 bad_otp_attack.py <ciphertext_file> <word1> <word2> ...")
        sys.exit(1)

    ciphertext_file = sys.argv[1]
    words = sys.argv[2:]

    with open(ciphertext_file, 'rb') as f:
        ciphertext = f.read()

    ciphertext_length = len(ciphertext)

    # Generate all possible permutations of words
    for permutation in itertools.permutations(words):
        key_candidate = bytes(''.join(permutation), 'utf-8')[:ciphertext_length]
        print("Chave candidata:", key_candidate)
        decrypted_message = decrypt_with_key(ciphertext, key_candidate)
        print("Mensagem descriptografada (hexadecimal):", decrypted_message.hex())
        if all(word.encode('utf-8') in decrypted_message.lower() for word in words):
            print("Mensagem descriptografada com sucesso:")
            print(decrypted_message.decode('utf-8'))
            break
    else:
        print("Unable to decrypt the message with the given words.")