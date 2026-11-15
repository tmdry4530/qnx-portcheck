#include <sys/sendfile.h> /* EXPECT: LNX-SENDFILE */
int main(void) {
    int copy(void) { return sendfile(out, in, 0, 16); } /* EXPECT: LNX-SENDFILE */
    return 0;
}
