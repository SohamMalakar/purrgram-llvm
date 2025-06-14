function sumDigits(n) {
    let sum = 0;
    while (n > 0) {
        sum += n % 10;
        n = Math.floor(n / 10);
    }
    return sum;
}

function sumAllDigits() {
    let totalSum = 0;
    for (let i = 1; i <= 100000000; i++) {
        totalSum += sumDigits(i);
    }
    console.log(`Sum of all digits from 1 to 100,000,000: ${totalSum}`);
}

sumAllDigits();