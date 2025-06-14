package main

import "fmt"

func main() {
    var sum int64 = 0
    for i := int64(0); i <= 1000000000; i += 2 {
        sum += i
    }
    fmt.Printf("Sum of even numbers: %d\n", sum)
}