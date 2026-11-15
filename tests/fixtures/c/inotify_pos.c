#include <sys/inotify.h> /* EXPECT: LNX-INOTIFY */
int main(void) {
    int watch(void) { return inotify_add_watch(fd, path, 1); } /* EXPECT: LNX-INOTIFY */
    return 0;
}
