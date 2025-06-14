def fibonacci(n)
  return n if n <= 1
  fibonacci(n - 1) + fibonacci(n - 2)
end

puts "Fibonacci(35): #{fibonacci(35)}"