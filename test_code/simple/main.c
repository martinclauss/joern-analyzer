#include <stdio.h>
#include "utils.h"
#include "math_ops.h"

int main() {
    int a = 10;
    int b = 5;
    
    // Call functions from different files
    int sum = add(a, b);
    int diff = subtract(a, b);
    
    // Use utility function
    print_result("Sum", sum);
    print_result("Difference", diff);
    
    // Call a function that calls another function
    process_numbers(a, b);
    
    return 0;
} 