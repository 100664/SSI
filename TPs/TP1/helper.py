from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization



def get_userdata(p12_fname):
    with open(p12_fname, "rb") as f:
        p12 = f.read()
    password = None
    (private_key, user_cert, [ca_cert]) = pkcs12.load_key_and_certificates(p12, password)
    return (private_key, user_cert, ca_cert)

def get_server_data(p12_fname):
    with open(p12_fname, "rb") as f:
        p12 = f.read()
    password = None  # Senha do arquivo P12, se houver
    (private_key, user_cert, _) = pkcs12.load_key_and_certificates(p12, password)
    return private_key, user_cert

def extract_pseudonym_from_certificate(user_cert):
    try:
        # Converter o certificado do usuário para um objeto x509.Certificate
        cert = x509.load_pem_x509_certificate(user_cert.public_bytes(serialization.Encoding.PEM))
        
        # Acessar os componentes do nome do certificado para encontrar o pseudônimo
        for name in cert.subject:
            if name.oid == NameOID.PSEUDONYM:
                return name.value
    except Exception as e:
        print("Erro ao extrair pseudônimo do certificado:", e)
    return None

def escrever_em_arquivo(texto):
    nome_arquivo = "/Users/martimr/Desktop/Uni/3ano2sem/SSI/projCA/log"
    with open(nome_arquivo, "a") as f:
        f.write(texto + "\n")