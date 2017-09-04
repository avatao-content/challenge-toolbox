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