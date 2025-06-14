def sum_even_numbers
  sum = 0
  (0..1000000000).step(2) do |i|
    sum += i
  end
  puts "Sum of even numbers: #{sum}"
end

sum_even_numbers