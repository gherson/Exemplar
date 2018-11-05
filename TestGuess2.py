import unittest


def guess2(i1):
    if i1 == 4:
        return "good job"
    elif i1 > 4:
        return "too high"
    elif i1 < 4:
        return "too low"


class TestGuess2(unittest.TestCase):

    def test_guess21(self):
        i1 = 10
        self.assertEqual("too high", guess2(i1))
    
    def test_guess22(self):
        i1 = 2
        self.assertEqual("too low", guess2(i1))
    
    def test_guess23(self):
        i1 = 4
        self.assertEqual("good job", guess2(i1))
    
    def test_guess24(self):
        i1 = 6
        self.assertEqual("too high", guess2(i1))
    
    def test_guess25(self):
        i1 = 5
        self.assertEqual("too high", guess2(i1))
    
    def test_guess26(self):
        i1 = 1
        self.assertEqual("too low", guess2(i1))
    

if __name__ == '__main__':
    unittest.main()
