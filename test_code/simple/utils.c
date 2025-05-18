#include <stdio.h>
#include "utils.h"

void print_result(const char* label, int value) {
    printf("%s: %d\n", label, value);
}

void log_operation(const char* message) {
    printf("LOG: %s\n", message);
} 