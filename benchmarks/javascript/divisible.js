function countDivisible() {
    let count = 0;
    for (let i = 1; i <= 1000000000; i++) {
        if (i % 3 === 0 || i % 5 === 0) {
            count++;
        }
    }
    console.log(`Count of numbers divisible by 3 or 5: ${count}`);
}

countDivisible();