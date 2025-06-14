def sum_digits(n)
  sum = 0
  while n > 0
    sum += n % 10
    n /= 10
  end
  sum
end

def sum_all_digits
  total_sum = 0
  (1..100000000).each do |i|
    total_sum += sum_digits(i)
  end
  puts "Sum of all digits from 1 to 100,000,000: #{total_sum}"
end

sum_all_digits