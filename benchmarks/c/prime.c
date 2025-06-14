#include <stdio.h>
#include <math.h>
#include <stdbool.h>

bool is_prime(long long n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    
    for (long long i = 3; i <= sqrt(n); i += 2) {
        if (n % i == 0) return false;
    }
    return true;
}

int main() {
    long long n = 999998727;
    printf("%lld is %s\n", n, is_prime(n) ? "prime" : "not prime");
    return 0;
}