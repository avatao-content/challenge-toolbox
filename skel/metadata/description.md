This is a an example description markdown file. It is important to use maximally H4 section names (####) so as to fit into the current frontend style in avatao.

Your task is to _securely_ implement the `get_randomized` function of the `app.c` file as specified below. You don't need to implement the `main` function and call `get_randomized`. Your function will be tested automatically upon solution submission.

The function gets a zero-terminated random input and collects the 32-bit integers from `INT_MIN` to `INT_MAX` (skip the ones out of this range) separated by non-numeric characters. The function needs to sum those integers and if overflow occurs, handle it as an error. The return value should be `NULL` if an error occured, otherwise an array with the numbers found in the text. The order of elements in this array should be (kind-of) securely randomized.

#### Parameters

`const char *text`: This is the user input you need to process. This input can contain anything, but it is zero-terminated.

`unsigned *count`: Output parameter, the number of integers found, 0 if error occurs.

`int *sum`: Sum of the numbers. It is 0 if error occurs (e.g., buffer overflow).

#### Example

##### Usage

    int count;
    int sum;
    int *res;
    res = get_randomized("1 2 asdf3", &count, &sum);
    free(res);

##### Output

    sum -> 6
    count -> 3
    res -> [1,2,3] or [1,3,2] or [2,1,3] or [2,3,1] or [3,1,2] or [3,2,1] (print one of these)

Hint: the program will be tested in a Linux box and compiled with gcc.
