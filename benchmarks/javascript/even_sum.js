function sumEvenNumbers() {
    let sum = 0;
    for (let i = 0; i <= 1000000000; i += 2) {
        sum += i;
    }
    console.log(`Sum of even numbers: ${sum}`);
}

sumEvenNumbers();