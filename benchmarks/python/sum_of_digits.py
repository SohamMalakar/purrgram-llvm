def sum_digits(n):
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total

def sum_all_digits():
    total_sum = 0
    for i in range(1, 100000001):
        total_sum += sum_digits(i)
    print(f"Sum of all digits from 1 to 100,000,000: {total_sum}")

sum_all_digits()