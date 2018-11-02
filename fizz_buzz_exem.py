def fizz_buzz(i1):
    if i1 % 3 == 0 and i1 % 5 == 0:
        return "FizzBuzz"
    elif i1 % 3 == 0:
        return "Fizz"
    elif i1 % 5 == 0:
        return "Buzz"
    else:
        return i1
