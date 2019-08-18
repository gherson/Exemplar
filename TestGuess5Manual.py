"""
Exemplar's job is to recognize the control implied (shown to the right) by the example_lines (at left):
[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, None, None),
(10, 0, eg == 0, truth, None, None),                        for eg in range(0, ?):
(15, 0, Hello! What is your name?, out, None, None),
(20, 0, Albert, in, None, None),
(25, 0, name==i1, truth, None, None),
(30, 0, 4, in, None, None),
(35, 0, secret==i1, truth, None, None),
(40, 0, Well, Albert, I am thinking of a number between 1 and 20., out, None, None),
(45, 0, guess_count==0, truth, None, None),                     for guess_count in range(0, ?):  # ?==2 just for this example.
(50, 0, Take a guess., out, None, None),
(55, 0, 10, in, None, None),
(60, 0, guess==i1, truth, None, None),
(65, 0, guess>secret, truth, None, None),                           if guess>secret:
(70, 0, Your guess is too high., out, None, None),
(75, 0, guess_count == 1, truth, None, None),
(80, 0, Take a guess., out, None, None),
(85, 0, 2, in, None, None),
(90, 0, guess==i1, truth, None, None),
(95, 0, guess<secret, truth, None, None),                           elif guess<secret:
(100, 0, Your guess is too low., out, None, None),
(105, 0, guess_count==2, truth, None, None),
(110, 0, Take a guess., out, None, None),
(115, 0, 4, in, None, None),
(120, 0, guess==i1, truth, None, None),
(125, 0, guess==secret, truth, None, None),                         elif guess==secret
(130, 0, guess_count + 1 == 3, truth, None, None),
(135, 0, Good job, Albert! You guessed my number in 3 guesses!, out, None, None),
                                                                        break # implied by premature (2 not 6) ending to this
                                                                                example of the guess_count loop, detectable
                                                                                once the below eg==1 example is processed.
(140, 0, eg == 1, truth, None, None),
(145, 0, Hello! What is your name?, out, None, None),
(150, 0, John, in, None, None),
(155, 0, name==i1, truth, None, None),
(160, 0, 3, in, None, None),
(165, 0, secret==i1, truth, None, None),
(170, 0, Well, John, I am thinking of a number between 1 and 20., out, None, None),
(175, 0, guess_count==0, truth, None, None),                    for guess_count in range(0, 5):
(180, 0, Take a guess., out, None, None),
(185, 0, 11, in, None, None),
(190, 0, guess==i1, truth, None, None),
(195, 0, guess>secret, truth, None, None),                          if guess > secret:
(200, 0, Your guess is too high., out, None, None),
(205, 0, guess_count == 1, truth, None, None),
(210, 0, Take a guess., out, None, None),
(215, 0, 1, in, None, None),
(220, 0, guess==i1, truth, None, None),
(225, 0, guess<secret, truth, None, None),                          if guess < secret:
(230, 0, Your guess is too low., out, None, None),
(235, 0, guess_count==2, truth, None, None),
(240, 0, Take a guess., out, None, None),
(245, 0, 2, in, None, None),
(250, 0, guess==i1, truth, None, None),
(255, 0, guess<secret, truth, None, None),                          if guess < secret:
(260, 0, Your guess is too low., out, None, None),
(265, 0, guess_count==3, truth, None, None),
(270, 0, Take a guess., out, None, None),
(275, 0, 10, in, None, None),
(280, 0, guess==i1, truth, None, None),
(285, 0, guess>secret, truth, None, None),                          ...
(290, 0, Your guess is too high., out, None, None),
(295, 0, guess_count==4, truth, None, None),
(300, 0, Take a guess., out, None, None),
(305, 0, 9, in, None, None),
(310, 0, guess==i1, truth, None, None),
(315, 0, guess>secret, truth, None, None),                          ...
(320, 0, Your guess is too high., out, None, None),
(325, 0, guess_count==5, truth, None, None),
(330, 0, Take a guess., out, None, None),
(335, 0, 8, in, None, None),
(340, 0, guess==i1, truth, None, None),
(345, 0, guess>secret, truth, None, None),                          ...
(350, 0, Your guess is too high., out, None, None),
(355, 0, guess_count >= 5, truth, None, None),              (end of guess_count loop one line above is implied by this
 line's deviation from past iterations. Can be best explained by reaching range end.<p>This line implies) if guess_count >= 5:
(360, 0, Nope. The number I was thinking of was 3., out, None, None)]
"""
import unittest, exemplar
io_trace = ''  # Will receive each test's print()'ed values.
example_input = []   # Assigned in each test to provide input() values to the function under test.


# print() is mocked so the tests can recreate the .exem in io_trace.
def print(line: str = "") -> None:
    global io_trace
    io_trace += ">" + line + '\n'


# input() is mocked to simulate user entries, for the tests' processing and for the tests' io_trace record.
def input(line: str = "") -> str:
    global io_trace
    result = example_input.pop(0)
    io_trace += "<" + result + '\n'  # Eg, '<Albert\n'
    return result


# Return the i/o statements of the named .exem file for comparison with io_trace.
def get_expected(exem: str, example_id: int) -> str:
    out_exem_lines = []
    example_reached = 0
    for line in exemplar.clean(exemplar.from_file(exem)):
        if not line.strip():
            example_reached += 1
        if (line.startswith('<') or line.startswith('>')) and example_id == example_reached:
            out_exem_lines.append(line)
    return '\n'.join(out_exem_lines) + '\n'


# The generated function under test.
def guess5():
    for eg in range(0, 2):
        print('Hello! What is your name?')
        name = input("name:")  # Eg, Albert
        secret = int(input("secret:"))  # Eg, 4
        print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
        for guess_count in range(0, 6):
            print('Take a guess.')
            guess = int(input("guess:"))  # Eg, 10
            if guess > secret:
                print('Your guess is too high.')
            if guess < secret:
                print('Your guess is too low.')
            if secret == guess:
                print('Good job, ' + str(name) + '! You guessed my number in ' + str(guess_count+1) + ' guesses!')
                break
    if guess_count >= 5:
        print('Nope. The number I was thinking of was ' + str(secret) + '.')


class TestGuess5(unittest.TestCase):

    def setUp(self):
        global io_trace
        io_trace = ''
    
    def test_guess51(self):
        global example_input
        example_input = ['Albert', '4', '10', '2', '4', 'John', '3', '11', '1', '2', '10', '9', '8']  # From an example of the .exem
        guess5()  # The function under test is used to write to io_trace.
        self.assertEqual(get_expected('guess5.exem', 0), io_trace)


if __name__ == '__main__':
    unittest.main()
