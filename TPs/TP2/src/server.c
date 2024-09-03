#include "server.h"

int createDirectory (const char* username) {
    char path[1024];
    snprintf(path, sizeof(path), "/home/martimr/Desktop/lib/users/%s", username);
    if (mkdir(path, 0777) == -1) {
        if (errno == EEXIST) {
            //utilizar já existe
            return 2;
        } else {
            //erro ao criar
            return 0;
        }
    } else {
        //criado com sucesso
        return 1;
    }
}


int removeDirectory(const char* username) {
    char path[1024];
    snprintf(path, sizeof(path), "/home/martimr/Desktop/lib/users/%s", username);
    if (rmdir(path) == -1) {
        //erro ao remover
        return 0;
    } else {
        //removido com sucesso
        return 1;
    }
}

void sendMessageToQueue(int msqid, const char *message) {
    struct msgbuf msg;

    // Preencher a estrutura de mensagem
    msg.mtype = 1; // Tipo de mensagem (pode ser qualquer valor que você queira)
    strncpy(msg.mtext, message, sizeof(msg.mtext));

    // Enviar mensagem para a fila
    if (msgsnd(msqid, &msg, strlen(msg.mtext)+1, IPC_NOWAIT) == -1) {
        perror("Erro ao enviar mensagem para a fila de mensagens");
        exit(EXIT_FAILURE);
    }
}


// Função para encontrar o identificador da fila de mensagens de um usuário
int findUserQueue(const char *username, ClientInfo *clientInfo, int mapSize) {
    for (int i = 0; i < mapSize; i++) {
        if (strcmp(clientInfo[i].username, username) == 0) {
            return clientInfo[i].msquid;
        }
    }
    return -1; // Usuário não encontrado
}

// Função para enviar mensagem para a fila de mensagens do usuário correspondente
void sendMessageToUserQueue(const char *username, const char *message, ClientInfo* clientInfo, int mapSize) {
    int userQueue = findUserQueue(username, clientInfo, mapSize);
    if (userQueue == -1) {
        fprintf(stderr, "Erro: Usuário '%s' não encontrado.\n", username);
        return;
    }
    sendMessageToQueue(userQueue, message);
}

void* handleClient(void* arg) {
    int client_socket_fd = *((int*)arg);
    free(arg);

    char buffer[1024];
    char* token;
    while(1){
        ssize_t bytes_received = recv(client_socket_fd, buffer, sizeof(buffer), 0);
        if (bytes_received <= 0) {
            close(client_socket_fd);
            pthread_exit(NULL);
        }

        buffer[bytes_received] = '\0'; // Adicionar terminador de string
        //printf ("BUFFER: %s\n", buffer);

        // Analisar o comando recebido do cliente
        if (strncmp(buffer, "concordia-enviar", strlen("concordia-enviar")) == 0) {
            // Lógica para enviar mensagem
        } else if (strncmp(buffer, "concordia-listar", strlen("concordia-listar")) == 0) {
            // Lógica para listar mensagens
        } else if (strncmp(buffer, "concordia-ler", strlen("concordia-ler")) == 0) {
            // Lógica para ler mensagem
        } else if (strncmp(buffer, "concordia-responder", strlen("concordia-responder")) == 0) {
            // Lógica para responder a mensagem
        } else if (strncmp(buffer, "concordia-remover", strlen("concordia-remover")) == 0) {
            // Lógica para remover mensagem
        } else if (strncmp(buffer, "concordia-ativar", strlen("concordia-ativar")) == 0) {
            token = strtok(buffer, " ");
            token = strtok (NULL, " ");
            token = strtok (NULL, " ");
            int resposta = createDirectory(token);

            int userQueue = findUserQueue(token, UserQueueMap, number_of_clients);
            if (userQueue == -1) {
                fprintf(stderr, "Erro: Usuário '%s' não encontrado.\n", token);
            } else {
                char activation_message[1024];
                if (resposta == 1){
                    snprintf(activation_message, sizeof(activation_message), "Usuário %s ativado com sucesso.\n", token);
                    printf ("Usuário ativado com sucesso\n");
                }
                if (resposta == 2){
                    snprintf(activation_message, sizeof(activation_message), "Usuário %s já existe.\n", token);
                    printf ("Usuário já existe\n");
                }
                if (resposta == 0){
                    snprintf(activation_message, sizeof(activation_message), "ERRO ao criar o usuário %s.\n", token);
                    printf ("Erro ao criar o usuário\n");
                }
                sendMessageToQueue(userQueue, activation_message);
            }


        } else if (strncmp(buffer, "concordia-desativar", strlen("concordia-desativar")) == 0) {
            //printf ("BUFFER:%s\n", buffer);
            token = strtok(buffer, " ");
            token = strtok (NULL, " ");
            token = strtok (NULL, " ");
            int resposta = removeDirectory( token);

            int userQueue = findUserQueue(token, UserQueueMap, number_of_clients);
            if (userQueue == -1) {
                fprintf(stderr, "Erro: Usuário '%s' não encontrado.\n", token);
            } else {
                char activation_message[1024];
                if (resposta == 1){
                    snprintf(activation_message, sizeof(activation_message), "Usuário %s removido com sucesso.\n", token);
                    printf ("Usuário removido com sucesso\n");
                }
                if (resposta == 0){
                    snprintf(activation_message, sizeof(activation_message), "ERRO ao remover o usuário %s.\n", token);
                    printf ("Erro ao remover o usuário\n");
                }
                sendMessageToQueue(userQueue, activation_message);
            }
        }else if (strncmp(buffer, "action", strlen("action")) == 0){
            token = strtok(buffer, " ");
            token = strtok(NULL, " ");
            strncpy(UserQueueMap[number_of_clients].username, token, sizeof(UserQueueMap[number_of_clients].username) - 1);
            UserQueueMap[number_of_clients].username[sizeof(UserQueueMap[number_of_clients].username) - 1] = '\0'; // Adicionar terminador nulo

            token = strtok(NULL, " ");
            UserQueueMap[number_of_clients].msquid = atoi(token);

            number_of_clients++;
        } else {
            int userQueue = findUserQueue(token, UserQueueMap, number_of_clients);
            if (userQueue == -1) {
                fprintf(stderr, "Erro: Usuário '%s' não encontrado.\n", token);
            } else {
                char message[1024];
                snprintf(message, sizeof(message), "COMANDO INVÁLIDO.\n");
                sendMessageToQueue(userQueue, message);
            }
        }
    }

    close(client_socket_fd);
    pthread_exit(NULL);
}

int main() {
    int server_socket_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    if ((server_socket_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Erro ao criar socket");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
#ifdef SO_REUSEPORT
    if (setsockopt(server_socket_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
#endif

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Erro ao vincular socket");
        exit(EXIT_FAILURE);
    }

    if (listen(server_socket_fd, MAX_PENDING_CONNECTIONS) == -1) {
        perror("Erro ao iniciar escuta por conexões");
        exit(EXIT_FAILURE);
    }

    printf("Servidor aguarda conexões na porta %d...\n", PORT);

    while (1) {
        int* client_socket_fd = (int*)malloc(sizeof(int));
        *client_socket_fd = accept(server_socket_fd, (struct sockaddr*)&client_addr, &client_addr_len);
        if (*client_socket_fd == -1) {
            perror("Erro ao aceitar conexão");
            free(client_socket_fd);
            continue;
        }
        else{
            printf ("Conexão estabelecida\n");
        }

        pthread_t client_thread;
        if (pthread_create(&client_thread, NULL, handleClient, (void*)client_socket_fd) != 0) {
            perror("Erro ao criar thread para lidar com o cliente");
            close(*client_socket_fd);
            free(client_socket_fd);
            continue;
        }

        // Detach da thread para liberar recursos automaticamente
        pthread_detach(client_thread);
    }
    close(server_socket_fd);
    return 0;
}