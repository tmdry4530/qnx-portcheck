#include <stdio.h>
int main(void) {
    int pipes(void) { return pipe2(pair, O_CLOEXEC); } /* EXPECT: LNX-PIPE2 */
    return 0;
}
