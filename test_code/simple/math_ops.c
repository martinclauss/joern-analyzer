#include <stdio.h>
#include "math_ops.h"
#include "utils.h"

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

void process_numbers(int a, int b) {
    int result = add(a, b);
    print_result("Processed", result);
    
    // Call another function from utils
    log_operation("Processing complete");
} 