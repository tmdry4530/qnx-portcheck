#include <sys/sysinfo.h> /* EXPECT: LNX-SYSINFO */
int main(void) {
    int info(void) { return sysinfo(&data); } /* EXPECT: LNX-SYSINFO */
    return 0;
}
