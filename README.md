# Exemplar
See [LOG.md](LOG.md) for status.

The goal of this project is synthesis of working (unpolished) Python functions from example input/output and assertions. 

Currently, if/elif, for loop, and break controls are synthesized until all given examples pass.

Exemplar's mechanisms for finding conforming code are deduction, generate-and-test, and asking multiple choice questions.

Examples that result in the function at bottom: 

    """
    leapYear(int year):
    returns true iff
    * the year is divisible by 4 and not divisible by 100 (eg, 2012, 2016, 2020, 2024)
    or
    * the year is divisible by 400 (eg, 2000, 2400, 2800)
    """
    <399
    True
    >False
    
    <400
    i1 % 400 == 0
    >True
    
    <2012
    i1 % 4 == 0 and i1 % 100 != 0
    >True
    
    <2000
    i1 % 400 == 0
    >True
    
    <2013
    True
    >False
    
    <2014
    True
    >False
    
    <2015
    True
    >False
    
    <2016
    i1 % 4 == 0 and i1 % 100 != 0
    >True
    
    <2020
    i1 % 4 == 0 and i1 % 100 != 0
    >True
    
    <2400
    i1 % 400 == 0
    >True

is interpreted to mean

    def leap_year():
        i1 = int(input("i1:"))  # Eg, 399
        if i1%400==0:
            print(True)
            return True
        elif i1 % 4 == 0 and i1 % 100 != 0:
            print(True)
            return True
        elif True:
            print(False)
            return False
        
Per-example unit tests are also generated.

This project is licensed under the terms of the GPL v3 license.
