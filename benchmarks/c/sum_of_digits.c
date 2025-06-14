#include <stdio.h>

int sum_digits(long long n) {
    int sum = 0;
    while (n > 0) {
        sum += n % 10;
        n /= 10;
    }
    return sum;
}

int main() {
    long long total_sum = 0;
    for (long long i = 1; i <= 100000000; i++) {
        total_sum += sum_digits(i);
    }
    printf("Sum of all digits from 1 to 100,000,000: %lld\n", total_sum);
    return 0;
}