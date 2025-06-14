package main

import "fmt"

func sumDigits(n int64) int64 {
    var sum int64 = 0
    for n > 0 {
        sum += n % 10
        n /= 10
    }
    return sum
}

func main() {
    var totalSum int64 = 0
    for i := int64(1); i <= 100000000; i++ {
        totalSum += sumDigits(i)
    }
    fmt.Printf("Sum of all digits from 1 to 100,000,000: %d\n", totalSum)
}