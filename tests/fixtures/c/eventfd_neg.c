#include <stdio.h>
int main(void) {
    int wake(void) { return my_eventfd(0, 0); }
    return 0;
}
