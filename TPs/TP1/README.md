<img src='uminho.png' width="30%">

# Serviço de *Message Replay* com Criptografia Aplicada

### Colaboradores

Nome                           |  Número
------------------------------ | --------
Jéssica Cristina Lima da Cunha | A100901
Martim José Amaro Redondo      | A100664
Tiago Azevedo Campos Moreira   | A100549


## Introdução

Este projeto consiste na criação de um serviço de *Message Replay* para facilitar a comunicação entre membros de uma organização. Será imprementado um servidor (`msg_server.py`) para gerir as solicitações dos utilizadores e um cliente, `msg_client.py`, para acesso às funcionalidades.

Os utilizadores interagem com o sistema através do cliente, enciando mensagens, solicitando mensagens na fila, recuperando mensagens específicas e obtendo ajuda sobre o uso do programa. A autenticidade e segurança das comunicações serão garantidas, utilizando certificados X.509 para identificação dos utilizadores.

## Geração da Chave de Diffie-Hellman

Tanto no cliente como no servidor escolhemos um valor de `p` e `g` aleatórios a partir disto, tal como feito no guião 6 vamos gerar a `server_dh_private_key` e a partir desta a `server_dh_public_key`, o mesmo é feito do lado do cliente onde vão ser geradas, também, a chave privada e pública de Diffie-Hellman à qual chamamos `client_dh_private_key` e `client_dh_public_key`, respetivamente.

## Geração da Derived Key

A primeira etapa para o Cliente é estabelecer a comunicação com o servidor, que decidimos alojar no IP: 127.0.0.1. Depois, o processo de negociação da chave compartilhada, ou `derived key`, com o servidor é iniciado. O processo começa com o servidor enviando sua `server_dh_public_key` para o cliente. Por sua vez, o cliente recebe essa chave e cria uma mensagem concatenando a `server_dh_public_key` recebida com a sua própria chave `client_dh_public_key`. Decidimos usar o RSA em conjunto com o DH para reforçar a segurança. Dessa forma, a mensagem é assinada e encapsulada em BSON com a `client_dh_public_key`, juntamente com a mensagem assinada (`client_signature`) e o certificado do usuário obtido no momento da conexão por meio do arquivo .p12, `user_cert`.


Durante a conexão, o servidor armazena esses dados e verifica se o cliente permanece íntegro, assegurando que ele esteja se comunicando com o Cliente inicial. A verificação é feita através da combinação da chave pública RSA extraída do `user_cert` com a `server_dh_public_key` e `client_dh_public_key` recém-recebidas. Isso permite reconstruir a mensagem assinada pelo cliente sem a assinatura. Dessa forma, o servidor valida a identidade do cliente.


Depois de validar isso, o servidor pode criar sua própria chave compartilhada para estabelecer comunicação segura com o cliente. A mesma operação é feita de forma similar pelo cliente, o qual envia sua `client_signature` e o `server_cert`, possibilitando ao servidor verificar a identidade do cliente. Após a autenticação do servidor ser confirmada, o cliente gera sua chave compartilhada.


Depois de estabelecida a DH_shared_key, a conexão entre o Cliente e o Servidor fica segura e confiável.

## Cliente

A partir daqui, assumimos que a conexão foi estabelecida com êxito. 

Começamos por inicializar os parâmetros do Cliente usando as informações fornecidas através de input. Usamos a biblioteca argparse para trabalhar com o standart input. Depois de obter e armazenar todas as informações iniciais, que podem ser extraídas do arquivo .p12, o Cliente passa para a etapa de processamento das ações solicitadas pelo usuário.Existem quatro ações possíveis:

 -> send: Para realizar esta ação, o processo é o seguinte: capturamos primeiro as informações do usuário através da entrada padrão e depois utilizamos o `user_cert` para extrair o `PSEUDÔNIMO`. Depois, construímos uma mensagem com os parâmetros desejados e a enviamos para o servidor usando o formato BSON. O servidor devolve esta mensagem ao cliente para assegurar a entrega segura da mesma.

 -> askqueue: Nesta ação, não é necessário que o usuário insira dados, mas temos que recuperar o `PSEUDÔNIMO`. A mensagem a ser enviada para o servidor é criada em seguida, que processa a mensagem e envia de volta ao Cliente a lista de todas as mensagens desse remetente. Para evitar problemas de sobrecarga, as mensagens são enviadas individualmente. Após processar cada mensagem, o Cliente envia um sinal ao servidor para solicitar a próxima mensagem da fila. Assim que todas as mensagens forem processadas, o servidor envia uma flag para sinalizar ao cliente que a lista de mensagens foi recebida completamente. As mensagens são impressas à medida que são processadas no Cliente.

 -> getmsg: Para iniciar esta ação, capturamos tanto as informações do usuário quanto o `PSEUDÔNIMO` via standart input. Depois, enviamos uma mensagem ao servidor com essas informações após criá-la. O servidor examina a mensagem e envia de volta a resposta correspondente para o Cliente. Caso a mensagem não seja encontrada, uma mensagem de erro será impressa na standart error. Se não, o Cliente verifica se o remetente é válido e, em caso afirmativo, imprime a mensagem na standart output. Se não for possível verificar o remetente, uma mensagem de erro será mostrada.

-> help: Apenas exibimos no terminal o conjunto de comandos necessários para executar qualquer uma das tarefas acima mencionadas nesta ação.

## Servidor

Vamos presumir, assim como no Cliente, que a conexão foi estabelecida com êxito. É importante mencionar os três dicionários presentes neste arquivo. Um deles armazena as mensagens não lidas, outro guarda os índices das mensagens e o terceiro armazena as mensagens já lidas. Todos os três dicionários são segmentados por Cliente, ou seja, cada Cliente tem uma seção única dentro do dicionário.

O servidor determina a ação a ser executada com base na mensagem recebida do Cliente contendo a `flag` correspondente à ação. Sabemos que existem 4 ações possíveis, no entanto, apenas 3 delas envolvem comunicação com o servidor, pois a ação help não requer interação com o servidor. Além disso, o servidor executa ações diferentes dependendo do tipo de ação. Se a ação for:

 -> send: Primeiramente, o servidor verifica a estrutura da mensagem. Se estiver correta, prossegue extraindo todas as informações da mensagem do Cliente e cria uma nova variável de `timestamp`. Em seguida, verifica se o `uid_receiver` já está no dicionário de IDs; se estiver, incrementa o índice desse `uid_receiver` em 1, caso contrário, cria uma nova seção no dicionário para esse Cliente. A mensagem é então criada com todas as informações e armazenada na fila de mensagens. Antes de concluir a ação, o servidor envia uma mensagem assinada para o `uid_sender` com a mensagem recebida, permitindo que o Cliente saiba que a mensagem foi recebida corretamente pelo servidor adequado.

 -> askqueue: Assim como no send, o servidor verifica a estrutura da mensagem. Se estiver correta, as informações da mensagem são extraídas e o servidor simplesmente acessa o dicionário dda queue para recuperar todas as mensagens do Cliente em questão e enviá-las uma por uma. Uma variável de controle é utilizada para que o Cliente decida quando deseja receber a próxima mensagem. Quando não houver mais mensagens, uma flag é enviada para que o Cliente saiba que já recebeu toda a fila de mensagens.

 -> getmsg: Primeiramente, o servidor verifica se a estrutura da mensagem está correta. Se estiver, as informações da mensagem são extraídas. Existem três cenários possíveis: primeiro, quando a mensagem já foi lida e está na fila de mensagens lidas; segundo, quando a mensagem está na queue normal, nesse caso, a mensagem é removida desse dicionário e movida para a queue de mensagens lidas; e por último, quando a mensagem não é encontrada em nenhum dos dicionários.

 ## Extras

Realizamos três aprimoramentos de forma abrangente. O primeiro consistiu na implementação de um sistema de LOG, no qual qualquer ação envolvendo o servidor seria registrada em um arquivo denominado `log`. Além disso, adotamos o formato BSON para facilitar a troca de mensagens entre o Servidor e o Cliente, como discutido durante a explicação do funcionamento do Cliente e do Servidor. Por fim, implementamos o recurso de recibo. O recibo em nossa concepção permite que o Cliente tenha a certeza de que o Servidor correto recebeu a mensagem com sucesso. Isso é alcançado fazendo com que o Servidor assine a mensagem recebida do Cliente e a devolva para que o Cliente possa verificar e confirmar que tudo transcorreu conforme o esperado.

## Conclusão

Em nossa opinião, o trabalho realizado atingiu um nível satisfatório, mas enfrentamos um desafio persistente em nosso código que resistiu a longas horas de discussões e tentativas de resolução. Depois de considerar cuidadosamente, chegamos à conclusão de que lidar com o erro para contorná-lo em alguns casos seria a melhor abordagem, mesmo que isso implicasse na perda parcial da integridade do trabalho. O problema está relacionado à inconsistência do processo de decodificação no cliente, que não opera de forma consistente em todas as situações, mesmo sob o mesmo comando, e ainda não identificamos a causa raiz. Reconhecemos que algumas partes do código são mais suscetíveis a erros do que outras, por isso optamos por não usar criptografia/descriptografia em certas seções para garantir uma apresentação mais estável. Por outro lado, tentamos reduzir esse problema através da introdução de outros elementos em nosso trabalho, como a adoção do BSON, um sistema de log e a criação de recibos.
