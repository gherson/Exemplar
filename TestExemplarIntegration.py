import unittest
import exemplar


class TestExemplarIntegration(unittest.TestCase):
    """
    The below test_* methods, e.g., test_fizz_buzz(), compare their `expected` result (that they have
    hard-coded via docstring) with the *actual* result of running Exemplar on the contents of their
    .exem file.  2018-06-07
    N.B. Running this class (re)creates .exem.py files.
    """
    def test_guess2(self):
        expected = """def guess2(i1):
    if i1 == 4:
        return "good job"
    elif i1 > 4:
        return "too high"
    elif i1 < 4:
        return "too low"\n"""
        code = exemplar.reverse_trace('guess2.exem')
        self.assertEqual(expected, code)

    def test_fizz_buzz(self):
        expected = """def fizz_buzz(i1):
    if i1 % 3 == 0 and i1 % 5 == 0:
        return "FizzBuzz"
    elif i1 % 3 == 0:
        return "Fizz"
    elif i1 % 5 == 0:
        return "Buzz"
    else:
        return i1\n"""
        code = exemplar.reverse_trace('fizz_buzz.exem')
        self.assertEqual(expected, code)

    def test_leap_year(self):
        expected = """def leap_year(i1):
    if i1 % 4 == 0 and i1 % 100 != 0:
        return True
    elif i1 % 400 == 0:
        return True
    else:
        return False\n"""
        code = exemplar.reverse_trace('leap_year.exem')
        self.assertEqual(expected, code)

    def test_prime_number(self):
        expected = """def prime_number(i1):
    if i1 == 1:
        return False
    elif i1 == 2:
        return True
    elif i1 < 1:
        return "input < 1 is illegal"
    
    accum1 = 1
    accum2 = 1
    while i1 % (i1-accum1) != 0 and (i1-accum2)>2:
        accum1 += 1
        accum2 += 1
    if i1 % (i1-accum1) == 0:
        return False
    elif (i1-accum2)==2:
        return True\n"""
        code = exemplar.reverse_trace('prime_number.exem')
        self.assertEqual(expected, code)

    # def test_my_split(self):
    #     code = exemplar.reverse_trace('my_split.exem')
        # redundant  print(code)  # step 1


# if __name__ == '__main__':
#     unittest.main()