import unittest


def prime_number(i1):
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
        return True


class TestPrimeNumber(unittest.TestCase):

    def test_prime_number1(self):
        i1 = 2
        self.assertEqual(True, prime_number(i1))
    
    def test_prime_number2(self):
        i1 = 3
        self.assertEqual(True, prime_number(i1))
    
    def test_prime_number3(self):
        i1 = 4
        self.assertEqual(False, prime_number(i1))
    
    def test_prime_number4(self):
        i1 = 5
        self.assertEqual(True, prime_number(i1))
    
    def test_prime_number5(self):
        i1 = 6
        self.assertEqual(False, prime_number(i1))
    
    def test_prime_number6(self):
        i1 = 0
        self.assertEqual("input < 1 is illegal", prime_number(i1))
    
    def test_prime_number7(self):
        i1 = 1
        self.assertEqual(False, prime_number(i1))
    
    def test_prime_number8(self):
        i1 = 1008
        self.assertEqual(False, prime_number(i1))
    
    def test_prime_number9(self):
        i1 = 1009
        self.assertEqual(True, prime_number(i1))
    

if __name__ == '__main__':
    unittest.main()
