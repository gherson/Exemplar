# AUTOGENERATED FILE

import unittest


def leap_year(i1):
    if i1 % 4 == 0 and i1 % 100 != 0:
        return True
    elif i1 % 400 == 0:
        return True
    else:
        return False


class TestLeapYear(unittest.TestCase):

    def test_leap_year1(self):
        i1 = 2012
        self.assertEqual(True, leap_year(i1))
    
    def test_leap_year2(self):
        i1 = 2000
        self.assertEqual(True, leap_year(i1))
    
    def test_leap_year3(self):
        i1 = 2013
        self.assertEqual(False, leap_year(i1))
    
    def test_leap_year4(self):
        i1 = 2014
        self.assertEqual(False, leap_year(i1))
    
    def test_leap_year5(self):
        i1 = 2015
        self.assertEqual(False, leap_year(i1))
    
    def test_leap_year6(self):
        i1 = 2016
        self.assertEqual(True, leap_year(i1))
    
    def test_leap_year7(self):
        i1 = 2020
        self.assertEqual(True, leap_year(i1))
    
    def test_leap_year8(self):
        i1 = 2400
        self.assertEqual(True, leap_year(i1))
    

if __name__ == '__main__':
    unittest.main()
