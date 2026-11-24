#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
void count_calls(void);

int main(void)
{
    count_calls(); count_calls(); count_calls();
    return 0;
}

void count_calls(void)
{
    int a = 0;
    static int b = 0;
    a++; b++; printf("a=%d,b=%d\n", a, b);
}
