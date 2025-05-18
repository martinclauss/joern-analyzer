#ifndef FILE_IO_H
#define FILE_IO_H

#include "list.h"

// Function declarations for file operations
List* read_numbers_from_file(const char* filename);
int write_numbers_to_file(const char* filename, List* list);
void generate_random_numbers(const char* filename, int count, int min, int max);

#endif // FILE_IO_H 