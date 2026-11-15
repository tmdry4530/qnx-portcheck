#include <stdio.h>
int main(void) {
    int client(void) { return accept4(fd, 0, 0, 0); } /* EXPECT: LNX-ACCEPT4 */
    return 0;
}
