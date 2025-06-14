package main

import "fmt"

func main() {
    var count int64 = 0
    for i := int64(1); i <= 1000000000; i++ {
        if i%3 == 0 || i%5 == 0 {
            count++
        }
    }
    fmt.Printf("Count of numbers divisible by 3 or 5: %d\n", count)
}