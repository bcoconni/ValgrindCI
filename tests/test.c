#include <stdlib.h>
#include <stdio.h>

int main(void)
{
    int *allocated_memory = malloc(10);
    unsigned int unitialized_var;

    if (unitialized_var != 0)
        printf("The variable is non zero by chance.\n");

    return 0;
}