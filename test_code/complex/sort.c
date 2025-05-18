#include <stdio.h>
#include "sort.h"

void swap_nodes(Node* a, Node* b) {
    if (!a || !b) return;
    int temp = a->data;
    a->data = b->data;
    b->data = temp;
}

int is_sorted(List* list) {
    if (!list || !list->head) return 1;
    
    Node* current = list->head;
    while (current->next) {
        if (current->data > current->next->data) {
            return 0;
        }
        current = current->next;
    }
    return 1;
}

void bubble_sort(List* list) {
    if (!list || !list->head) return;
    
    int swapped;
    Node* current;
    Node* last = NULL;
    
    do {
        swapped = 0;
        current = list->head;
        
        while (current->next != last) {
            if (current->data > current->next->data) {
                swap_nodes(current, current->next);
                swapped = 1;
            }
            current = current->next;
        }
        last = current;
    } while (swapped);
}

void insertion_sort(List* list) {
    if (!list || !list->head) return;
    
    Node* current = list->head->next;
    while (current) {
        Node* key = current;
        Node* prev = list->head;
        
        while (prev != current && prev->data > key->data) {
            prev->next->data = prev->data;
            prev = prev->next;
        }
        prev->data = key->data;
        current = current->next;
    }
}

void selection_sort(List* list) {
    if (!list || !list->head) return;
    
    Node* current = list->head;
    while (current) {
        Node* min = current;
        Node* temp = current->next;
        
        while (temp) {
            if (temp->data < min->data) {
                min = temp;
            }
            temp = temp->next;
        }
        
        if (min != current) {
            swap_nodes(current, min);
        }
        current = current->next;
    }
}

// Helper function for quick sort
Node* partition(Node* low, Node* high) {
    int pivot = high->data;
    Node* i = low;
    
    for (Node* j = low; j != high; j = j->next) {
        if (j->data <= pivot) {
            swap_nodes(i, j);
            i = i->next;
        }
    }
    swap_nodes(i, high);
    return i;
}

// Helper function for quick sort
void quick_sort_recursive(Node* low, Node* high) {
    if (low && high && low != high && low->next != high) {
        Node* pivot = partition(low, high);
        quick_sort_recursive(low, pivot);
        quick_sort_recursive(pivot->next, high);
    }
}

void quick_sort(List* list) {
    if (!list || !list->head) return;
    
    // Find the last node
    Node* last = list->head;
    while (last->next) {
        last = last->next;
    }
    
    quick_sort_recursive(list->head, last);
} 