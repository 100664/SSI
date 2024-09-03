import asyncio
import helper as helper
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography import x509
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import bson
from datetime import datetime
import os
import argparse
import sys

string_ERRO = """ 
MSG RELAY SERVICE: command error!

COMANDOS PERMITIDOS:
    - user <FNAME>: especifica o ficheiro com dados do utilizador.
    - send <UID> <SUBJECT>:  envia uma mensagem com assunto <SUBJECT> destinada ao utilizador com identificador <UID>.
    - askqueue: solicita ao servidor que lhe envie a lista de mensagens não lidas da queue do utilizador. 
    - getmsg <NUM>: solicita ao servidor o envio da mensagem da sua queue com número <NUM>.
    - help: imprime instruções de uso do programa.
        
"""

conn_port = 8443
max_msg_size = 99999
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2
path_file_log = "/Users/martimr/Desktop/Uni/3ano2sem/SSI/projCA/log"

# Gerar os parâmetros DH
parameters = dh.DHParameterNumbers(p, g).parameters()

# Gerar a chave privada DH e obter a chave pública
client_dh_private_key = parameters.generate_private_key()
client_dh_public_key = client_dh_private_key.public_key()

# Serializar a chave pública para enviar ao servidor
client_dh_public_key_bytes = client_dh_public_key.public_bytes(
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
    """ Classe que implementa a funcionalidade de um CLIENTE. """

    def __init__(self, sckt=None):
        """ Construtor da classe. """
        self.sckt = sckt
        self.user_certeficado = None
        self.ca_certeficado = None
        self.private_key = None
        self.shared_key = None
        self.args = None  # Adicione um atributo para armazenar os argumentos






    def set_arguments(self):
        try:
            parser = argparse.ArgumentParser(description='MSG Relay Client')
            parser.add_argument('-user', metavar='<FNAME>')
            parser.add_argument('action', choices=['send', 'askqueue', 'getmsg', 'help'])
            parser.add_argument('args', nargs='*')

            self.args = parser.parse_args()


            private_key, user_cert, ca_cert = helper.get_userdata(self.args.user)
            self.user_certeficado = user_cert
            self.ca_certeficado = ca_cert
            self.private_key = private_key

        except (Exception, SystemExit, SystemError) as e:
            sys.stderr.write(string_ERRO)









    async def process(self, reader, writer):
        

            if self.args.action == 'send':
                if len(self.args.args) < 3:
                    sys.stderr.write(string_ERRO)
                    writer.write(b'Erro ao processar comando: argumentos insuficientes/em demasia.')
                else:
                    
                    uid_receiver = self.args.args[0]
                    subject = self.args.args[1]
                    content = self.args.args[2]
                    uid_sender = helper.extract_pseudonym_from_certificate(self.user_certeficado)

                    if (uid_receiver == uid_sender):
                        sys.stderr.write(string_ERRO)
                    else:
                        
                        signature = self.private_key.sign(
                            content.encode(),
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH
                            ),
                            hashes.SHA256()
                        )

                        msg = {
                            'flag' : 'send',
                            'uid_receiver' : uid_receiver,
                            'uid_sender' : uid_sender,
                            'subject' : subject,
                            'content' : content,
                            'signature' : signature, #tenho que assinar toda a mensagem
                            'user_cert' : self.user_certeficado.public_bytes(serialization.Encoding.PEM)
                        }

                        msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)

                        writer.write(msg_to_send)
                        await writer.drain()

                        msg_bytes_to_confirm = await reader.read(max_msg_size)
                        msg = decrypt_message(msg_bytes_to_confirm, self.DH_shared_key)
                        txt = bson.loads(msg)

                        recibo  = txt['recibo']
                        content_in_bytes = content.encode()
                        server_cert = txt['server_cert']
                        cert = x509.load_pem_x509_certificate(server_cert)
                        RSA_public_key_to_recibo = cert.public_key()

                        try:
                            RSA_public_key_to_recibo.verify(
                            recibo,
                            content_in_bytes,
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH
                            ),
                            hashes.SHA256()
                        )
                        except InvalidSignature:
                            sys.stderr.write("Server não recebeu a mensagem corretamente.")
                            return
                        except Exception as e:
                            sys.stderr.write("Server não recebeu a mensagem corretamente.")
                            return

                        sys.stdout.write("Mensagem enviada com sucesso.\n\n")











            elif self.args.action == 'askqueue':
                if len(self.args.args) > 0:
                    sys.stderr.write(string_ERRO)
                    writer.write(b'Erro ao processar comando: argumentos insuficientes/em demasia.')
                else:
                    uid_sender = helper.extract_pseudonym_from_certificate(self.user_certeficado)

                    msg = {
                        'flag' : 'askqueue',
                        'uid_sender' : uid_sender,
                    }
                    msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)
                    writer.write(msg_to_send)
                    await writer.drain()
                
                    while True:
                        data = await reader.read(max_msg_size)
                        #print(data)
                        if data[:7] == b'IS_OVER':
                            sys.stdout.write("Não há mais mensagens na QUEUE\n")
                            break
                        elif data[:11] == b'NO_MESSAGES':
                            sys.stdout.write("Não existem mensagens na QUEUE.\n")
                            break
                        else:
                            msg_bytes = decrypt_message(data, self.DH_shared_key)
                            #print (msg_bytes)
                            msg = bson.loads(msg_bytes)
                            #print(msg)
                            if msg['flag'] == "MESSAGE_IN_QUEUE":
                                print(f"ID: {msg['ID']};\n UID_SENDER: {msg['ID_sender']};\n SUBJECT: {msg['subject']};\n TIMESTAMP: {msg['timestamp']}\n\n")

                                writer.write(b'ACK')
                                await writer.drain()
                        







            elif self.args.action == 'getmsg':
                if len(self.args.args) != 1:
                    sys.stderr.write(string_ERRO)
                    writer.write(b'Erro ao processar comando: argumentos insuficientes/em demasia.')
                    
                else:
                    uid_request = helper.extract_pseudonym_from_certificate(self.user_certeficado)
                    number_of_msg = self.args.args[0]
                    msg = {
                        'flag' : 'getmsg',
                        'uid_request' : uid_request,
                        'number_of_msg' : number_of_msg
                    }
                    msg_to_send = encrypt_message(bson.dumps(msg), self.DH_shared_key)
                    writer.write(msg_to_send)
                    await writer.drain()

                    msg_bytes = await reader.read(max_msg_size)

                    print (msg_bytes)

                    if (msg_bytes == b'MSG_NOT_FOUND'):
                        sys.stderr.write("\nMSG RELAY SERVICE: unknown message!\n\n")
                        
                    else:
                        txt_bytes = decrypt_message(msg_bytes, self.DH_shared_key)
                        txt = bson.loads(txt_bytes)  
                        content_from_other = txt['content']
                        signature_from_other = txt['signature']
                        cert_from_other = txt['user_cert']


                        cert = x509.load_pem_x509_certificate(cert_from_other)
                        RSA_public_key_from_other = cert.public_key()

                        try:
                            RSA_public_key_from_other.verify(
                            signature_from_other,
                            content_from_other.encode(),
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH
                            ),
                            hashes.SHA256()
                        )
                        except InvalidSignature:
                            sys.stderr.write("MSG RELAY SERVICE: verification error!")
                            return
                        except Exception as e:
                            sys.stderr.write("MSG RELAY SERVICE: verification error!")
                            return


                        sys.stdout.write(f"\nCONTENT: {content_from_other}\n\n")











            elif self.args.action == 'help':
                if len(self.args.args) > 0:
                    sys.stderr.write(string_ERRO)
                    writer.write(b'Erro ao processar comando: argumentos insuficientes/em demasia.')
                else:
                    uid = helper.extract_pseudonym_from_certificate(self.user_certeficado)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    helper.escrever_em_arquivo(f"{timestamp} - {uid} pediu os comandos")
                    print("""

    COMANDOS PERMITIDOS:
        - user <FNAME>: especifica o ficheiro com dados do utilizador.
        - send <UID> <SUBJECT>:  envia uma mensagem com assunto <SUBJECT> destinada ao utilizador com identificador <UID>.
        - askqueue: solicita ao servidor que lhe envie a lista de mensagens não lidas da queue do utilizador. 
        - getmsg <NUM>: solicita ao servidor o envio da mensagem da sua queue com número <NUM>.
        - help: imprime instruções de uso do programa.

                """)


        







    async def defineSharedKey(self, reader, writer):
        msg = await reader.read(max_msg_size)
        server_DH_public_key_bytes = serialization.load_pem_public_key(msg)
        data_to_send = server_DH_public_key_bytes.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ) + client_dh_public_key_bytes

        signature = self.private_key.sign(
            data_to_send,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        msg_to_send_to_server = {
            'client_dh_public_key' : client_dh_public_key_bytes,
            'signature_client' : signature,
            'user_cert' : self.user_certeficado.public_bytes(serialization.Encoding.PEM)
        }
        msg_to_send = bson.dumps(msg_to_send_to_server)
        writer.write(msg_to_send)
        await writer.drain()

        info_server = await reader.read(max_msg_size)

        txt = bson.loads(info_server) 
        signature_from_server = txt['signature_server']
        server_cert = txt['server_cert']

        cert = x509.load_pem_x509_certificate(server_cert)
        server_RSA_public_key = cert.public_key()
        try:
            server_RSA_public_key.verify(
            signature_from_server,
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

        server_DH_public_key = serialization.load_pem_public_key(msg)
        DH_shared_key = client_dh_private_key.exchange(server_DH_public_key)

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(DH_shared_key)

        self.DH_shared_key = derived_key











async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', conn_port)
    addr = writer.get_extra_info('peername')
    client = Client(addr)
    client.set_arguments()
    await client.defineSharedKey(reader, writer)
    await client.process(reader, writer)
    writer.close()


def run_client():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client())


run_client()