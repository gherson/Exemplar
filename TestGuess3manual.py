# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
import unittest
import exemplar


class TestGuess3(unittest.TestCase):
    out_trace = ''
    in_trace = []

    # print() is redefined to recreate a clean .exem in out_trace (stripped of comments).
    def print(self, line: str = "") -> None:
        #global out_trace
        self.out_trace += ">" + line + '\n'

    # input() is redefined to recreate a clean .exem in out_trace (stripped of comments).
    # N.B. Automated testing requires that standard input be redirected to come from a file.
    def input(self, line: str = "") -> None:
        #global out_trace, in_trace
        value = self.in_trace.pop(0)
        self.out_trace += "<" + value + '\n'  # Eg, '<Albert\n'
        return value

    def guess3(self):
        self.print('Hello! What is your name?')
        name = self.input('name:')  # Eg, Albert
        secret = int(self.input('secret:'))  # Eg, 4
        self.print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
        for guess_count in range(0, 3):
            self.print('Take a guess.')
            guess = int(self.input('guess:'))  # Eg, 10
            if guess > secret:
                self.print('Your guess is too high.')
            elif guess < secret:
                self.print('Your guess is too low.')
            elif guess == secret:
                self.print('Good job, ' + str(name) + '! You guessed my number in 3 guesses!')

    def setUp(self):
        #global out_trace
        self.out_trace = ''

    # Return the named exem (stripped of comments).
    @staticmethod
    def get_expected(exem: str) -> str:
        out_exem_lines = []
        for line in exemplar.clean(exemplar.from_file(exem)):
            if line.startswith('<') or line.startswith('>'):
                out_exem_lines.append(line)
        return '\n'.join(out_exem_lines) + '\n'

    def test_guess31(self):
        # global in_trace
        self.in_trace = ['Albert', '4', '10', '2', '4']
        spam = "asdf"
        self.guess3()  # The function under test.
        self.assertEqual(self.get_expected('guess3.exem'), self.out_trace)


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
>Good job, Albert! You guessed my number in 3 guesses!
'''