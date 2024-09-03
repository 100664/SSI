import sys
from cfich_chacha20 import decrypt_file, encrypt_file

def chacha20Attack(encryptedFile, position, textAtPosition, newTextAtPosition):
    with open(encryptedFile, 'rb') as file:
        encoded = file.read()
    
    nonce = encoded[:16]
    content = bytearray(encoded[16:])
    contentAux = bytearray(encoded[16:])

    testKey = bytearray([0x01] * 32)

    textAtPositionBytes = textAtPosition.encode()
    newTextAtPositionBytes = newTextAtPosition.encode()

    byteCombination = [i for i in range(256)]
    
    for letter, (original_byte, new_byte) in enumerate(zip(textAtPositionBytes, newTextAtPositionBytes)):
        actual_position = position + letter
        print(actual_position)

        for byte in byteCombination:
            testKey[actual_position] = byte
            possibleDecoded = decrypt_file(encoded, testKey)
            if possibleDecoded[actual_position] == original_byte:
                print("Found match attempt", letter, "for byte", byte)
                
                contentAux[actual_position] = new_byte
                getTheLetter = encrypt_file(contentAux, testKey, nonce)
                content[actual_position] = getTheLetter[actual_position]

                break 
    
    with open(f"{encryptedFile}.attack", 'wb') as file:
        file.write(nonce)
        file.write(content)



def main():
    if len(sys.argv) == 5:
        chacha20Attack(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
    else:
        print("Error!")


if __name__ == '__main__':
    main()
