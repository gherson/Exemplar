# Exemplar
Programming by examples given as unit tests (i/o) that are augmented with assertions.  

Example: 

    >Hello! What is your name?
    <Albert
    name             # Short for name==i1
    <4
    secret
    >Well, Albert, I am thinking of a number between 1 and 20.
    guess_count==0  
    >Take a guess.
    <10
    guess, guess>secret  # assignment, selection
    >Your guess is too high.
    guess_count == 1  # repeated condition assumed to indicate iteration.
    >Take a guess.
    <2
    guess, guess<secret  
    >Your guess is too low.
    guess_count==2  
    >Take a guess.
    <4
    guess, guess==secret  
    guess_count + 1 == 3  
    >Good job, Albert! You guessed my number in 3 guesses!
    
becomes
    
    def guess3(self):
        print('Hello! What is your name?')
        name = input('name:')  # Eg, Albert
        secret = int(input('secret:'))  # Eg, 4
        print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
        for guess_count in range(0, 3):
            print('Take a guess.')
            guess = int(input('guess:'))  # Eg, 10
            if guess > secret:
                print('Your guess is too high.')
            elif guess < secret:
                print('Your guess is too low.')
            elif guess == secret:
                print('Good job, ' + str(name) + '! You guessed my number in 3 guesses!')