#include <stdio.h>
int main(void) {
    int signal_fd(void) { return my_signalfd(-1, &mask, 0); }
    return 0;
}
