function sum_digits(n)
    sum = 0
    while n > 0
        sum += n % 10
        n ÷= 10
    end
    return sum
end

function sum_all_digits()
    total_sum = 0
    for i in 1:100000000
        total_sum += sum_digits(i)
    end
    println("Sum of all digits from 1 to 100,000,000: $total_sum")
end

sum_all_digits()