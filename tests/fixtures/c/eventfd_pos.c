#include <sys/eventfd.h> /* EXPECT: LNX-EVENTFD */
int main(void) {
    int wake(void) { return eventfd(0, 0); } /* EXPECT: LNX-EVENTFD */
    return 0;
}
