#ifndef LIST_H
#define LIST_H

#include <stddef.h>

// Node structure for the linked list
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// List structure
typedef struct {
    Node* head;
    size_t size;
} List;

// Function declarations
List* list_create(void);
void list_destroy(List* list);
void list_append(List* list, int data);
void list_prepend(List* list, int data);
int list_remove(List* list, int data);
int list_contains(List* list, int data);
void list_print(List* list);
size_t list_size(List* list);
Node* list_get_node(List* list, size_t index);

#endif // LIST_H 