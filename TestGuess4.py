# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
import unittest, exemplar
actual_io_trace = ''  # Receives test values print()'ed and input().
example_input = []   # Assigned in each test to provide input() values to the function under test.


# 3 functions unchanged from starter:
# print() is mocked so the tests can recreate the .exem in actual_io_trace.
def print(line: str = "") -> None:
    global actual_io_trace
    actual_io_trace += ">" + line + '\n'


# input() is mocked to simulate user entries, for the tests' processing and for the tests' actual_io_trace record.
def input(line: str = "") -> str:
    global actual_io_trace
    result = example_input.pop(0)
    actual_io_trace += "<" + result + '\n'  # Eg, '<Albert\n'
    return result


# Return the i/o statements of the named .exem file (for comparison with actual_io_trace).
def get_expected_io(exem: str, example_id: int) -> str:
    out_exem_lines = []
    example_reached = 0
    for line in exemplar.clean(exemplar.from_file(exem)):
        if not line.strip():
            example_reached += 1
        if (line.startswith('<') or line.startswith('>')) and example_id == example_reached:
            out_exem_lines.append(line)
    return '\n'.join(out_exem_lines) + '\n'


# The generated function under test.
def guess4():
    print('Hello! What is your name?')
    name = input("name:")  # Eg, John
    secret = int(input("secret:"))  # Eg, 3
    print('Well, ' + str(name) + ', I am thinking of a number between 1 and 20.')
    for guess_count in range(0, 6):
        print('Take a guess.')
        guess = int(input("guess:"))  # Eg, 11
        if guess > secret:
            print('Your guess is too high.')
    if guess < secret:
        print('Your guess is too low.')
    if guess_count >= 5:
        print('Nope. The number I was thinking of was ' + str(secret) + '.')


class TestGuess4(unittest.TestCase):

    def setUp(self):
        global actual_io_trace
        actual_io_trace = ''
    
    def test_guess41(self):
        global example_input
        example_input = ['John', '3', '11', '1', '2', '10', '9', '8']  # From an example of the .exem
        guess4()  # The function under test is used to write to actual_io_trace.
        self.assertEqual(get_expected_io('guess4.exem', example_id=1), actual_io_trace)


if __name__ == '__main__':
    unittest.main()
