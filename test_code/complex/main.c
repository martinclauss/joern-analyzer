#include <stdio.h>
#include <stdlib.h>
#include "list.h"
#include "sort.h"
#include "file_io.h"

void test_list_operations(List* list) {
    printf("\nTesting list operations:\n");
    printf("Initial list size: %zu\n", list_size(list));
    
    // Test append
    list_append(list, 42);
    list_append(list, 17);
    list_append(list, 99);
    printf("After appending 3 numbers:\n");
    list_print(list);
    
    // Test prepend
    list_prepend(list, 5);
    printf("After prepending 5:\n");
    list_print(list);
    
    // Test contains
    printf("List contains 17: %d\n", list_contains(list, 17));
    printf("List contains 100: %d\n", list_contains(list, 100));
    
    // Test remove
    list_remove(list, 17);
    printf("After removing 17:\n");
    list_print(list);
}

void test_sorting_algorithms(List* list) {
    printf("\nTesting sorting algorithms:\n");
    
    // Test bubble sort
    printf("Before bubble sort:\n");
    list_print(list);
    bubble_sort(list);
    printf("After bubble sort:\n");
    list_print(list);
    
    // Shuffle the list
    list_remove(list, 5);
    list_remove(list, 42);
    list_remove(list, 99);
    list_append(list, 99);
    list_append(list, 5);
    list_append(list, 42);
    
    // Test insertion sort
    printf("\nBefore insertion sort:\n");
    list_print(list);
    insertion_sort(list);
    printf("After insertion sort:\n");
    list_print(list);
    
    // Shuffle again
    list_remove(list, 5);
    list_remove(list, 42);
    list_remove(list, 99);
    list_append(list, 42);
    list_append(list, 99);
    list_append(list, 5);
    
    // Test selection sort
    printf("\nBefore selection sort:\n");
    list_print(list);
    selection_sort(list);
    printf("After selection sort:\n");
    list_print(list);
    
    // Shuffle one more time
    list_remove(list, 5);
    list_remove(list, 42);
    list_remove(list, 99);
    list_append(list, 99);
    list_append(list, 5);
    list_append(list, 42);
    
    // Test quick sort
    printf("\nBefore quick sort:\n");
    list_print(list);
    quick_sort(list);
    printf("After quick sort:\n");
    list_print(list);
}

void test_file_operations(void) {
    printf("\nTesting file operations:\n");
    
    // Generate random numbers
    const char* input_file = "numbers.txt";
    const char* output_file = "sorted_numbers.txt";
    
    printf("Generating random numbers...\n");
    generate_random_numbers(input_file, 10, 1, 100);
    
    // Read numbers from file
    printf("Reading numbers from file...\n");
    List* list = read_numbers_from_file(input_file);
    if (!list) {
        printf("Error reading numbers from file\n");
        return;
    }
    
    printf("Numbers read from file:\n");
    list_print(list);
    
    // Sort the numbers
    printf("\nSorting numbers...\n");
    quick_sort(list);
    
    // Write sorted numbers to file
    printf("Writing sorted numbers to file...\n");
    if (write_numbers_to_file(output_file, list)) {
        printf("Sorted numbers written to %s\n", output_file);
    } else {
        printf("Error writing sorted numbers to file\n");
    }
    
    list_destroy(list);
}

int main(void) {
    // Create a new list
    List* list = list_create();
    if (!list) {
        printf("Error creating list\n");
        return 1;
    }
    
    // Test list operations
    test_list_operations(list);
    
    // Test sorting algorithms
    test_sorting_algorithms(list);
    
    // Clean up the list
    list_destroy(list);
    
    // Test file operations
    test_file_operations();
    
    return 0;
} 