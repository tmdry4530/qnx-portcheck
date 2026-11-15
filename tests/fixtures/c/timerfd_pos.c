#include <sys/timerfd.h> /* EXPECT: LNX-TIMERFD */
int main(void) {
    int timer(void) { return timerfd_create(0, 0); } /* EXPECT: LNX-TIMERFD */
    return 0;
}
