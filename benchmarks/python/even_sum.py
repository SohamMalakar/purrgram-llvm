def sum_even_numbers():
    sum_val = 0
    for i in range(0, 1000000001, 2):
        sum_val += i
    print(f"Sum of even numbers: {sum_val}")

sum_even_numbers()