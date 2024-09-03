#ifndef SERVER_H
#define SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <errno.h>
#include <pwd.h>
#include <sys/ipc.h>
#include <sys/msg.h>

#include "msg.h"

#define PORT 8080
#define MAX_PENDING_CONNECTIONS 10
#define SIZE 100

typedef struct {
    int msquid; // Identificador da fila de mensagens
    char username[256]; // Nome de usuário
} ClientInfo;

ClientInfo UserQueueMap[SIZE];

int number_of_clients = 0;

int createDirectory(const char* username);

int removeDirectory(const char* username);

void sendMessageToQueue(int msqid, const char *message);

int findUserQueue(const char *username, ClientInfo *clientInfo, int mapSize);

void sendMessageToUserQueue(const char *username, const char *message, ClientInfo *clientInfo, int mapSize);

void* handleClient(void* arg);

#endif