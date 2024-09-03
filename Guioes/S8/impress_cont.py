import sys

def impress_cont(filename):
    try:
        with open(filename, 'r') as arquivo:
            conteudo = arquivo.read()
            print(conteudo)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{filename}' não foi encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")

if len(sys.argv) != 2:
    print("Uso: python programa.py <nome_do_arquivo>")
    sys.exit(1)

filename = sys.argv[1]
impress_cont(filename)
