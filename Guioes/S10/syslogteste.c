#include <syslog.h>

int main (){

    openlog("syslogteste",LOG_PID,LOG_USER);
    syslog(LOG_INFO,"%s","Hello world");
    closelog();


    return 0;
}
