#include <stdio.h>
int main(void) {
    int name(void) { return my_prctl(PR_SET_NAME, "worker"); }
    return 0;
}
