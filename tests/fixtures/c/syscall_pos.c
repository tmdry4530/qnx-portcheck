#include <sys/syscall.h> /* EXPECT: LNX-SYSCALL */
int main(void) {
    long tid(void) { return syscall(SYS_gettid); } /* EXPECT: LNX-SYSCALL */
    return 0;
}
