# Exemplar
Function synthesis from code traces consisting of >input, <output, and assertions 
modelling the needed control structure. 

Currently, if/elif, for loop, and break controls
 can be synthesized.
  
The mechanisms for finding conforming code are deduction and generate-and-test.

Example 1: 

    # User wins.
    >Hello! What is your name?
    <Albert
    name==i1         # simple assignment (SA)
    <4               # A random #
    secret==i1       # SA
    >Well, Albert, I am thinking of a number between 1 and 20.
    guess_count==0   # iteration
    # Full line comment.
    >Take a guess.
    <10
    guess==i1, guess>secret  # SA, selection
    >Your guess is too high.
    guess_count == 1 # iteration
    >Take a guess.
    <2
    guess==i1, guess<secret  # SA, selection
    >Your guess is too low.
    guess_count==2   # iteration
    >Take a guess.
    <4
    guess==i1, guess==secret  # SA, selection
    guess_count + 1 == 3  # SA
    >Good job, Albert! You guessed my number in 3 guesses!
    
   
    # User loses.
    >Hello! What is your name?
    <John
    name==i1
    <3
    secret==i1
    >Well, John, I am thinking of a number between 1 and 20.
    guess_count==0
    >Take a guess.
    <11
    guess==i1, guess>secret
    >Your guess is too high.
    guess_count == 1
    >Take a guess.
    <1
    guess==i1, guess<secret
    >Your guess is too low.
    guess_count==2
    >Take a guess.
    <2
    guess==i1, guess<secret
    >Your guess is too low.
    guess_count==3
    >Take a guess.
    <10
    guess==i1, guess>secret
    >Your guess is too high.
    guess_count==4
    >Take a guess.
    <9
    guess==i1, guess>secret
    >Your guess is too high.
    guess_count==5
    >Take a guess.
    <8
    guess==i1, guess>secret
    >Your guess is too high.
    guess_count >= 5  # User avoids guess_count == 5, as that'd look like another iteration.
    >Nope. The number I was thinking of was 3.

    
becomes
    
    def guess4():
        print('Hello! What is your name?')
        name = input("name:")  # Eg, Albert
        secret = int(input("secret:"))  # Eg, 4
        print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
        for guess_count in range(0, 6, 1):
            print('Take a guess.')
            guess = int(input("guess:"))  # Eg, 10
            if guess>secret:
                print('Your guess is too high.')
            elif guess<secret:
                print('Your guess is too low.')
            elif secret==guess:
                print('Good job, ' + str(name) + '! You guessed my number in ' + str(guess_count+1) + ' guesses!')
                break
        if guess_count>=5:
            print('Nope. The number I was thinking of was ' + str(secret) + '.')
        
 with per-example unit tests also generated.
 
 Example 2:
 
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

becomes

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
        
in the if/elif branch order Exemplar found to succeed.