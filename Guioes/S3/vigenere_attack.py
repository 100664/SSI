import sys
from collections import Counter
from vigenere import vigenere_cipher_dec
from itertools import product


def mostCommonLetter(text):
    frequency = Counter(text)
    return frequency.most_common(1)[0][0]


def generateCombinations(size, letterFrequency):
    combinations = [''.join(p) for p in product(letterFrequency, repeat=size)]
    def combinationWeight(combination):
        return sum(letterFrequency.index(char) for char in combination)
    sortedCombinations = sorted(combinations, key=combinationWeight)
    
    return sortedCombinations


def keyCombination(parts, attempt, size):
    key = ""
    
    for i in range(0,size):
        letter = parts[i]
        number = ord(letter) + (ord(attempt[i]) - ord("A"))
        if number > 90:
            number = 64 + (number - 90)
        key += chr(number)

    return key


def vigenereAttack(size,encripted,listaPalavras):
    letterFrequency = ['A', 'E', 'O', 'S', 'R', 'I', 'N', 'D', 'M', 'U', 'T', 'C', 'L', 'P', 'V', 'G', 'H', 'Q', 'B', 'F', 'Z', 'J', 'X', 'K', 'W', 'Y']
    # responsável por gerar todas as combinações possíveis de letras por ordem crescente de fre
    letterFrequencyCombinations = generateCombinations(size, letterFrequency)                       #gera todas as combinações possíveis de letras por ordem crescente de frequência
    sizeCombinations = len(letterFrequencyCombinations)                                             #tamanho do vetor de combinações

    parts = {}
    for i in range(size):
        parts[i] = ""
    for i in range(len(encripted)):
        parts[i % size] += encripted[i]

    mostCommonLetters = []
    for i in range(0, size):
        mostCommonLetters.append(mostCommonLetter(parts[i]))                                            #pega a letra mais comum de cada parte


    attempt = 1

    while True:
        possibleKey = keyCombination(mostCommonLetters, letterFrequencyCombinations[attempt - 1], size) #gera a chave com base na letra mais comum de cada parte e a combinação de letras
    
        possibleSolution = vigenere_cipher_dec(encripted, possibleKey)                                  #decifra o texto com a chave gerada

        if any(word in possibleSolution for word in listaPalavras):
            return possibleKey, possibleSolution
        
        attempt += 1

        if attempt > sizeCombinations:
            break

    return "",""


def main():
    if len(sys.argv) > 3:
        letterCombination, result = vigenereAttack(int(sys.argv[1]), sys.argv[2], sys.argv[3:])
        if result != "":
            print(f"{letterCombination}\n{result}")
    else:
        print('Error!\nExample usage: python3 cesar_attack.py "IGXZGMUKYZGTUVGVU" BACO PAPO')


if __name__ == '__main__':
    main()