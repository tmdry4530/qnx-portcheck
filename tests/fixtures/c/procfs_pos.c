#include <stdio.h>
int main(void) {
    const char *path = "/proc/self/exe"; /* EXPECT: LNX-PROCFS */
    return 0;
}
