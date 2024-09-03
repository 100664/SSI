import asyncio
import socket
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

conn_port = 8443
max_msg_size = 9999

class Client:
    def __init__(self, sckt=None):
        self.sckt = sckt
        self.msg_cnt = 0
        self.shared_key = b'5r9XqL#u@J3Z6*dN'  # Substitua por uma chave segura

    def encrypt_message(self, message):
        aesgcm = AESGCM(self.shared_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
        encrypted_message = nonce + ciphertext
        return encrypted_message

    def decrypt_message(self, encrypted_message):
        aesgcm = AESGCM(self.shared_key)
        nonce = encrypted_message[:12]
        ciphertext = encrypted_message[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    def process(self, msg=b""):
        """ Processa uma mensagem (`bytestring`) enviada pelo SERVIDOR.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt += 1
        if (msg == b''):
            new_msg = input('Input message to send: ')
            encrypted_msg = self.encrypt_message(new_msg)
            return encrypted_msg
        
        # Decrypt the received message
        decrypted_msg = self.decrypt_message(msg)
        print(f'Received ({self.msg_cnt}): {decrypted_msg}')

        # Encrypt the response message
        new_msg = input('Input message to send (empty to finish): ')
        if new_msg:
            encrypted_msg = self.encrypt_message(new_msg)
            return encrypted_msg
        else:
            return None
        


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr)
    msg = client.process()
    while msg:
        writer.write(msg)
        msg = await reader.read(max_msg_size)
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
