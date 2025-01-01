#include <klee/klee.h>
#include <assert.h>
int example_function1(int x, int y)
{
    return (x / 2) + (y / 2) + ((x % 2 + y % 2) / 2);
}
int example_function2(int x, int y)
{
    return (int)((x + y) / 2.0);
    //return (int)(((long long)x + (long long)y) / 2.0);
}
int compareFunction(int x, int y)
{
    int result1 = example_function1(x, y);
    int result2 = example_function2(x, y);
    klee_assert(result1 == result2);
    return 1;
}
int main()
{
    int a, b;
    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");
    compareFunction(a, b);
    return 0;
}