def is_prime(n)
  return false if n < 2
  return true if n == 2
  return false if n.even?
  
  (3..Math.sqrt(n).to_i).step(2) do |i|
    return false if n % i == 0
  end
  true
end

n = 999998727
puts "#{n} is #{is_prime(n) ? 'prime' : 'not prime'}"