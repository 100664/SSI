#ifndef USER_H
#define USER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pwd.h>
#include <sys/wait.h>
#include <grp.h>

#define PORT 8080
#define SERVER_IP "127.0.0.1"
#define DAEMON_PATH "/home/martimr/Desktop/SSI/Projeto2/bin/user"

#include "msg.h"

void criarGroup (char* nomeGrupo, char* remetente);

void removerGroup(char* nomeGrupo);

void listarMembrosGrupo(char *nomeGrupo);

void adicionarUsuarioGrupo(char *nomeGrupo, char *usuario);

void removerUsuarioGrupo(char *nomeGrupo, char *usuario);

void startUserDaemon();

#endif