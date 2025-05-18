#include <stdlib.h>
#include <stdio.h>
#include "list.h"

List* list_create(void) {
    List* list = (List*)malloc(sizeof(List));
    if (list) {
        list->head = NULL;
        list->size = 0;
    }
    return list;
}

void list_destroy(List* list) {
    if (!list) return;
    
    Node* current = list->head;
    while (current) {
        Node* next = current->next;
        free(current);
        current = next;
    }
    free(list);
}

void list_append(List* list, int data) {
    if (!list) return;
    
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return;
    
    new_node->data = data;
    new_node->next = NULL;
    
    if (!list->head) {
        list->head = new_node;
    } else {
        Node* current = list->head;
        while (current->next) {
            current = current->next;
        }
        current->next = new_node;
    }
    list->size++;
}

void list_prepend(List* list, int data) {
    if (!list) return;
    
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (!new_node) return;
    
    new_node->data = data;
    new_node->next = list->head;
    list->head = new_node;
    list->size++;
}

int list_remove(List* list, int data) {
    if (!list || !list->head) return 0;
    
    Node* current = list->head;
    Node* prev = NULL;
    
    while (current) {
        if (current->data == data) {
            if (prev) {
                prev->next = current->next;
            } else {
                list->head = current->next;
            }
            free(current);
            list->size--;
            return 1;
        }
        prev = current;
        current = current->next;
    }
    return 0;
}

int list_contains(List* list, int data) {
    if (!list) return 0;
    
    Node* current = list->head;
    while (current) {
        if (current->data == data) return 1;
        current = current->next;
    }
    return 0;
}

void list_print(List* list) {
    if (!list) return;
    
    printf("List contents: ");
    Node* current = list->head;
    while (current) {
        printf("%d ", current->data);
        current = current->next;
    }
    printf("\n");
}

size_t list_size(List* list) {
    return list ? list->size : 0;
}

Node* list_get_node(List* list, size_t index) {
    if (!list || index >= list->size) return NULL;
    
    Node* current = list->head;
    for (size_t i = 0; i < index; i++) {
        current = current->next;
    }
    return current;
} 