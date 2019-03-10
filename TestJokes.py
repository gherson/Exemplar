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
def jokes():
    print('What do you get when you cross a snowman with a vampire?')
    input()
    print('Frostbite!')
    print('')
    print('What do dentists call an astronaut\'s cavity?')
    input()
    print('A black hole!')
    print('')
    print('Knock knock.')
    input()
    print('Who\'s there?')
    input()
    print('Interrupting cow.')
    input()
    print('Interrupting cow wh-MOO!')


class TestJokes(unittest.TestCase):

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
    
    def test_jokes1(self):
        global in_trace
        in_trace = ['', '', '', '', '']  # From an example of the .exem
        jokes()  # The function under test is used to write to out_trace.
        self.assertEqual(self.get_expected('jokes.exem'), out_trace)


if __name__ == '__main__':
    unittest.main()


''' The source .exem, for reference:
"""
jokes from http://inventwithpython.com/invent4thed/chapter4.html.

N.B. this is a script without list_conditions or variables.
"""
>What do you get when you cross a snowman with a vampire?
<
>Frostbite!
>
>What do dentists call an astronaut's cavity?
<
>A black hole!
>
>Knock knock.
<
>Who's there?
<
>Interrupting cow.
<
>Interrupting cow wh-MOO!
'''
