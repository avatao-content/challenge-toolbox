/* Used to explicitly link the submitted solution for the objdump checks */
#include "tests/geomean.cpp"

int main() {
    // Call all methods from the solution's code to prevent the compiler from
    // optimizing it away
    auto gm = geometric_mean();
}