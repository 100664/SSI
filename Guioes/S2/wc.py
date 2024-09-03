import sys

def counter(file):
    with open(file, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        linhas = conteudo.count('\n')
        palavras = len(conteudo.split())
        caracteres = len(conteudo)
        
        return linhas, palavras, caracteres

def main(args):
    if len(args) == 2:
        file = args[1]
        linhas, palavras, caracteres = counter(file)
        if linhas is not None:
            print(f"{linhas:8} {palavras:8} {caracteres:8} {file}")

if __name__ == "__main__":
    main(sys.argv)
