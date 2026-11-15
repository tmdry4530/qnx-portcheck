#include <stdio.h>
int main(void) {
    int ready(void) { return my_epoll_wait(1, events, 4, 0); }
    return 0;
}
