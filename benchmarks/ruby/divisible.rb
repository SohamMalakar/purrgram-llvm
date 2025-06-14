def count_divisible
  count = 0
  (1..1000000000).each do |i|
    count += 1 if i % 3 == 0 || i % 5 == 0
  end
  puts "Count of numbers divisible by 3 or 5: #{count}"
end

count_divisible