import sys

def preproc(str):
    l = []
    for c in str:
        if c.isalpha():
            l.append(c.upper())
    return "".join(l) 

def caesar_cipher_enc(text, key):
    result = ''
    key = ord(key) - ord('A')                               #transforma a chave em um número inteiro, pois a chave é uma letra do alfabeto e a função 
                                                            #"ord" retorna o valor ASCII do caracter
    for char in text:                                       #percorre cada caracter da mensagem
        if char.isalpha():                                  #verifica se o caracter é uma letra
            shifted = ord(char) + key                       #somar o deslocamento para cifrar a mensagem
            if shifted > ord('Z'):                          #se o valor ASCII do caracter for maior que o valor ASCII de 'Z', 
                                                            #volta para o início do alfabeto e continua a aumentar
                shifted = shifted - ord('Z') + ord('A') - 1 #subtrai o valor ASCII de 'Z' do valor ASCII do caracter, soma o valor ASCII de 'A' e subtrai 1 
                                                            #(ou seja, volta para o início do alfabeto e continua a aumentar)
            result += chr(shifted)                          #adiciona o caracter cifrado à mensagem cifrada
        else:
            result += char                                  #adiciona o caracter à mensagem cifrada sem cifrar (caracteres especiais, números, etc)
    return result

def caesar_cipher_dec(text, key):
    result = ''
    key = ord(key.upper()) - ord('A')
    for char in text:
        if char.isalpha():
            shifted = ord(char) - key 
            if shifted < ord('A'):                            #se o valor ASCII do caracter for menor que o valor ASCII de 'A', 
                                                              #volta para o final do alfabeto e continua a diminuir
                shifted = ord('Z') - (ord('A') - shifted - 1) #subtrai o valor ASCII do caracter do valor ASCII de 'A' e subtrai 1
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
        encrypted = caesar_cipher_enc(message, key)
        print("Encrypted:", encrypted)
    elif operation == 'dec':
        decrypted = caesar_cipher_dec(message, key)
        print("Decrypted:", decrypted)
    else:
        print("Operação inválida. Use: enc ou dec")
    
if __name__ == "__main__":
    main()
    