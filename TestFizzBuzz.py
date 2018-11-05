import unittest


def fizz_buzz(i1):
    if i1 % 3 == 0 and i1 % 5 == 0:
        return "FizzBuzz"
    elif i1 % 3 == 0:
        return "Fizz"
    elif i1 % 5 == 0:
        return "Buzz"
    else:
        return i1


class TestFizzBuzz(unittest.TestCase):

    def test_fizz_buzz1(self):
        i1 = 1
        self.assertEqual(i1, fizz_buzz(i1))
    
    def test_fizz_buzz2(self):
        i1 = 2
        self.assertEqual(i1, fizz_buzz(i1))
    
    def test_fizz_buzz3(self):
        i1 = 3
        self.assertEqual("Fizz", fizz_buzz(i1))
    
    def test_fizz_buzz4(self):
        i1 = 4
        self.assertEqual(i1, fizz_buzz(i1))
    
    def test_fizz_buzz5(self):
        i1 = 5
        self.assertEqual("Buzz", fizz_buzz(i1))
    
    def test_fizz_buzz6(self):
        i1 = 6
        self.assertEqual("Fizz", fizz_buzz(i1))
    
    def test_fizz_buzz7(self):
        i1 = 7
        self.assertEqual(i1, fizz_buzz(i1))
    
    def test_fizz_buzz8(self):
        i1 = 8
        self.assertEqual(i1, fizz_buzz(i1))
    
    def test_fizz_buzz9(self):
        i1 = 9
        self.assertEqual("Fizz", fizz_buzz(i1))
    
    def test_fizz_buzz10(self):
        i1 = 10
        self.assertEqual("Buzz", fizz_buzz(i1))
    
    def test_fizz_buzz11(self):
        i1 = 15
        self.assertEqual("FizzBuzz", fizz_buzz(i1))
    
    def test_fizz_buzz12(self):
        i1 = 30
        self.assertEqual("FizzBuzz", fizz_buzz(i1))
    

if __name__ == '__main__':
    unittest.main()
