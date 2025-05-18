#include "../../include/core/calculator.h"
#include <stdlib.h>

Calculator* calculator_create(void) {
    Calculator* calc = (Calculator*)malloc(sizeof(Calculator));
    if (calc) {
        calc->result = 0.0;
        calc->operation_count = 0;
    }
    return calc;
}

void calculator_destroy(Calculator* calc) {
    if (calc) {
        free(calc);
    }
}

double calculator_perform_operation(Calculator* calc, double a, double b, OperationType op) {
    if (!calc) {
        log_error("Invalid calculator instance");
        return 0.0;
    }

    double result = 0.0;
    switch (op) {
        case OP_ADD:
            result = add(a, b);
            break;
        case OP_SUBTRACT:
            result = subtract(a, b);
            break;
        case OP_MULTIPLY:
            result = multiply(a, b);
            break;
        case OP_DIVIDE:
            if (b != 0.0) {
                result = divide(a, b);
            } else {
                log_error("Division by zero");
                return 0.0;
            }
            break;
    }

    calc->result = result;
    calc->operation_count++;
    log_operation("Operation performed", result);
    return result;
}

void calculator_log_stats(Calculator* calc) {
    if (calc) {
        log_message(LOG_INFO, "Calculator Statistics:");
        log_operation("Total operations", calc->operation_count);
        log_operation("Last result", calc->result);
    }
} 