#ifndef PROJETO2_MSG_H
#define PROJETO2_MSG_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <errno.h>


#define MESSAGE_SIZE 1024

struct msgbuf {
    long mtype;
    char mtext[MESSAGE_SIZE];
};

int initMessageQueue();
void readFromMessageQueue(int msqid);

#endif //PROJETO2_MSG_H
