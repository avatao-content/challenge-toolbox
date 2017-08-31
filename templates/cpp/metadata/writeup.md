Geometric mean
==============

## Complete the header of `geometric_mean()`

Cost: 20%

The function should use variadic templates from C++11 as follows:
```cpp
template<typename... Nums>
auto geometric_mean(Nums... nums) {
    /*code comes here*/
}
```

Using template argument deduction, the function will be able to take any combination of types. Template substitution will fail for types where multiplication or taking the nth root -- or the 1/nth power in our case -- fails, so handling incompatible types requires no manual intervention, it's all done by the compiler.

## Complete the body of `geometric_mean()`

Cost: 10%

The following three lines of code can be used to complement the header written in the previous hint. The `product_helper()` function is explained in the later ones.

```cpp
    unsigned int n = sizeof...(nums);
    auto product = product_helper(nums...);
    return std::pow(product, 1.0/n);
```

## Write a helper function to compute the product of the arguments -- Recursion

Cost: 50%

The product has to be computed with a recursive function, like this one:

```cpp
template<typename Num, typename... Nums>
auto product_helper(Num head, Nums... tail) {
    return head * product_helper(tail...);
}
```

## Write a helper function to compute the product of the arguments -- Stopping the recursion

Cost: 10%

You have to stop the recursion when there are no arguments left. ADL makes sure that this function is called instead of the template one, thus ending the recursion.
```cpp
auto product_helper() {
    return 1;
}
```

## Complete solution
```cpp
#include <cmath>
#include <iostream>

auto product_helper() {
    return 1;
}

template<typename Num, typename... Nums>
auto product_helper(Num head, Nums... tail) {
    return head * product_helper(tail...);
}

template<typename... Nums>
auto geometric_mean(Nums... nums) {
    unsigned int n = sizeof...(nums);
    auto product = product_helper(nums...);
    return std::pow(product, 1.0/n);
}
```