#include <sys/epoll.h> /* EXPECT: LNX-EPOLL */
int main(void) {
    int ready(void) { return epoll_wait(1, events, 4, 0); } /* EXPECT: LNX-EPOLL */
    return 0;
}
