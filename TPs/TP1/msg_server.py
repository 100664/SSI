import asyncio
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography import x509
import bson
import os
import helper as helper

conn_cnt = 0
conn_port = 8443
max_msg_size = 99999

p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2

queue = {} #queue de mensagens para cada cliente
msg_id = {}
msg_id_already_sent = {}

server_RSA_private_key, server_cert = helper.get_server_data("/Users/martimr/Desktop/Uni/3ano2sem/SSI/projCA/MSG_SERVER.p12")

parameters = dh.DHParameterNumbers(p,g).parameters() #gerar os parâmetros DH

server_dh_private_key = parameters.generate_private_key() #gerar a chave privada DH
server_dh_public_key = server_dh_private_key.public_key() #obter a chave pública

# Serializar a chave pública do servidor para enviar ao cliente
server_dh_public_key_bytes = server_dh_public_key.public_bytes(
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











class ServerWorker(object):
    """ Classe que implementa a funcionalidade do SERVIDOR. """
    def __init__(self, cnt, addr=None):
        """ Construtor da classe. """
        self.id = cnt
        self.addr = addr
        self.msg_cnt = 0
        self.DH_shared_key = None





        

    async def process(self, reader, writer):
        """ Processa uma mensagem (`bytestring`) enviada pelo CLIENTE.
            Retorna a mensagem a transmitir como resposta (`None` para
            finalizar ligação) """
        self.msg_cnt += 1
        data = await reader.read(max_msg_size)
        decrypted_msg = decrypt_message(data, self.DH_shared_key)
        txt = bson.loads(decrypted_msg)

        if txt['flag'] == 'send':

            if 'flag' not in txt or txt['flag'] != 'send' or \
                'uid_receiver' not in txt or 'uid_sender' not in txt or \
                'subject' not in txt or 'content' not in txt or \
                'user_cert' not in txt:
                    writer.write(b'Mensagem mal formatada.')
                    await writer.drain()
                    return
            
            uid_sender = txt['uid_sender']
            uid_receiver = txt['uid_receiver']
            subject = txt['subject']
            content = txt['content']
            signature = txt['signature']
            user_cert = txt['user_cert']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"{self.id} : {uid_sender} enviou uma mensagem para {uid_receiver}.")

            helper.escrever_em_arquivo(f"{timestamp} - {uid_sender} enviou uma mensagem para {uid_receiver}.")

            if uid_receiver not in msg_id:
                msg_id[uid_receiver] = 1 
            else:
                msg_id[uid_receiver] += 1
                
            message_id = msg_id[uid_receiver]
            new_message = {
                'ID': message_id,
                'ID_sender': uid_sender,
                'subject': subject,
                'content': content,
                'signature': signature, 
                'user_cert': user_cert,
                'timestamp': timestamp
            }

            if uid_receiver not in queue:
                queue[uid_receiver] = []
            queue[uid_receiver].append(new_message)



            recibo = server_RSA_private_key.sign(
            txt['content'].encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

            rebico_msg = {
                'recibo': recibo,
                'server_cert' : server_cert.public_bytes(serialization.Encoding.PEM)
            }

            msg_to_send = encrypt_message(bson.dumps(rebico_msg), self.DH_shared_key)
            writer.write(msg_to_send)
            await writer.drain()







            
        elif txt['flag'] == 'askqueue':

            if 'flag' not in txt or txt['flag'] != 'askqueue' or \
            'uid_sender' not in txt:
                writer.write(b'Mensagem mal formatada.')
                await writer.drain()
                return
            
            uid_receiver = txt['uid_sender']
            print(f"{self.id} : '{uid_receiver}' está a pedir a sua queue de mensagens.")
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            helper.escrever_em_arquivo(f"{timestamp} - {uid_receiver} está a pedir a sua queue de mensagens.")
            

            if uid_receiver in queue:
                messages = queue[uid_receiver]

                for message in messages:
                    msg = {
                        'flag': 'MESSAGE_IN_QUEUE',
                        'ID': message['ID'],
                        'ID_sender': message['ID_sender'],
                        'subject': message['subject'],
                        'timestamp': message['timestamp']
                    }
                    msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)
                    writer.write(msg_to_send)
                    await writer.drain()

                    confirmation = await reader.read(max_msg_size)
                    if confirmation != b'ACK':
                        break

                writer.write(b'IS_OVER')
                await writer.drain()

            else:
                writer.write(b'NO_MESSAGES')
                await writer.drain()









        elif txt['flag'] == 'getmsg':
            if 'flag' not in txt or txt['flag'] != 'getmsg' or \
            'uid_request' not in txt or 'number_of_msg' not in txt:
                writer.write(b'Mensagem mal formatada.')
                await writer.drain()
                return

            uid_request = txt['uid_request']
            number_of_msg = txt['number_of_msg']

            print(f"{self.id} : '{uid_request}' pediu a mensagem de ID {number_of_msg}.")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            helper.escrever_em_arquivo(f"{timestamp} - {uid_request} pediu a mensagem de ID {number_of_msg}.")

            if (uid_request, number_of_msg) in msg_id_already_sent:
                requested_message = msg_id_already_sent[(uid_request, number_of_msg)]

                msg = {
                    'flag' : 'MSG_ALREADY_SENT',
                    'content': requested_message['content'],
                    'signature': requested_message['signature'],
                    'user_cert': requested_message['user_cert']

                }
                msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)
                writer.write(msg_to_send)
                await writer.drain()


            elif uid_request in queue:
                messages_main = queue[uid_request]

                all_ids = []
                for _, messages in queue.items():
                    for message in messages:
                        all_ids.append(message['ID'])

                if int(number_of_msg) in all_ids: #se o id estiver BANG
                    requested_message = None
                    for message in messages_main: 
                        if message['ID'] == int(number_of_msg):
                            requested_message = message
                            break
                    if requested_message is not None:
                        msg_id_already_sent[(uid_request, number_of_msg)] = requested_message
                        messages_main.remove(requested_message)
                        msg = {
                            'flag' : 'MSG_FOUND',
                            'content': requested_message['content'],
                            'signature': requested_message['signature'],
                            'user_cert': requested_message['user_cert']
                        }
                        msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)
                        writer.write(msg_to_send)
                        await writer.drain()
                    else:
                        msg_to_send = b'MSG_NOT_FOUND'
                        writer.write(msg_to_send)
                        await writer.drain()

                else: #se o id nao estiver BANG

                    msg_to_send = b'MSG_NOT_FOUND'
                    writer.write(msg_to_send)
                    await writer.drain()

            else:
                msg_to_send = b'MSG_NOT_FOUND'
                writer.write(msg_to_send)
                await writer.drain()






    
    async def defineSharedKey(self, reader, writer):
        writer.write(server_dh_public_key_bytes)
        await writer.drain()

        data = await reader.read(max_msg_size)
        txt = bson.loads(data) 
        client_DH_public_key_bytes = txt['client_dh_public_key']
        signature = txt['signature_client']
        user_cert = txt['user_cert']
        cert = x509.load_pem_x509_certificate(user_cert)
        client_RSA_public_key = cert.public_key()



        data_to_send = server_dh_public_key_bytes + client_DH_public_key_bytes
        
        try:
            client_RSA_public_key.verify(
            signature,
            data_to_send,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        except InvalidSignature:
            print("Assinatura inválida.")
            return
        except Exception as e:
            print("Erro na verificação da assinatura:", e)
            return
        
        client_DH_public_key = serialization.load_pem_public_key(client_DH_public_key_bytes)
        DH_shared_key = server_dh_private_key.exchange(client_DH_public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(DH_shared_key)

        self.DH_shared_key = derived_key

        signature_server = server_RSA_private_key.sign(
            data_to_send,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        server_cert_serializable = server_cert.public_bytes(serialization.Encoding.PEM)
        msg = {
            'signature_server' : signature_server,
            'server_cert' : server_cert_serializable
        }

        msg_to_send = bson.dumps(msg)
        writer.write(msg_to_send)
        await writer.drain()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        helper.escrever_em_arquivo(f"{timestamp} - Chave partilhada estabelecida com {self.addr}.")









        

async def handle_echo(reader, writer):
    global conn_cnt
    conn_cnt += 1
    addr = writer.get_extra_info('peername')
    srvwrk = ServerWorker(conn_cnt, addr)
    await srvwrk.defineSharedKey(reader, writer)
    await srvwrk.process(reader, writer)
    print("[%d]" % srvwrk.id)
    writer.close()


def run_server():
    loop = asyncio.new_event_loop()
    coro = asyncio.start_server(handle_echo, '127.0.0.1', conn_port)
    server = loop.run_until_complete(coro)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    helper.escrever_em_arquivo(f"{timestamp} - Servidor iniciado")

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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    helper.escrever_em_arquivo(f"{timestamp} - Servidor terminado\n")
    print('\nFINISHED!')

run_server()
