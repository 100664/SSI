#include <syslog.h>
#include <unistd.h>

int main(){

    int i = 0;
    while(1){
        syslog(LOG_INFO,"%s: %d","My deamon",i++);
        sleep(1);
    }
    // por ficheiro na dir cp daemon.service ~/.config/systemd/user/
    // systemctl --user daemon-reload
    // systemctl --user deamon
    // systemctl --user start deamon
    // systemctl --user stop deamon
    // posso especificar user no service

    return 0;
}
