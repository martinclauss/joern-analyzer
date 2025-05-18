#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "file_io.h"

List* read_numbers_from_file(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("Error opening file %s for reading\n", filename);
        return NULL;
    }
    
    List* list = list_create();
    if (!list) {
        fclose(file);
        return NULL;
    }
    
    int number;
    while (fscanf(file, "%d", &number) == 1) {
        list_append(list, number);
    }
    
    fclose(file);
    return list;
}

int write_numbers_to_file(const char* filename, List* list) {
    if (!list) return 0;
    
    FILE* file = fopen(filename, "w");
    if (!file) {
        printf("Error opening file %s for writing\n", filename);
        return 0;
    }
    
    Node* current = list->head;
    while (current) {
        fprintf(file, "%d\n", current->data);
        current = current->next;
    }
    
    fclose(file);
    return 1;
}

void generate_random_numbers(const char* filename, int count, int min, int max) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        printf("Error opening file %s for writing\n", filename);
        return;
    }
    
    srand(time(NULL));
    for (int i = 0; i < count; i++) {
        int number = min + rand() % (max - min + 1);
        fprintf(file, "%d\n", number);
    }
    
    fclose(file);
} 