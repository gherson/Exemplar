# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
import unittest, exemplar
actual_io_trace = ''  # Receives test values print()'ed and input().
global_input = []   # Assigned in each test to provide input() values to the function under test.


# 3 functions unchanged from starter:
# print() is mocked so the tests can recreate the .exem in actual_io_trace.
def print(line: str = "") -> None:
    global actual_io_trace
    line = line.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes
    actual_io_trace += ">" + line + '\n'


# input() is mocked to simulate user entries, for the tests' processing and for the tests' actual_io_trace record.
def input(line: str = "") -> str:
    global actual_io_trace
    result = global_input.pop(0)
    result = result.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes
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
        global actual_io_trace
        actual_io_trace = ''
    
    def test_jokes1(self):
        global global_input
        global_input = ['', '', '', '', '']  # From an example of the .exem
        jokes()  # The function under test is used to write to actual_io_trace.
        self.assertEqual(get_expected_io('jokes.exem', example_id=0), actual_io_trace)


if __name__ == '__main__':
    unittest.main()
