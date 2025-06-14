<?php
function sumDigits($n) {
    $sum = 0;
    while ($n > 0) {
        $sum += $n % 10;
        $n = intval($n / 10);
    }
    return $sum;
}

function sumAllDigits() {
    $totalSum = 0;
    for ($i = 1; $i <= 100000000; $i++) {
        $totalSum += sumDigits($i);
    }
    echo "Sum of all digits from 1 to 100,000,000: $totalSum\n";
}

sumAllDigits();
?>