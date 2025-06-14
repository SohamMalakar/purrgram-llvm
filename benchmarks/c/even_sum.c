#include <stdio.h>

int main() {
    long long sum = 0;
    for (long long i = 0; i <= 1000000000; i += 2) {
        sum += i;
    }
    printf("Sum of even numbers: %lld\n", sum);
    return 0;
}