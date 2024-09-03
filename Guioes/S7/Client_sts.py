from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hmac
from cryptography import x509

def generate_shared_key(private_key, public_key):
    """Gera a chave compartilhada usando Diffie-Hellman."""
    shared_key = private_key.exchange(public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'station-to-station',
        backend=default_backend()
    ).derive(shared_key)
    return derived_key

def sign_message(private_key, message):
    """Assina a mensagem usando RSA."""
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, message, signature):
    """Verifica a assinatura usando RSA."""
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def main():
    # Carregar a chave privada e pública do cliente
    with open('MSG_CLI1.key', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=b'1234',
            backend=default_backend()
        )

    with open('MSG_CLI1.crt', 'rb') as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        client_public_key = cert.public_key()

    # Obter a chave pública do servidor
    with open('MSG_SERVER.crt', 'rb') as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        server_public_key = cert.public_key()

    # Troca de chaves Diffie-Hellman
    shared_key = generate_shared_key(private_key, server_public_key)

    # Assinar e enviar a chave pública do cliente ao servidor
    client_public_key_bytes = client_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    client_signature = sign_message(private_key, client_public_key_bytes)

    # Receber a chave pública do servidor e a assinatura do servidor
    # Aqui, por simplicidade, suponhamos que o cliente já tenha a chave pública do servidor e a assinatura

    # Verificar a assinatura da chave pública do servidor
    if verify_signature(server_public_key, server_public_key_bytes, server_signature):
        print("Assinatura do servidor verificada com sucesso!")
    else:
        print("Falha ao verificar a assinatura do servidor.")

    # Assinar e enviar a chave pública do cliente ao servidor
    server_public_key_bytes = server_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    server_signature = sign_message(private_key, server_public_key_bytes)

    # Finalizar a troca de chaves
    # Aqui, por simplicidade, suponhamos que o servidor já tenha a chave pública do cliente e a assinatura

    # Usar a chave compartilhada para comunicação segura com o servidor
    # Aqui você pode usar a chave compartilhada para criptografar e descriptografar mensagens

if __name__ == "__main__":
    main()
