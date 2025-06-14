function count_divisible()
    count = 0
    for i in 1:1000000000
        if i % 3 == 0 || i % 5 == 0
            count += 1
        end
    end
    println("Count of numbers divisible by 3 or 5: $count")
end

count_divisible()