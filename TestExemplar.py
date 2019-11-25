import unittest
import exemplar


class TestExemplar(unittest.TestCase):
    """
    These unit test Exemplar by spot-checking exemplary solutions. (Class TestExemplarIntegration is outdated. 2019-11-21)
    Note that (.py, .tmp) files are written for passing and not failing tests.
    """

    @classmethod
    def setUp(cls):
        pass
        """
        exemplar.reset_db()  # Unshared, in-memory database.
        # Replicates the_trace after loading prime_number.exem via readlines():
        examples = [  # commas required!
            '2\n', 'True\n', 'i1 == 2c\n', '\n',
            '3\n', 'True\n', 'i1 % (i1-1) != 0c, (i1-1)==2c\n', '\n',
            '4\n', 'False\n', 'i1 % (i1-1) != 0c, (i1-1)>2c, \n', 'i1 % (i1-2) == 0c\n', '\n',
            '5\n', 'True\n', 'i1 % (i1-1) != 0c, (i1-1)>2c, \n', 'i1 % (i1-2) != 0c, (i1-2)>2c, \n',
            'i1 % (i1-3) != 0c, (i1-3)==2c\n', '\n',
            '6\n', 'False\n', 'i1 % (i1-1) != 0c, (i1-1)>2c, \n', 'i1 % (i1-2) != 0c, (i1-2)>2c, \n',
            'i1 % (i1-3) != 0c, (i1-3)>2c, \n', 'i1 % (i1-4) == 0c\n', '\n',
            '0\n', '"input < 1 is illegal"\n', 'i1 < 1c\n', '\n',
            '1\n', 'False\n', 'i1 == 1c \n', '\n',
            '1008\n', 'False\n', '\n',
            '1009\n', 'True\n', '\n']
        exemplar.fill_example_lines(examples)  # Inserts into the examples and termination tables."""

    def test_fizz_buzz(self):
        code, test_file_contents = exemplar.reverse_trace("fizz_buzz.exem")
        assert """def fizz_buzz():
    i1 = int(input("i1:"))""" in code
        assert "# The generated function under Stage 2" in test_file_contents

    def test_leap_year(self):
        code, test_file_contents = exemplar.reverse_trace("leap_year.exem")
        assert """def leap_year():
    i1 = int(input("i1:"))""" in code
        assert "# The generated function under Stage 2" in test_file_contents

    def test_prime_number(self):
        code, test_file_contents = exemplar.reverse_trace("prime_number.exem")
        assert """def prime_number():
    inp = int(input("inp:"))""" in code
        assert "# The generated function under Stage 2" in test_file_contents

    def test_guess4(self):
        code, test_file_contents = exemplar.reverse_trace("guess4.exem")
        assert """def guess4():
    print('Hello! What is your name?')""" in code
        assert "# The generated function under Stage 2" in test_file_contents

    """
    def test_denude1(self):
        expected = "code"
        code = exemplar.denude(' code  ')
        self.assertEqual(expected, code)

    def test_define_loop1(self):
        sql = "SELECT DISTINCT reason AS r1 FROM examples WHERE reason IS NOT NULL AND loop_likely = 1 " + \
                "ORDER BY cond_cnt DESC, inp"
        exemplar.cursor.execute(sql)
        loop_likely_reasons = exemplar.cursor.fetchall()
        loop_steps, loop_step_increments = exemplar.define_loop(loop_likely_reasons)
        expected = [], []  # Nothing will be found without running mark_loop_likely() and remove_all_c_labels()
        self.assertEqual(expected, (loop_steps, loop_step_increments))
    def test_gen_return4(self):
        with self.assertRaises(TypeError):  # TypeError: 'NoneType' object is not subscriptable
            exemplar.get_output("won't be found")

    def test_dump_table1(self):
        expected = "[all examples:\n(inp, output, reason, cond_cnt, loop_likely)\n" + \
            "('2', 'True', 'i1 == 2', 1, 0),\n" + \
            "('3', 'True', 'i1 % (i1-1) != 0, (i1-1)==2', 2, 0),\n" + \
            "('4', 'False', 'i1 % (i1-1) != 0, (i1-1)>2, i1 % (i1-2) == 0', 3, 0),\n" + \
            "('5', 'True', " + \
            "'i1 % (i1-1) != 0, (i1-1)>2, i1 % (i1-2) != 0, (i1-2)>2, i1 % (i1-3) != 0, (i1-3)==2', 6, 0),\n" + \
            "('6', 'False', 'i1 % (i1-1) != 0, (i1-1)>2, i1 % (i1-2) != 0, (i1-2)>2, i1 % (i1-3) != 0, " + \
            "(i1-3)>2, i1 % (i1-4) == 0', 7, 0),\n" + \
            "('0', '\"input < 1 is illegal\"', 'i1 < 1', 1, 0),\n" + \
            "('1', 'False', 'i1 == 1', 1, 0),\n" + \
            "('1008', 'False', None, 0, 0),\n" + \
            "('1009', 'True', None, 0, 0)]"
        # print(expected)
        # print(exemplar.dump_table("examples"))
        self.assertEqual(expected, exemplar.dump_table("examples"))

    def test_dump_table2(self):
        exemplar.mark_loop_likely()  # Update the loop_likely column in the examples and termination tables.
        exemplar.remove_all_c_labels()
        expected = ""[all termination:
(final_cond, output, step_num, loop_step, loop_likely)
('i1 == 2', 'True', None, None, 0),
('(i1-1)==2', 'True', None, None, 1),
('i1 % (i1-2) == 0', 'False', None, None, 1),
('i1 < 1', '"input < 1 is illegal"', None, None, 0),
('i1 == 1', 'False', None, None, 0)]""
        self.assertEqual(expected, exemplar.dump_table("termination"))

    ""Example tests:
    Prototype:
    def test_(self):
        expected = ""
        self.assertEqual(expected, exemplar.(""))
        
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    """


# if __name__ == '__main__':
    # unittest.main()
