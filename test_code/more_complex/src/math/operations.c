#include "../../include/math/operations.h"
#include "../utils/logger.c"

double add(double a, double b) {
    double result = a + b;
    log_operation("Addition", result);
    return result;
}

double subtract(double a, double b) {
    double result = a - b;
    log_operation("Subtraction", result);
    return result;
}

double multiply(double a, double b) {
    double result = a * b;
    log_operation("Multiplication", result);
    return result;
}

double divide(double a, double b) {
    if (b == 0.0) {
        log_error("Division by zero attempted");
        return 0.0;
    }
    double result = a / b;
    log_operation("Division", result);
    return result;
} 