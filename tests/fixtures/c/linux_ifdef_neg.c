#include <stdio.h>
int main(void) {
     #if defined(__linux__) || defined(__QNX__)
    return 0;
}
