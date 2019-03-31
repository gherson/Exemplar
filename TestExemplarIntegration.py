import unittest, exemplar, MockCursor


class TestExemplarIntegration(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global mock_cursor
        mock_cursor = MockCursor.MockCursor()   # The advantage of MockCursor is that no is database required.

        """ Under maintenance
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
        exemplar.process_examples(examples)  # Inserts into the examples and termination tables.
    """

    def test_process_examples1(self):
        mock_cursor.mocking(1)  # exemplar.cursor is now mocked.
        example_lines = ["<Albert"]  # Processing this input should cause the following calls for INSERTion.
        exemplar.process_examples(example_lines)
        expected = [("INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)",
                     (5, 0, '__example__==0', 'truth')),
                    ("INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)",
                     (10, 0, 'Albert', 'in'))]
        assert expected == exemplar.cursor.get_actual(), "Got " + str(exemplar.cursor.get_actual())
        mock_cursor.mocking(0)  # Restore (unmock) cursor.

    def test_fill_conditions_table1(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.process_examples(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, loop_likely, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, None, for),
(20, 0, i1 == name, i1==name, i1, ==, name, None, None, assign),
(30, 0, i1 == secret, i1==secret, i1, ==, secret, None, None, assign),
(40, 0, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, None, for),
(55, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(60, 0, guess > secret, guess>secret, guess, >, secret, None, None, if),
(70, 0, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, None, for),
(85, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(90, 0, guess < secret, guess<secret, guess, <, secret, None, None, if),
(100, 0, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, None, for),
(115, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(120, 0, secret == guess, guess==secret, secret, ==, guess, None, None, if),
(125, 0, guess_count+1 == 3, guess_count+_==_, guess_count+1, ==, 3, None, None, assign)]"""
        # print(exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_fill_conditions_table2(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.process_examples(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, loop_likely, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, None, for),
(20, 0, i1 == name, i1==name, i1, ==, name, None, None, assign),
(30, 0, i1 == secret, i1==secret, i1, ==, secret, None, None, assign),
(40, 0, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, None, for),
(55, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(60, 0, guess > secret, guess>secret, guess, >, secret, None, None, if),
(70, 0, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, None, for),
(85, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(90, 0, guess < secret, guess<secret, guess, <, secret, None, None, if),
(100, 0, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, None, for),
(115, 0, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(120, 0, secret == guess, guess==secret, secret, ==, guess, None, None, if),
(125, 0, guess_count+1 == 3, guess_count+_==_, guess_count+1, ==, 3, None, None, assign),
(135, 1, 1 == __example__, _==__example__, 1, ==, __example__, None, None, for),
(150, 1, i1 == name, i1==name, i1, ==, name, None, None, assign),
(160, 1, i1 == secret, i1==secret, i1, ==, secret, None, None, assign),
(170, 1, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, None, for),
(185, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(190, 1, guess > secret, guess>secret, guess, >, secret, None, None, if),
(200, 1, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, None, for),
(215, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(220, 1, guess < secret, guess<secret, guess, <, secret, None, None, if),
(230, 1, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, None, for),
(245, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(250, 1, guess < secret, guess<secret, guess, <, secret, None, None, if),
(260, 1, 3 == guess_count, _==guess_count, 3, ==, guess_count, None, None, for),
(275, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(280, 1, guess > secret, guess>secret, guess, >, secret, None, None, if),
(290, 1, 4 == guess_count, _==guess_count, 4, ==, guess_count, None, None, for),
(305, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(310, 1, guess > secret, guess>secret, guess, >, secret, None, None, if),
(320, 1, 5 == guess_count, _==guess_count, 5, ==, guess_count, None, None, for),
(335, 1, i1 == guess, i1==guess, i1, ==, guess, None, None, assign),
(340, 1, guess > secret, guess>secret, guess, >, secret, None, None, if),
(355, 2, 2 == __example__, _==__example__, 2, ==, __example__, None, None, for)]"""
        # print(exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_fill_conditions_table3(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.process_examples(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, loop_likely, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, None, for)]"""
        # print(exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_fill_control_traces1(self):
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.process_examples(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.fill_control_traces()
        expected = """[all conditions:
        (el_id, example_id, condition, scheme, left_side, relop, right_side, loop_likely, control_id, condition_type)
        (5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, None, for)]"""
        print(exemplar.dump_table("control_traces"))
        # print(exemplar.dump_table("conditions"))
        #self.assertEqual(expected, exemplar.dump_table("conditions"))

    ''' Under maintenance
    def test_remove_all_c_labels1(self):
        # Reset db, put a few rows in examples table, and probe it before and after a call to remove_all_c_labels().

        exemplar.reset_db()  # Empty the database.
        # Simulating a 3-example .exem file with c labels in 2 rows, viz., 1 'output' field and 2 'reason' fields.
        exemplar.process_examples(["1\n", "False\n", "i1 == 1\n", "\n",
                                   "2\n", "i1 == 2c\n", "i1 == 2c\n", "\n",
                                   "3\n", "True\n", "i1 % (i1-1) != 0c, (i1-1)==2c\n", "\n"])
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

        def test_gen_tests1(self):
            expected = """def test_testing1(self):
        self.assertEqual(True, testing(2))

    def test_testing2(self):
        self.assertEqual(True, testing(3))

    def test_testing3(self):
        self.assertEqual(False, testing(4))

    def test_testing4(self):
        self.assertEqual(True, testing(5))

    def test_testing5(self):
        self.assertEqual(False, testing(6))

    def test_testing6(self):
        self.assertEqual("input < 1 is illegal", testing(0))

    def test_testing7(self):
        self.assertEqual(False, testing(1))

    def test_testing8(self):
        self.assertEqual(False, testing(1008))

    def test_testing9(self):
        self.assertEqual(True, testing(1009))

    """
            self.assertEqual(expected, exemplar.generate_tests("testing"))

        def test_gen_tests2(self):
            exemplar.reset_db()  # Empty the database.
            exemplar.process_examples(["2\n", "True\n", "i1 == 2c\n", "\n"])  # Simulating a 1-example .exem file.
            expected = """def test_testing1(self):
        self.assertEqual(True, testing(2))

    """
            self.assertEqual(expected, exemplar.generate_tests("testing"))

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

    '''
# if __name__ == '__main__':
#     unittest.main()