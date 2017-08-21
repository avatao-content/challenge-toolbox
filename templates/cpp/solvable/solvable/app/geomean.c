#include <stdio.h>
#include <stdarg.h>
#include <math.h>

double geometric_mean(size_t count, ...) {
    va_list nums;
    double product = 1.0;

    va_start(nums, count);

    for(size_t i = 0; i < count; i++) {
        product *= va_arg(nums, double);
    }

    va_end(nums);
    return pow(product, 1.0/count);
}

int main(int argc, char const *argv[])
{
    printf("%f\n", geometric_mean(3, 1.0, 2.0, 3.0));
    return 0;
}