#include <stdio.h>

int main() {
    long long count = 0;
    for (long long i = 1; i <= 1000000000; i++) {
        if (i % 3 == 0 || i % 5 == 0) {
            count++;
        }
    }
    printf("Count of numbers divisible by 3 or 5: %lld\n", count);
    return 0;
}