#include <sys/prctl.h> /* EXPECT: LNX-PRCTL */
int main(void) {
    int name(void) { return prctl(PR_SET_NAME, "worker"); } /* EXPECT: LNX-PRCTL */
    return 0;
}
