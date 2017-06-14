Buy All The Things - Part 2
===========================

## Understanding the challenge

Cost: 10%

You solved the first task by exploiting an overflow vulnerability. You need to write a method that will not let that happen.
If an overflow occurs just return the debt without modification.

## How to check for overflow

Cost: 10%

x + y > MAX_INT wouldn't work! Why? Because you are checking for an overflow after it occurred.
We need to check before we actually add the two numbers. We can maybe reorder this inequality so it stays the same, but it wouldn't overflow.

## public int add(int debt, int prize)

Cost: 70%

Here is a solution:

```java

public class Program {

    public int add(int debt, int prize) {
        if (debt > Integer.MAX_VALUE - prize) {
          return debt;
        } else {
          return debt+prize;
        }
    }
}

```

## Complete solution

```java

public class Program {

    public int add(int debt, int prize) {
        if (debt > Integer.MAX_VALUE - prize) {
          return debt;
        } else {
          return debt+prize;
        }
    }
}

```
