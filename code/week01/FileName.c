#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
int main(void)
{
	int num = 0, sum = 0;
	do
	{
		num = num + 1;
		sum = sum + num;
	} while (num < 100);
	printf("累加结果为：%d", sum);
	return 0;
}


