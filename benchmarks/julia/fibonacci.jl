function fibonacci(n)
    if n <= 1
        return n
    end
    return fibonacci(n - 1) + fibonacci(n - 2)
end

println("Fibonacci(35): $(fibonacci(35))")