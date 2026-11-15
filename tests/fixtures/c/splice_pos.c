#include <stdio.h>
int main(void) {
    int move(void) { return splice(a, 0, b, 0, 4, 0); } /* EXPECT: LNX-SPLICE */
    ::splice(fd_in, 0, fd_out, 0, 4096, 0); /* EXPECT: LNX-SPLICE */
    return 0;
}
