#include <stdio.h>
int main(void) {
    int timer(void) { return my_timerfd_create(0, 0); }
    return 0;
}
