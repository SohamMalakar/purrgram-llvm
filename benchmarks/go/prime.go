package main

import (
    "fmt"
    "math"
)

func isPrime(n int64) bool {
    if n < 2 {
        return false
    }
    if n == 2 {
        return true
    }
    if n%2 == 0 {
        return false
    }
    
    for i := int64(3); i <= int64(math.Sqrt(float64(n))); i += 2 {
        if n%i == 0 {
            return false
        }
    }
    return true
}

func main() {
    n := int64(999998727)
    result := "not prime"
    if isPrime(n) {
        result = "prime"
    }
    fmt.Printf("%d is %s\n", n, result)
}