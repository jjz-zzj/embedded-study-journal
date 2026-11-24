#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
void print_frame(unsigned char* buf, int len);   /* 声明 */

int main(void)
{
    unsigned char frame[8] = { 0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A };
    int i = 0;

    printf("main 里 sizeof(frame) = %zu\n", sizeof(frame));
    print_frame(frame, 8);
    printf("回来后 frame[0] = %02X\n", (unsigned int)frame[0]);
    return 0;
}

void print_frame(unsigned char* buf, int len)   
{
    int i;
    printf("函数里 sizeof(frame)=%zu\n", sizeof(buf));/* 1. 打印 sizeof(buf)，和 main 那个数比一比 */
    for (i = 0; i < len; i++) { printf("函数里 frame[%d]=%02X\n", i, buf[i]); }/* 2. 用 len 控制循环，逐个 %02X 打印 buf[i] */
    buf[0] = 0xFF;/* 3. 写一句 buf[0] = 0xFF; —— 看看 main 那边会不会变 */
}
