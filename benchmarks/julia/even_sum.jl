function sum_even_numbers()
    sum = 0
    for i in 0:2:1000000000
        sum += i
    end
    println("Sum of even numbers: $sum")
end

sum_even_numbers()