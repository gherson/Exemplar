import unittest
import exemplar


class TestExemplar(unittest.TestCase):
    """
    These unit test the Exemplar methods. (Class TestExemplarIntegration, by contrast, tests whole problem solutions.)
    """
    @classmethod
    def setUp(cls):
        exemplar.reset_db()  # Unshared, in-memory database.
        global examples  # For database-dependent tests.
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
        exemplar.parse_trace(examples)  # Inserts into the examples and termination tables.

    def test_denude1(self):
        expected = "code"
        code = exemplar.denude(' code  ')
        self.assertEqual(expected, code)

    def test_denude2(self):
        expected = "code"
        code = exemplar.denude(" code # This should be removed. # 2nd comment ")
        self.assertEqual(expected, code)

    def test_denude3(self):
        expected = "code \# This should NOT be removed."
        code = exemplar.denude(" code \# This should NOT be removed. # 1st comment ")
        self.assertEqual(expected, code)

    def test_denude4(self):
        expected = "code '# This should NOT be removed.'"
        code = exemplar.denude(" code '# This should NOT be removed.' # 1st comment ")
        self.assertEqual(expected, code)

    def test_positions_outside_strings1(self):
        expected = [47, 51, 53, 54]  # From the 4 "t"s in "t not tt"
        self.assertEqual(expected, exemplar.positions_outside_strings(
            "'# These ttt will be ignored' including \this but not tthese", 't'))

    def test_remove_c_labels(self):
        expected = 'i1 % (i1-1) != 0, (i1-1)>2'
        self.assertEqual(expected, exemplar.remove_c_labels('i1 % (i1-1) != 0c, (i1-1)>2c'))

    def test_final_condition(self):
        expected = "(i1-1)>2c"
        self.assertEqual(expected, exemplar.final_condition("i1 % (i1-1) != 0c, (i1-1)>2c"))

    def test_schematize1(self):
        expected = "i1 % (len(i1)-_) <= 0c"
        self.assertEqual(expected, exemplar.schematize('i1 % (len(i1)-13) <= 0c'))

    def test_parse_trace1(self):
        exemplar.reset_db()  # Empty the database.
        exemplar.parse_trace(["2\n", "True\n", "i1 == 2c\n", "\n"])  # Simulating a 1-example .exem file.
        exemplar.cursor.execute("SELECT * FROM examples")
        expected = ('2', 'True', 'i1 == 2', 1, 0)  # The entire contents of the examples table, we expect.
        self.assertEqual(expected, exemplar.cursor.fetchone())
        exemplar.cursor.execute("SELECT * FROM termination")
        expected = ('i1 == 2', 'True', None, None, 0)  # The entire contents of the termination table, we expect.
        self.assertEqual(expected, exemplar.cursor.fetchone())

    def test_parse_trace2(self):
        exemplar.reset_db()  # Empty the database.
        exemplar.parse_trace(["1008\n", "False\n", "\n"])  # Simulating a 'reason'-less 1-example .exem file.
        exemplar.cursor.execute("SELECT * FROM examples")
        expected = ('1008', 'False', None, 0, 0)  # The entire contents of the examples table, we expect.
        self.assertEqual(expected, exemplar.cursor.fetchone())
        exemplar.cursor.execute("SELECT * FROM termination")  # Should be empty.
        self.assertEqual(None, exemplar.cursor.fetchone())

    def test_parse_trace3(self):
        exemplar.cursor.execute("SELECT COUNT(*) FROM examples")
        expected = 9
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_parse_trace4(self):
        exemplar.cursor.execute("SELECT COUNT(*) FROM termination")
        expected = 5
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_mark_loop_likely1(self):
        # Confirming that the count of loop_likely rows before and after calling mark_loop_likely().
        exemplar.cursor.execute("SELECT COUNT(*) FROM examples WHERE loop_likely = 1")
        expected = 0
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])
        exemplar.mark_loop_likely()
        exemplar.cursor.execute("SELECT COUNT(*) FROM examples WHERE loop_likely = 1")
        expected = 4
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_mark_loop_likely2(self):
        # Confirming that an exact match on a single condition 'reason' (of inp = 2) among the conditions of
        # multi-condition examples also leads to that single condition example's loop_likely being set to 1.
        exemplar.cursor.execute("UPDATE examples SET reason = 'i1 == 1, i1 == 2c', cond_cnt = 2 WHERE inp = 1")
        exemplar.mark_loop_likely()
        exemplar.cursor.execute("SELECT COUNT(*) FROM examples WHERE loop_likely = 1")
        expected = 5   # No longer 4
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_remove_all_c_labels1(self):
        # Reset db, put a few rows in examples table, and probe it before and after a call to remove_all_c_labels().

        exemplar.reset_db()  # Empty the database.
        # Simulating a 3-example .exem file with c labels in 2 rows, viz., 1 'output' field and 2 'reason' fields.
        exemplar.parse_trace(["1\n", "False\n",    "i1 == 1\n", "\n",
                              "2\n", "i1 == 2c\n", "i1 == 2c\n", "\n",
                              "3\n", "True\n",     "i1 % (i1-1) != 0c, (i1-1)==2c\n", "\n"])
        # Selecting the c label rows by what they should have after c label removal.
        select = "SELECT COUNT(*) FROM examples WHERE output = 'i1 == 2' OR reason = 'i1 % (i1-1) != 0, (i1-1)==2'"
        exemplar.cursor.execute(select)
        expected = 2  # 0   CAN NO LONGER TEST THIS FUNCTION BECAUSE c LABELS DON'T GET STORED. 11/1/18
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])
        exemplar.mark_loop_likely()  # Called for realism.
        exemplar.remove_all_c_labels()
        exemplar.cursor.execute(select)
        expected = 2
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_build_reason_evals1(self):
        # Reset db, put a few rows in examples table, and probe the reason_evals table after a call to build it.

        exemplar.reset_db()  # Empty the database.
        # Simulating a 2-example .exem file from the "FizzBuzz" problem.
        exemplar.parse_trace(["5\n", "Buzz\n", "i1 % 5 == 0c\n", "\n",
                              "6\n", "Fizz\n", "i1 % 3 == 0c\n", "\n"])
        exemplar.mark_loop_likely()
        exemplar.remove_all_c_labels()
        exemplar.build_reason_evals()
        exemplar.cursor.execute("SELECT count(*) FROM reason_evals")  # (inp, reason, reason_explains_io, reason_value)
        expected = 4  # Each 'reason' produces a True and False outcome as i1 takes turns as 5 and 6.
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])
        exemplar.cursor.execute("SELECT count(*) FROM reason_evals WHERE reason_value = 1")
        expected = 2
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])
        exemplar.cursor.execute("SELECT count(*) FROM reason_evals WHERE reason_value = 1 AND reason_explains_io = 1")
        expected = 2  # The reason_explains_io=1 explains the count of 2 here and in the prior Select.
        self.assertEqual(expected, exemplar.cursor.fetchone()[0])

    def test_find_safe_pretests1(self):
        # In the FizzBuzz problem, 'i1 % 3 == 0 and i1 % 5 == 0' can be a pretest to 'i1 % 5 == 0' but not v.v.
        exemplar.reset_db()  # Empty the database.
        # Simulating a 2-example .exem file.
        exemplar.parse_trace(["5\n", "Buzz\n", "i1 % 5 == 0c\n", "\n",
                              "15\n", "FizzBuzz\n", "i1 % 3 == 0c and i1 % 5 == 0c\n", "\n"])
        exemplar.mark_loop_likely()
        exemplar.remove_all_c_labels()
        exemplar.build_reason_evals()
        exemplar.find_safe_pretests()
        exemplar.cursor.execute("SELECT * FROM pretests")  # (pretest, condition)
        expected = "i1 % 3 == 0 and i1 % 5 == 0", 'i1 % 5 == 0'
        self.assertEqual(expected, exemplar.cursor.fetchone())

    def test_reset_db(self):
        exemplar.reset_db()  # Empties database.
        exemplar.cursor.execute("SELECT * FROM examples")  # So this should find nothing.
        self.assertEqual(None, exemplar.cursor.fetchone())

    def test_find_rel_op1(self):
        expected = (18, 20)
        self.assertEqual(expected, exemplar.find_rel_op("i1 % (len(i1)-13) <= 0c"))

    def test_find_rel_op2(self):
        expected = (18, 19)
        self.assertEqual(expected, exemplar.find_rel_op("i1 % (len(i1)-13) < 0c"))

    def test_find_rel_op3(self):
        expected = ()
        self.assertEqual(expected, exemplar.find_rel_op(""))

    def test_find_rel_op4(self):
        expected = (12, 14)
        self.assertEqual(expected, exemplar.find_rel_op("i1 % (i1-1) != 0c"))

    def test_same_step0(self):
        expected = True
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i1 % (i1-1) != 0"))

    def test_same_step1(self):
        expected = True
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i1 % (i1-1) == 0"))

    def test_same_step2(self):
        # Simplify the expressions -- note that + - is seen as different from minus:
        expected = False
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i1 % (i1+-1) != 0"))

    def test_same_step3(self):
        expected = False
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i1 % (i1-1) != 5"))

    def test_same_step4(self):
        expected = False
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i2 % (i1-1) != 0"))

    def test_same_step5(self):
        expected = False
        self.assertEqual(expected, exemplar.same_step("i1 % (i1-_) != 0", "i1 % (i1+1) != 0"))

    def test_list_conditions1(self):
        expected = ['i1 % (i1-1) != 0c']
        self.assertEqual(expected, exemplar.list_conditions('  i1 % (i1-1) != 0c  '))

    def test_list_conditions2(self):
        expected = ['i1 % (i1-1) != 0c', '(i1-1)=="hi, joe"']
        self.assertEqual(expected, exemplar.list_conditions('  i1 % (i1-1) != 0c  , (i1-1)=="hi, joe"  '))

    def test_list_conditions3(self):
        expected = ['']
        self.assertEqual(expected, exemplar.list_conditions(''))

    def test_get_inc_pos1(self):
        expected = (9, 10)
        self.assertEqual(expected, exemplar.get_inc_int_pos('i1 % (i1-1) != 0c'))

    def test_get_inc_pos2(self):
        expected = (12, 13)
        self.assertEqual(expected, exemplar.get_inc_int_pos('i1 % (i1 + +1) != 0c'))

    def test_get_inc_pos3(self):
        expected = (4, 5)
        self.assertEqual(expected, exemplar.get_inc_int_pos('(i1-1)>2c'))

    def test_get_inc_pos4(self):
        expected = ()
        self.assertEqual(expected, exemplar.get_inc_int_pos('i1 % (i1-_) != 0c'))

    def test_get_increment1(self):
        expected = -1
        self.assertEqual(expected, exemplar.get_increment('i1 % (i1-1) != 0c'))

    def test_get_increment2(self):
        expected = 1
        self.assertEqual(expected, exemplar.get_increment('i1 % (i1 + +1) != 0c'))

    def test_get_increment3(self):
        expected = -1
        self.assertEqual(expected, exemplar.get_increment('(i1-1)>2c'))

    def test_get_increment4(self):
        expected = 0
        self.assertEqual(expected, exemplar.get_increment('i1 % (i1-_) != 0c'))

    def test_define_loop1(self):
        sql = "SELECT DISTINCT reason AS r1 FROM examples WHERE reason IS NOT NULL AND loop_likely = 1 " + \
                "ORDER BY cond_cnt DESC, inp"
        exemplar.cursor.execute(sql)
        loop_likely_reasons = exemplar.cursor.fetchall()
        loop_steps, loop_step_increments = exemplar.define_loop(loop_likely_reasons)
        expected = [], []  # Nothing will be found without running mark_loop_likely() and remove_all_c_labels()
        self.assertEqual(expected, (loop_steps, loop_step_increments))

    def test_define_loop2(self):
        exemplar.mark_loop_likely()
        exemplar.remove_all_c_labels()
        sql = "SELECT DISTINCT reason AS r1 FROM examples WHERE reason IS NOT NULL AND loop_likely = 1 " + \
                "ORDER BY cond_cnt DESC, inp"
        exemplar.cursor.execute(sql)
        loop_likely_reasons = exemplar.cursor.fetchall()  # E.g., [('i1 % 5 == 0',), ('i1 % 3 == 0',)]
        loop_steps, loop_step_increments = exemplar.define_loop(loop_likely_reasons)
        expected = ['i1 % (i1-1) != 0', '(i1-1)>2'], \
                   [-1, -1, -2, -2, -3, -3, -4, -1, -1, -2, -2, -3, -3, -1, -1, -2, -1, -1]  # *All* increments.
        self.assertEqual(expected, (loop_steps, loop_step_increments))

    def test_gen_return1(self):  # 'True', 'i1 == 2'
        expected = "True"
        self.assertEqual(expected, exemplar.gen_return('i1 == 2'))

    def test_gen_return2(self):  # 'False', 'i1 == 1'
        expected = "False"
        self.assertEqual(expected, exemplar.gen_return('i1 == 1'))

    def test_gen_return3(self):  # '"input < 1 is illegal"', 'i1 < 1'
        expected = '"input < 1 is illegal"'
        self.assertEqual(expected, exemplar.gen_return('i1 < 1'))

    def test_gen_return4(self):
        with self.assertRaises(TypeError):  # TypeError: 'NoneType' object is not subscriptable
            exemplar.gen_return("won't be found")

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
        expected = """[all termination:
(final_cond, output, step_num, loop_step, loop_likely)
('i1 == 2', 'True', None, None, 0),
('(i1-1)==2', 'True', None, None, 1),
('i1 % (i1-2) == 0', 'False', None, None, 1),
('i1 < 1', '"input < 1 is illegal"', None, None, 0),
('i1 == 1', 'False', None, None, 0)]"""
        self.assertEqual(expected, exemplar.dump_table("termination"))

    def test_dump_table3(self):
        exemplar.mark_loop_likely()
        exemplar.remove_all_c_labels()
        exemplar.build_reason_evals()
        expected = """[all reason_evals:
(inp, reason, reason_explains_io, reason_value)
('2', 'i1 == 2', 1, 1),
('0', 'i1 == 2', 0, 0),
('1', 'i1 == 2', 0, 0),
('2', 'i1 < 1', 0, 0),
('0', 'i1 < 1', 1, 1),
('1', 'i1 < 1', 0, 0),
('2', 'i1 == 1', 0, 0),
('0', 'i1 == 1', 0, 0),
('1', 'i1 == 1', 1, 1)]"""
        self.assertEqual(expected, exemplar.dump_table("reason_evals"))

    def test_dump_table4(self):
        exemplar.mark_loop_likely()
        exemplar.remove_all_c_labels()
        exemplar.build_reason_evals()
        exemplar.find_safe_pretests()
        expected = """[all pretests:
(pretest, condition)
('i1 < 1', 'i1 == 2'),
('i1 == 1', 'i1 == 2'),
('i1 == 2', 'i1 < 1'),
('i1 == 1', 'i1 < 1'),
('i1 == 2', 'i1 == 1'),
('i1 < 1', 'i1 == 1')]"""
        self.assertEqual(expected, exemplar.dump_table("pretests"))

    """ Example tests:
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
