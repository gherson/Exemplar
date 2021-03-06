# AUTOGENERATED FILE -- RENAME OR YOUR EDITS WILL BE OVERWRITTEN
import unittest
actual_io_trace = ''  # Receives test values print()'ed and input().
global_input = []   # Assigned in each test to provide input() values to the function under test.


# 3 functions unchanged from starter:
# print() is mocked to see if the tests recreate the .exem-specified i/o in actual_io_trace.
def print(line="") -> None:
    global actual_io_trace
    if line is str:
        line = line.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes
    actual_io_trace += ">" + str(line) + '\n'


# input() is mocked to return the test-specified input as well as add it to actual_io_trace.
def input(variable_name: str = "") -> str:
    # (variable_name is ignored because it may not have been specified by the .exem.)
    global actual_io_trace
    result = global_input.pop(0)
    result = result.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes
    actual_io_trace += "<" + result + '\n'  # Eg, '<Albert\n'
    return result


# The generated function under Stage 2 (i.e., a test per example) testing.
def fizz_buzz():
    i1 = int(input("i1:"))  # Eg, 15
    if i1%3==0 and i1%5==0:
        print('FizzBuzz')
        return 'FizzBuzz' 
    elif i1%3==0:
        print('Fizz')
        return 'Fizz' 
    elif i1%5==0:
        print('Buzz')
        return 'Buzz' 
    else:  # == elif True:
        print(str(i1))
        return str(i1) 


class TestFizzBuzz(unittest.TestCase):

    def setUp(self):
        global actual_io_trace
        actual_io_trace = ''
        self.maxDiff = None

    def test_fizz_buzz4(self):
        global global_input
        global_input = ['15']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<15
>FizzBuzz
''', actual_io_trace)

    def test_fizz_buzz8(self):
        global global_input
        global_input = ['1']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<1
>1
''', actual_io_trace)

    def test_fizz_buzz12(self):
        global global_input
        global_input = ['2']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<2
>2
''', actual_io_trace)

    def test_fizz_buzz16(self):
        global global_input
        global_input = ['3']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<3
>Fizz
''', actual_io_trace)

    def test_fizz_buzz20(self):
        global global_input
        global_input = ['4']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<4
>4
''', actual_io_trace)

    def test_fizz_buzz24(self):
        global global_input
        global_input = ['5']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<5
>Buzz
''', actual_io_trace)

    def test_fizz_buzz28(self):
        global global_input
        global_input = ['6']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<6
>Fizz
''', actual_io_trace)

    def test_fizz_buzz32(self):
        global global_input
        global_input = ['7']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<7
>7
''', actual_io_trace)

    def test_fizz_buzz35(self):
        global global_input
        global_input = ['8']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<8
>8
''', actual_io_trace)

    def test_fizz_buzz38(self):
        global global_input
        global_input = ['9']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<9
>Fizz
''', actual_io_trace)

    def test_fizz_buzz42(self):
        global global_input
        global_input = ['10']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<10
>Buzz
''', actual_io_trace)

    def test_fizz_buzz45(self):
        global global_input
        global_input = ['15']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<15
>FizzBuzz
''', actual_io_trace)

    def test_fizz_buzz48(self):
        global global_input
        global_input = ['30']  # From the .exem
        fizz_buzz()  # The function under test is used to write to actual_io_trace.
        self.assertEqual('''<30
>FizzBuzz
''', actual_io_trace)


if __name__ == '__main__':
    unittest.main()
