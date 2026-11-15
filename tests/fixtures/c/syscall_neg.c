#include <stdio.h>
int main(void) {
    long tid(void) { return my_syscall("SYS_gettid"); }
    return 0;
}
