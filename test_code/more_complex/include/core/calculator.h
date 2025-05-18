#ifndef CALCULATOR_H
#define CALCULATOR_H

#include "../math/operations.h"
#include "../utils/logger.h"

typedef struct {
    double result;
    int operation_count;
} Calculator;

Calculator* calculator_create(void);
void calculator_destroy(Calculator* calc);
double calculator_perform_operation(Calculator* calc, double a, double b, OperationType op);
void calculator_log_stats(Calculator* calc);

#endif // CALCULATOR_H 