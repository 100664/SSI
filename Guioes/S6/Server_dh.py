import asyncio
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.dh  import DHParameters
import os

conn_cnt = 0
conn_port = 8443
max_msg_size = 9999

p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2

parameters = dh.DHParameterNumbers(p,g).parameters() #gerar os parâmetros DH

private_key = parameters.generate_private_key() #gerar a chave privada DH
public_key = private_key.public_key() #obter a chave pública

# Serializar a chave pública do servidor para enviar ao cliente
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

class ServerWorker:
    def __init__(self, cnt, addr=None):
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0
        self.shared_key = None

    # Processar as mensagens que chegam do cliente e enviar novas
    def process(self, msg):
        decrypted_msg = decrypt_message(msg, self.shared_key)
        print(f'{self.id}: {decrypted_msg.decode()}')
        response = decrypted_msg.decode().upper()
        if len(response) > 0:
            return encrypt_message(response.encode(), self.shared_key)
        else:
            return None
        
    # Definir a chave partilhada a partir da chave pública do cliente
    async def defineSharedKey(self, reader, writer):
        writer.write(public_key_bytes) # enviar a chave pública do servidor para o cliente fazer o mesmo
        await writer.drain()
        data = await reader.read(max_msg_size)
        client_public_key = serialization.load_pem_public_key(data)
        shared_key = private_key.exchange(client_public_key)
        
        # Derivar uma chave simétrica a partir da chave compartilhada
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        self.shared_key = derived_key
        print(f"Chave compartilhada estabelecida.")


#
#
# Funcionalidade Cliente/Servidor
#
# obs: não deverá ser necessário alterar o que se segue
#


async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt += 1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
    await srvwrk.defineSharedKey(reader, writer)
    data = await reader.read(max_msg_size)
    while True:
        if not data: continue
        if data[:1]==b'\n': break
        data = srvwrk.process(data)
        if not data: break
        writer.write(data)
        await writer.drain()
        data = await reader.read(max_msg_size)
    print("[%d]" % srvwrk.id)
    writer.close()


def run_server():
    loop = asyncio.new_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', conn_port)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    print('  (type ^C to finish)\n')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    print('\nFINISHED!')

run_server()