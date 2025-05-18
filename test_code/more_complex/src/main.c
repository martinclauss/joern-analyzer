#include "include/core/calculator.h"
#include <stdio.h>

int main() {
    // Create calculator instance
    Calculator* calc = calculator_create();
    if (!calc) {
        printf("Failed to create calculator\n");
        return 1;
    }

    // Perform some operations
    double result;

    // Addition
    result = calculator_perform_operation(calc, 10.5, 5.2, OP_ADD);
    printf("10.5 + 5.2 = %.2f\n", result);

    // Subtraction
    result = calculator_perform_operation(calc, 20.0, 7.5, OP_SUBTRACT);
    printf("20.0 - 7.5 = %.2f\n", result);

    // Multiplication
    result = calculator_perform_operation(calc, 4.0, 3.0, OP_MULTIPLY);
    printf("4.0 * 3.0 = %.2f\n", result);

    // Division
    result = calculator_perform_operation(calc, 15.0, 3.0, OP_DIVIDE);
    printf("15.0 / 3.0 = %.2f\n", result);

    // Try division by zero
    result = calculator_perform_operation(calc, 10.0, 0.0, OP_DIVIDE);
    printf("10.0 / 0.0 = %.2f\n", result);

    // Log calculator statistics
    calculator_log_stats(calc);

    // Clean up
    calculator_destroy(calc);
    return 0;
} 