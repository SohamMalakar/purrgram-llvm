<?php
function countDivisible() {
    $count = 0;
    for ($i = 1; $i <= 1000000000; $i++) {
        if ($i % 3 == 0 || $i % 5 == 0) {
            $count++;
        }
    }
    echo "Count of numbers divisible by 3 or 5: $count\n";
}

countDivisible();
?>