#include <stdio.h>
int main(void) {
    #ifdef __linux__ /* EXPECT: LNX-LINUX-IFDEF */
    return 0;
}
