#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/inotify.h>
#include <unistd.h>

static int signal_write_fd = -1;

static void handle_signal(int signo)
{
    unsigned char value = (unsigned char)signo;
    if (signal_write_fd >= 0)
        (void)write(signal_write_fd, &value, sizeof(value));
}

static int install_signals(int pipefd[2])
{
    struct sigaction action;
    if (pipe(pipefd) < 0) return -1;
    signal_write_fd = pipefd[1];
    memset(&action, 0, sizeof(action));
    action.sa_handler = handle_signal;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGINT, &action, NULL) < 0 ||
        sigaction(SIGTERM, &action, NULL) < 0) return -1;
    return 0;
}

int main(int argc, char **argv)
{
    int notify_fd, epoll_fd, pipefd[2];
    struct epoll_event event, ready[8];
    char buffer[4096];
    int running = 1;
    if (argc != 2) {
        fprintf(stderr, "usage: %s DIRECTORY\n", argv[0]);
        return 2;
    }
    notify_fd = inotify_init1(IN_CLOEXEC);
    if (notify_fd < 0) { perror("inotify_init1"); return 1; }
    if (inotify_add_watch(notify_fd, argv[1], IN_CREATE | IN_DELETE |
                          IN_MODIFY | IN_MOVED_FROM | IN_MOVED_TO) < 0) {
        perror("inotify_add_watch"); close(notify_fd); return 1;
    }
    if (install_signals(pipefd) < 0) {
        perror("signal setup"); close(notify_fd); return 1;
    }
    epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) { perror("epoll_create1"); return 1; }
    memset(&event, 0, sizeof(event));
    event.events = EPOLLIN;
    event.data.fd = notify_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, notify_fd, &event) < 0) {
        perror("epoll_ctl inotify"); return 1;
    }
    event.data.fd = pipefd[0];
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, pipefd[0], &event) < 0) {
        perror("epoll_ctl signal pipe"); return 1;
    }
    puts("filewatchd: watching; Ctrl-C to stop");
    while (running) {
        int count = epoll_wait(epoll_fd, ready, 8, -1);
        if (count < 0) { if (errno == EINTR) continue; perror("epoll_wait"); break; }
        for (int i = 0; i < count; ++i) {
            if (ready[i].data.fd == pipefd[0]) {
                unsigned char sig;
                (void)read(pipefd[0], &sig, sizeof(sig));
                running = 0;
            } else {
                ssize_t length = read(notify_fd, buffer, sizeof(buffer));
                if (length < 0) { if (errno != EINTR) perror("inotify read"); continue; }
                for (char *cursor = buffer; cursor < buffer + length; ) {
                    struct inotify_event *ev = (struct inotify_event *)cursor;
                    printf("event mask=0x%x name=%s\n", ev->mask,
                           ev->len ? ev->name : "(directory)");
                    cursor += sizeof(*ev) + ev->len;
                }
                fflush(stdout);
            }
        }
    }
    close(epoll_fd); close(pipefd[0]); close(pipefd[1]); close(notify_fd);
    puts("filewatchd: stopped");
    return 0;
}
