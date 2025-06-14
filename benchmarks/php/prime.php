<?php
function isPrime($n) {
    if ($n < 2) return false;
    if ($n == 2) return true;
    if ($n % 2 == 0) return false;
    
    for ($i = 3; $i <= sqrt($n); $i += 2) {
        if ($n % $i == 0) return false;
    }
    return true;
}

$n = 999998727;
echo "$n is " . (isPrime($n) ? "prime" : "not prime") . "\n";
?>