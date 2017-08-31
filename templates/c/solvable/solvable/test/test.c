#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include <string.h>
#include <limits.h>

int *get_randomized(const char *text_p, unsigned *count, int *sum);

int comp(const void * elem1, const void * elem2){
    int f = *((int*)elem1);
    int s = *((int*)elem2);
    if (f > s) return  1;
    if (f < s) return -1;
    return 0;
}

static void test_normal(void **state)
{
    int *res;
    unsigned count;
    int sum;
    int expected[] = {1, 2, 3};

    res = get_randomized("1 2 3", &count, &sum);
	assert_int_equal(count, 3);
	assert_int_equal(sum, 6);
	qsort(res, count, sizeof(int), comp);
	assert_memory_equal(res, expected, sizeof(int) * count);
    free(res);
}

static void test_negative(void **state)
{
    int *res;
    unsigned count;
    int sum;
    int expected[] = {-2, -1, 3, 4};

    res = get_randomized("-1 -2 3 4", &count, &sum);
	assert_int_equal(count, 4);
	assert_int_equal(sum, 4);
	qsort(res, count, sizeof(int), comp);
	assert_memory_equal(res, expected, sizeof(int) * count);
    free(res);
}


static void test_skip_overflowing_num(void **state)
{
    int *res;
    unsigned count;
    int sum;
    int expected[] = {-2, -1, 3, 4};

    res = get_randomized("-1 -2 3 2147483648 4", &count, &sum);
	assert_int_equal(count, 4);
	assert_int_equal(sum, 4);
	qsort(res, count, sizeof(int), comp);
	assert_memory_equal(res, expected, sizeof(int) * count);
    free(res);
}

static void test_skip_underflowing_num(void **state)
{
    int *res;
    unsigned count;
    int sum;
    int expected[] = {-2, -1, 3, 4};

    res = get_randomized("-1 -2 3 -2147483649 4", &count, &sum);
	assert_int_equal(count, 4);
	assert_int_equal(sum, 4);
	qsort(res, count, sizeof(int), comp);
	assert_memory_equal(res, expected, sizeof(int) * count);
    free(res);
}

static void test_randomness(void **state)
{
    int *res1,*res2,*res3;
    unsigned count;
    int sum;

    res1 = get_randomized("1 2 3 4 5 6 7 8 9 10", &count, &sum);
    res2 = get_randomized("1 2 3 4 5 6 7 8 9 10", &count, &sum);
    res3 = get_randomized("1 2 3 4 5 6 7 8 9 10", &count, &sum);
    assert_int_equal(count, 10);
    assert_int_equal(sum, 55);

	assert_true(
		(memcmp(res1, res2, sizeof(int) * count) != 0) ||
    	(memcmp(res1, res3, sizeof(int) * count) != 0) ||
    	(memcmp(res2, res3, sizeof(int) * count) != 0)
	);
    free(res1);
    free(res2);
    free(res3);
}

static void test_normal_noisy(void **state)
{
    int *res;
    unsigned count;
    int sum;
    int expected[] = {-43, 12, 56, 2147483547};

	res = get_randomized("12 2147483547ádfgksdf égjtq-43iohjtedélfgjőöikrfmásékfdjé 56", &count, &sum);
    assert_int_equal(count, 4);
    assert_int_equal(sum, 2147483572);
    qsort(res, count, sizeof(int), comp);
	assert_memory_equal(res, expected, sizeof(int) * count);
    free(res);
}



static void test_empty(void **state)
{
    int *res;
    unsigned count;
    int sum;

    res = get_randomized("", &count, &sum);
	assert_int_equal(count, 0);
	assert_int_equal(sum, 0);
	assert_null(res);
}

static void test_overflow(void **state)
{
    int *res;
    unsigned count;
    int sum;

    res = get_randomized("2147483647 5", &count, &sum);
	assert_int_equal(count, 0);
	assert_int_equal(sum, 0);
	assert_null(res);
}

static void test_underflow(void **state)
{
    int *res;
    unsigned count;
    int sum;

    res = get_randomized("-2147483647 -5", &count, &sum);
	assert_int_equal(count, 0);
	assert_int_equal(sum, 0);
	assert_null(res);
}


int main(void)
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(test_normal),
		cmocka_unit_test(test_negative),
		cmocka_unit_test(test_skip_overflowing_num),
		cmocka_unit_test(test_skip_underflowing_num),
		cmocka_unit_test(test_randomness),
		cmocka_unit_test(test_normal_noisy),
		cmocka_unit_test(test_empty),
		cmocka_unit_test(test_overflow),
		cmocka_unit_test(test_underflow)
	};

	return cmocka_run_group_tests(tests, NULL, NULL);
}
