import sys

def preproc(str):
    l = []
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l) 

def vigenere_cipher_enc(text, key):
    result = ''
    key_length = len(key)
    for i, char in enumerate(text):                         #enumerate() retorna o índice e o valor de cada elemento da lista (ou string) passada como argumento 
        if char.isalpha():
            key_char = key[i % key_length]                  # com o uso da divisão modular, a chave é repetida até que tenha o mesmo tamanho da mensagem 
            shift = ord(key_char) - ord('A')                #transforma a chave em um número inteiro, pois a chave é uma letra do alfabeto e a função
            shifted = ord(char) + shift                     #"ord" retorna o valor ASCII do caracter
            if shifted > ord('Z'):                          #se o valor ASCII do caracter for maior que o valor ASCII de 'Z', 
                                                            #volta para o início do alfabeto e continua a aumentar
                shifted = shifted - ord('Z') + ord('A') - 1 #subtrai o valor ASCII de 'Z' do valor ASCII do caracter, soma o valor ASCII de 'A' e subtrai 1
            result += chr(shifted)
        else:
            result += char
    return result


def vigenere_cipher_dec(text, key):
    result = ''
    key_length = len(key)
    for i, char in enumerate(text):
        if char.isalpha():
            key_char = key[i % key_length]
            shift = ord(key_char) - ord('A')
            shifted = ord(char) - shift  
            if shifted < ord('A'):  
                shifted = ord('Z') - (ord('A') - shifted - 1)
            result += chr(shifted)
        else:
            result += char
    return result

def main():
    if len(sys.argv) != 4:
        print("Forma de executar errada. Use: python cesar.py <enc|dec> <key> <message>")
        sys.exit(1)

    operation = sys.argv[1]
    key = sys.argv[2]
    message = preproc(sys.argv[3])

    if operation == 'enc':
        encrypted = vigenere_cipher_enc(message, key)
        print("Encrypted:", encrypted)
    elif operation == 'dec':
        decrypted = vigenere_cipher_dec(message, key)
        print("Decrypted:", decrypted)
    else:
        print("Operação inválida. Use: enc ou dec")
    
if __name__ == "__main__":
    main()
    