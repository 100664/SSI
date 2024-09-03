import string

def preproc(str):
      l = []
      for c in str:
              l.append(c.upper())
      return "".join(l)  

import string

def decrypt(text, key):
    decrypted_text = ''                                     #variável que armazenará a mensagem decifrada
    key = ord(key) - ord('A')                               #transforma a chave em um número inteiro
    for char in text:                                       #percorre cada caracter da mensagem                    
        if char.isalpha():                                  #verifica se o caracter é uma letra                   
            shifted = ord(char) - key                       #subtrai o deslocamento para decifrar a mensagem       
            if shifted < ord('A'):                          #se o valor ASCII do caracter for menor que o valor ASCII de 'A',         
                shifted = shifted + ord('Z') - ord('A') + 1 #volta para o final do alfabeto e continua a diminuir
            decrypted_text += chr(shifted)                  #adiciona o caracter decifrado à mensagem decifrada
        else:
            decrypted_text += char                          #adiciona o caracter à mensagem decifrada sem decifrar (caracteres especiais, números, etc)
    return decrypted_text                                   #retorna a mensagem decifrada

def caesar_attack(ciphertext, words):
    for shift in range(26):                                                 #percorre todas as possíveis chaves de cifra de César (26 letras do alfabeto)
        decrypted_text = decrypt(ciphertext, string.ascii_uppercase[shift]) #decifra a mensagem com a chave atual
        if any(word.upper() in decrypted_text for word in words):           #verifica se alguma das palavras passadas como argumento está na mensagem decifrada
            return string.ascii_uppercase[shift], decrypted_text            #retorna a chave e a mensagem decifrada
    return None, None                                                       #retorna None caso não consiga decifrar a mensagem

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 cesar_attack.py <ciphertext> <word1> <word2> ...")
        sys.exit(1)

    ciphertext = preproc(sys.argv[1])
    word1 = preproc(sys.argv[2])
    word2 = preproc(sys.argv[3])
    words = [word1, word2]
    
    letter, decrypted_text = caesar_attack(ciphertext, words)

    if letter is not None:
        print(letter)
        print(decrypted_text)
    else:
        print("Failed to decrypt the message!")

if __name__ == "__main__":
    main()
