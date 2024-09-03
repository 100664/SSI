#include "msg.h"

// Função para inicializar a fila de mensagens
int initMessageQueue() {
    key_t key = ftok("/tmp", 'A');
    if (key == -1) {
        perror("Erro ao gerar chave para a fila de mensagens");
        exit(EXIT_FAILURE);
    }

    int msqid = msgget(key, IPC_CREAT | 0666);
    if (msqid == -1) {
        perror("Erro ao criar a fila de mensagens");
        exit(EXIT_FAILURE);
    }

    return msqid;
}

void readFromMessageQueue(int msqid) {
    struct msgbuf message;

    size_t message_size = sizeof(message) - sizeof(long);

    if (msgrcv(msqid, &message, message_size, 0, IPC_NOWAIT) == -1) {
        if (errno == ENOMSG) {
            return;
        }
        perror("Erro ao receber mensagem da fila de mensagens");
        exit(EXIT_FAILURE);
    }

    printf("Mensagem recebida da fila de mensagens: %s", message.mtext);
}
