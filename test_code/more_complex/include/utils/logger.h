#ifndef LOGGER_H
#define LOGGER_H

typedef enum {
    LOG_INFO,
    LOG_WARNING,
    LOG_ERROR
} LogLevel;

void log_message(LogLevel level, const char* message);
void log_operation(const char* operation, double result);
void log_error(const char* error_message);

#endif // LOGGER_H 