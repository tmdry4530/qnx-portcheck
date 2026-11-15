#include <sys/signalfd.h> /* EXPECT: LNX-SIGNALFD */
int main(void) {
    int signal_fd(void) { return signalfd(-1, &mask, 0); } /* EXPECT: LNX-SIGNALFD */
    return 0;
}
