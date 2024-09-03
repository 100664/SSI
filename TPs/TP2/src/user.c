#include "user.h"

void criarGroup (char* nomeGrupo, char* remetente){
    pid_t pid;
    int status;
    pid = fork();
    if (pid < 0) {
        perror("Erro ao criar processo filho");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        char* argv1[] = {"sudo", "groupadd", "-r", nomeGrupo, NULL};
        if (execvp("sudo", argv1) < 0) {
            perror("Erro ao executar groupadd");
            exit(EXIT_FAILURE);
        }
    } else {
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            if (WEXITSTATUS(status) == 0) {
                printf("Grupo %s criado com sucesso.\n", nomeGrupo);
                char* argv2[] = {"sudo", "usermod", "-a", "-G", nomeGrupo, remetente, NULL};
                if (execvp("sudo", argv2) < 0) {
                    perror("Erro ao executar usermod");
                    exit(EXIT_FAILURE);
                }
                printf ("sucesso a fazer usermod");
            } else {
                printf("Erro ao criar o grupo '%s'.\n", nomeGrupo);
            }
        } else {
            perror("Processo filho terminou inesperadamente");
            exit(EXIT_FAILURE);
        }
    }
}

void removerGroup(char* nomeGrupo) {
    pid_t pid;
    int status;
    pid = fork();
    if (pid < 0) {
        perror("Erro ao criar processo filho");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        // Remover o grupo como superusuário
        char* argv[] = {"sudo", "groupdel", nomeGrupo, NULL};
        if (execvp("sudo", argv) < 0) {
            perror("Erro ao executar groupdel");
            exit(EXIT_FAILURE);
        }
    } else {
        waitpid(pid, &status, 0);

        if (WIFEXITED(status)) {
            if (WEXITSTATUS(status) == 0) {
                printf("Grupo %s removido com sucesso.\n", nomeGrupo);
            } else {
                printf("Erro ao remover o grupo '%s'.\n", nomeGrupo);
            }
        } else {
            perror("Processo filho terminou inesperadamente");
            exit(EXIT_FAILURE);
        }
    }
}

void listarMembrosGrupo(char *nomeGrupo) {
    struct group *grp = getgrnam(nomeGrupo);
    if (grp == NULL) {
        fprintf(stderr, "Erro ao obter informações do grupo %s.\n", nomeGrupo);
        exit(EXIT_FAILURE);
    }
    printf("Membros do grupo '%s':\n", nomeGrupo);

    int c = 0;

    while (grp->gr_mem[c] != NULL) {
        printf("%s\n", grp->gr_mem[c]);
        c++;
    }
    if (c == 0) {
        printf("O grupo '%s' não possui membros.\n", nomeGrupo);
    }
}

void adicionarUsuarioGrupo(char *nomeGrupo, char *usuario) {
    pid_t pid;
    int status;
    pid = fork();
    if (pid < 0) {
        perror("Erro ao criar processo filho");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        char *argv[] = {"sudo", "usermod", "-a", "-G", nomeGrupo, usuario, NULL};
        if (execvp("sudo", argv) < 0) {
            perror("Erro ao executar usermod");
            exit(EXIT_FAILURE);
        }
    } else {
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            if (WEXITSTATUS(status) == 0) {
                printf("Usuário '%s' adicionado ao grupo '%s' com sucesso.\n", usuario, nomeGrupo);
            } else {
                printf("Erro ao adicionar o usuário '%s' ao grupo '%s'.\n", usuario, nomeGrupo);
            }
        } else {
            perror("Processo filho terminou inesperadamente");
            exit(EXIT_FAILURE);
        }
    }
}

void removerUsuarioGrupo(char *nomeGrupo, char *usuario) {
    pid_t pid;
    int status;
    pid = fork();
    if (pid < 0) {
        perror("Erro ao criar processo filho");
        exit(EXIT_FAILURE);
    } else if (pid == 0) {
        char *argv[] = {"sudo", "gpasswd", "-d", usuario, nomeGrupo, NULL};
        if (execvp("sudo", argv) < 0) {
            perror("Erro ao executar gpasswd");
            exit(EXIT_FAILURE);
        }
    } else {
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            if (WEXITSTATUS(status) == 0) {
                printf("Usuário '%s' removido do grupo '%s' com sucesso.\n", usuario, nomeGrupo);
            } else {
                printf("Erro ao remover o usuário '%s' do grupo '%s'.\n", usuario, nomeGrupo);
            }
        } else {
            perror("Processo filho terminou inesperadamente");
            exit(EXIT_FAILURE);
        }
    }
}

void startUserDaemon() {
    uid_t uid = getuid();
    struct passwd *pw = getpwuid(uid);
    const char *username = pw->pw_name;
    char daemon_command[1024];
    snprintf(daemon_command, sizeof(daemon_command), "%s %s", DAEMON_PATH, username);
    int ret = system(daemon_command);
    if (ret == -1) {
        perror("Erro ao iniciar o daemon");
        exit(EXIT_FAILURE);
    }
}


int main() {

    startUserDaemon();

    int client_socket_fd;
    struct sockaddr_in server_addr;

    if ((client_socket_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Erro ao criar socket");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("Endereço de IP inválido");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
#ifdef SO_REUSEPORT
    if (setsockopt(client_socket_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
#endif

    if (connect(client_socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Erro ao conectar ao servidor");
        exit(EXIT_FAILURE);
    }

    printf("Conectado ao servidor.\n");

    int msqid = initMessageQueue();

    struct passwd *pw = getpwuid(getuid());
    const char* userName = pw->pw_name;


    char* token;
    char message[1024];

    snprintf(message, sizeof(message), "action %s %d", userName, msqid);
    strcat(message, "\0");
    send (client_socket_fd, message, strlen(message), 0);

    while (1) {
        printf("Escreve que tipo de ação queres executar: ");
        fgets(message, sizeof(message), stdin);

        message[strcspn(message, "\n")] = '\0';

        if (strcmp(message, "concordia-ativar") == 0) {

            struct passwd *pw = getpwuid(getuid());
            const char* userName = pw->pw_name;
            snprintf(message, sizeof(message), "concordia-ativar %s", userName);
            strcat(message, "\0");
            send(client_socket_fd, message, strlen(message), 0);

        }else if (strcmp(message, "concordia-desativar") == 0) {

            struct passwd *pw = getpwuid(getuid());
            const char* userName = pw->pw_name;
            snprintf(message, sizeof(message), "concordia-desativar %s", userName);
            strcat(message, "\0");
            send(client_socket_fd, message, strlen(message), 0);

        }else if (strncmp(message, "concordia-grupo-criar", strlen("concordia-grupo-criar"))== 0){

            token = strtok(message, " ");
            token = strtok (NULL, " ");
            struct passwd *pw = getpwuid(getuid());
            char* name = pw->pw_name;
            criarGroup (token, name);

        }else if (strncmp(message, "concordia-grupo-remover", strlen("concordia-grupo-remover")) == 0){

            token = strtok (message, " ");
            token = strtok ( NULL, " ");
            removerGroup(token);

        }else if (strncmp(message, "concordia-grupo-listar", strlen("concordia-grupo-listar")) == 0){

            token = strtok (message, " ");
            token = strtok ( NULL, " ");
            listarMembrosGrupo(token);

        }else if (strncmp(message, "concordia-grupo-destinario-adicionar", strlen("concordia-grupo-destinario-adicionar")) == 0){

            token = strtok (message, " ");
            token = strtok ( NULL, " ");
            char* grupo = token;
            token = strtok ( NULL, " ");
            adicionarUsuarioGrupo(grupo, token);

        }else if (strncmp(message, "concordia-grupo-destinario-remover", strlen("concordia-grupo-destinario-remover")) == 0){

            token = strtok (message, " ");
            token = strtok ( NULL, " ");
            char* grupo = token;
            token = strtok ( NULL, " ");
            removerUsuarioGrupo(grupo, token);

        }else if (strcmp(message, "stop") == 0) {

            send(client_socket_fd, message, strlen(message), 0);
            //o daemon encerrará automaticamente pois está interligado com o user. Só preciso de me preocupar com a mensagem ser devidamente enviada para o servidor.
            break;

        }else {

            send(client_socket_fd, message, strlen(message), 0);

        }

        readFromMessageQueue(msqid);

    }

    msgctl(msqid, IPC_RMID, NULL);
    close(client_socket_fd);

    return 0;
}