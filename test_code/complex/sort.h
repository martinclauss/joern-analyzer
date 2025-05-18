#ifndef SORT_H
#define SORT_H

#include "list.h"

// Function declarations for different sorting algorithms
void bubble_sort(List* list);
void insertion_sort(List* list);
void selection_sort(List* list);
void quick_sort(List* list);

// Helper functions
void swap_nodes(Node* a, Node* b);
int is_sorted(List* list);

#endif // SORT_H 