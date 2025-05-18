#include "../../include/utils/logger.h"
#include <stdio.h>
#include <time.h>

void log_message(LogLevel level, const char* message) {
    time_t now;
    time(&now);
    char* timestamp = ctime(&now);
    timestamp[strlen(timestamp) - 1] = '\0';  // Remove newline

    const char* level_str;
    switch (level) {
        case LOG_INFO:
            level_str = "INFO";
            break;
        case LOG_WARNING:
            level_str = "WARNING";
            break;
        case LOG_ERROR:
            level_str = "ERROR";
            break;
        default:
            level_str = "UNKNOWN";
    }

    printf("[%s] [%s] %s\n", timestamp, level_str, message);
}

void log_operation(const char* operation, double result) {
    char message[256];
    snprintf(message, sizeof(message), "%s: %.2f", operation, result);
    log_message(LOG_INFO, message);
}

void log_error(const char* error_message) {
    log_message(LOG_ERROR, error_message);
} 