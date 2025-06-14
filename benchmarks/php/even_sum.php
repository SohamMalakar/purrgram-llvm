<?php
function sumEvenNumbers() {
    $sum = 0;
    for ($i = 0; $i <= 1000000000; $i += 2) {
        $sum += $i;
    }
    echo "Sum of even numbers: $sum\n";
}

sumEvenNumbers();
?>