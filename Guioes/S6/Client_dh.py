import asyncio
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.dh  import DHParameters
import os

conn_port = 8443
max_msg_size = 9999

p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2

# Gerar os parâmetros DH
parameters = dh.DHParameterNumbers(p,g).parameters()

# Gerar a chave privada DH e obter a chave pública
private_key = parameters.generate_private_key()
public_key = private_key.public_key()

# Serializar a chave pública para enviar ao servidor
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def encrypt_message(message, key):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message, None)
    return nonce + ciphertext

def decrypt_message(encrypted_message, key):
    aesgcm = AESGCM(key)
    nonce = encrypted_message[:12]
    ciphertext = encrypted_message[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext

class Client:
    def __init__(self, sckt=None):
        self.sckt = sckt
        self.msg_cnt = 0
        self.shared_key = None

    # Processar as mensagens que chegam do servidor e enviar novas
    def process(self, msg=b""):
        self.msg_cnt += 1
        if msg != b"":
            decrypted_msg = decrypt_message(msg, self.shared_key)
            print(f'Received ({self.msg_cnt}): {decrypted_msg.decode()}')
        print('Input message to send (empty to finish)')
        new_msg = input().encode()
        if len(new_msg) > 0:
            return encrypt_message(new_msg, self.shared_key)
        else:
            return None

    # Definir a chave partilhada a partir da chave pública do servidor
    async def defineSharedKey(self, reader, writer):
        msg = await reader.read(max_msg_size)
        server_public_key = serialization.load_pem_public_key(msg)
        shared_key = private_key.exchange(server_public_key)

        # Derivar uma chave simétrica a partir da chave compartilhada
        derived_key = HKDF( 
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        self.shared_key = derived_key
        print(f"Chave compartilhada estabelecida.")
        writer.write(public_key_bytes) # Enviar a chave pública do cliente para o servidor fazer o mesmo
        await writer.drain()

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr)
    await client.defineSharedKey(reader, writer)
    msg = client.process()
    while msg:
        writer.write(msg)
        await writer.drain()
        print("Waiting message from server")
        msg = await reader.read(max_msg_size)
        print("Recieved message from server")
        if msg :
            msg = client.process(msg)
        else:
            break
    writer.write(b'\n')
    print('Socket closed!')
    writer.close()

def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())


run_client()

