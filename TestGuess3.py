# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
import unittest, exemplar
out_trace = ''  # Will receive each test's print()'ed values.
in_trace = []   # Assigned in each test to provide input() values to the function under test.


# print() is mocked to allow the tests a chance to recreate the .exem in out_trace.
def print(line: str = "") -> None:
    global out_trace
    out_trace += ">" + line + '\n'


# input() is mocked to simulate user entries and allow the tests to recreate the .exem in out_trace.
def input(line: str = "") -> str:
    global out_trace
    result = in_trace.pop(0)
    out_trace += "<" + result + '\n'  # Eg, '<Albert\n'
    return result


# The (generated) function under test.
def guess3():
    print('Hello! What is your name?')
    name = input('name:')  # Eg, Albert
    secret = int(input('secret:'))  # Eg, 4
    print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
    for guess_count in range(0, 3):
        print('Take a guess.')
        guess = int(input('guess:'))  # Eg, 10
        if guess>secret:
            print('Your guess is too high.')
        elif guess<secret:
            print('Your guess is too low.')
        elif guess==secret:
            print('Good job, ' + str(name) + '! You guessed my number in ' + str(guess_count+1) + ' guesses!')


class TestGuess3(unittest.TestCase):

    def setUp(self):
        global out_trace
        out_trace = ''

    # Return the i/o statements of the named .exem file for comparison with out_trace.
    @staticmethod
    def get_expected(exem: str) -> str:
        out_exem_lines = []
        for line in exemplar.clean(exemplar.from_file(exem)):
            if line.startswith('<') or line.startswith('>'):
                out_exem_lines.append(line)
        return '\n'.join(out_exem_lines) + '\n'
    
    def test_guess31(self):
        global in_trace
        in_trace = ['Albert', '4', '10', '2', '4']  # From an example of the .exem
        guess3()  # The function under test is used to write to out_trace.
        self.assertEqual(self.get_expected('guess3.exem'), out_trace)


if __name__ == '__main__':
    unittest.main()


''' The source .exem, for reference:
"""
Todo Enable full line comments. Enable as penultimate line: 3 == guess_count + 1
"""
>Hello! What is your name?
<Albert
name==i1         # simple assignment (SA)
<4
secret==i1       # SA
>Well, Albert, I am thinking of a number between 1 and 20.
guess_count==0   # iteration
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
'''
