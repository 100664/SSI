import asyncio
import os
import socket
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

conn_cnt = 0
conn_port = 8443
max_msg_size = 9999

class ServerWorker(object):
        def __init__(self, cnt, addr=None):
            self.id = cnt
            self.addr = addr
            self.msg_cnt = 0
            self.shared_key = b'5r9XqL#u@J3Z6*dN'  # Substitua por uma chave segura

        def encrypt_message(self, message, nonce):
            aesgcm = AESGCM(self.shared_key)
            ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
            return ciphertext

        def decrypt_message(self, ciphertext, nonce):
            aesgcm = AESGCM(self.shared_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode()

        def process(self, msg):
            """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
                Retorna a mensagem a transmitir como resposta (`None` para
                finalizar ligação) """
            self.msg_cnt += 1

            nonce = msg[:12]
            ciphertext = msg[12:]

            decrypted_msg = self.decrypt_message(ciphertext, nonce)
            print(f'Received from Client {self.id} ({self.msg_cnt}): {decrypted_msg}')

            # Encrypt the response message
            new_msg = input('Input message to send (empty to finish): ')
            if new_msg:
                new_nonce = os.urandom(12)
                encrypted_msg = self.encrypt_message(new_msg, new_nonce)
                encrypted_msg_with_nonce = new_nonce + encrypted_msg
                return encrypted_msg_with_nonce
            else:
                return None









async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt +=1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
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
