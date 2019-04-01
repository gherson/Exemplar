# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
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
def get_expected(exem: str) -> str:
    out_exem_lines = []
    for line in exemplar.clean(exemplar.from_file(exem)):
        if line.startswith('<') or line.startswith('>'):
            out_exem_lines.append(line)
    return '\n'.join(out_exem_lines) + '\n'


# The (working) sequential target function.
def jokes():
    __example__=0
    assert __example__==0
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
        global io_trace
        io_trace = ''
    
    def test_jokes1(self):
        global example_input
        example_input = ['', '', '', '', '']  # From an example of the .exem
        jokes()  # The function under test is used to write to io_trace.
        self.assertEqual(get_expected('jokes.exem'), io_trace)


if __name__ == '__main__':
    unittest.main()
