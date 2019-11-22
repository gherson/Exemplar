import unittest, exemplar, MockCursor


class TestExemplarIntegration(unittest.TestCase):
    """
    These unit tests are outdated.  (See TestExemplar.py. 2019-11-21)
    """

    @classmethod
    def setUp(cls):
        global mock_cursor
        mock_cursor = MockCursor.MockCursor()  # No database required.

        """ Under maintenance
        exemplar.reset_db()  # Unshared, in-memory database.

        # Replicates the example_lines table as it exists after loading prime_number.exem via readlines():
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
        exemplar.fill_example_lines(examples)  # Inserts into the examples and termination tables.
        """

    def test_process_examples1(self):
        mock_cursor.mocking(True)  # exemplar.cursor is now mocked.
        example_lines = ["<Albert"]  # Processing this input should cause the following calls for INSERT.
        exemplar.fill_example_lines(example_lines)  # When this function writes to cursor, it is held in mock_cursor.actual
        # and should look like this:
        expected = [("INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)",
                     (5, 0, '__example__==0', 'truth')),
                    ("INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)",
                     (10, 0, 'Albert', 'in'))]
        assert expected == exemplar.cursor.get_actual(), "Got " + str(exemplar.cursor.get_actual())
        mock_cursor.mocking(False)  # Restore (unmock) cursor.

    def test_process_examples_jokes(self):
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        expected = """[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, None, None),
(10, 0, What do you get when you cross a snowman with a vampire?, out, None, None),
(15, 0, , in, None, None),
(20, 0, Frostbite!, out, None, None),
(25, 0, , out, None, None),
(30, 0, What do dentists call an astronaut\\'s cavity?, out, None, None),
(35, 0, , in, None, None),
(40, 0, A black hole!, out, None, None),
(45, 0, , out, None, None),
(50, 0, Knock knock., out, None, None),
(55, 0, , in, None, None),
(60, 0, Who\\'s there?, out, None, None),
(65, 0, , in, None, None),
(70, 0, Interrupting cow., out, None, None),
(75, 0, , in, None, None),
(80, 0, Interrupting cow wh-MOO!, out, None, None)]"""
        self.assertEqual(expected, exemplar.dump_table("example_lines"))

    def test_process_examples_guess3(self):
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        expected = """[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, None, None),
(10, 0, Hello! What is your name?, out, None, None),
(15, 0, Albert, in, None, None),
(20, 0, name==i1, truth, None, None),
(25, 0, 4, in, None, None),
(30, 0, secret==i1, truth, None, None),
(35, 0, Well, Albert, I am thinking of a number between 1 and 20., out, None, None),
(40, 0, guess_count==0, truth, None, None),
(45, 0, Take a guess., out, None, None),
(50, 0, 10, in, None, None),
(55, 0, guess==i1, truth, None, None),
(60, 0, guess>secret, truth, None, None),
(65, 0, Your guess is too high., out, None, None),
(70, 0, guess_count == 1, truth, None, None),
(75, 0, Take a guess., out, None, None),
(80, 0, 2, in, None, None),
(85, 0, guess==i1, truth, None, None),
(90, 0, guess<secret, truth, None, None),
(95, 0, Your guess is too low., out, None, None),
(100, 0, guess_count==2, truth, None, None),
(105, 0, Take a guess., out, None, None),
(110, 0, 4, in, None, None),
(115, 0, guess==i1, truth, None, None),
(120, 0, guess==secret, truth, None, None),
(125, 0, guess_count + 1 == 3, truth, None, None),
(130, 0, Good job, Albert! You guessed my number in 3 guesses!, out, None, None)]"""
        # print(exemplar.dump_table("example_lines"))
        self.assertEqual(expected, exemplar.dump_table("example_lines"))

    def test_process_examples_guess4(self):
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        expected = """[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, None, None),
(10, 0, Hello! What is your name?, out, None, None),
(15, 0, Albert, in, None, None),
(20, 0, name==i1, truth, None, None),
(25, 0, 4, in, None, None),
(30, 0, secret==i1, truth, None, None),
(35, 0, Well, Albert, I am thinking of a number between 1 and 20., out, None, None),
(40, 0, guess_count==0, truth, None, None),
(45, 0, Take a guess., out, None, None),
(50, 0, 10, in, None, None),
(55, 0, guess==i1, truth, None, None),
(60, 0, guess>secret, truth, None, None),
(65, 0, Your guess is too high., out, None, None),
(70, 0, guess_count == 1, truth, None, None),
(75, 0, Take a guess., out, None, None),
(80, 0, 2, in, None, None),
(85, 0, guess==i1, truth, None, None),
(90, 0, guess<secret, truth, None, None),
(95, 0, Your guess is too low., out, None, None),
(100, 0, guess_count==2, truth, None, None),
(105, 0, Take a guess., out, None, None),
(110, 0, 4, in, None, None),
(115, 0, guess==i1, truth, None, None),
(120, 0, guess==secret, truth, None, None),
(125, 0, guess_count + 1 == 3, truth, None, None),
(130, 0, Good job, Albert! You guessed my number in 3 guesses!, out, None, None),
(135, 1, __example__==1, truth, None, None),
(140, 1, Hello! What is your name?, out, None, None),
(145, 1, John, in, None, None),
(150, 1, name==i1, truth, None, None),
(155, 1, 3, in, None, None),
(160, 1, secret==i1, truth, None, None),
(165, 1, Well, John, I am thinking of a number between 1 and 20., out, None, None),
(170, 1, guess_count==0, truth, None, None),
(175, 1, Take a guess., out, None, None),
(180, 1, 11, in, None, None),
(185, 1, guess==i1, truth, None, None),
(190, 1, guess>secret, truth, None, None),
(195, 1, Your guess is too high., out, None, None),
(200, 1, guess_count == 1, truth, None, None),
(205, 1, Take a guess., out, None, None),
(210, 1, 1, in, None, None),
(215, 1, guess==i1, truth, None, None),
(220, 1, guess<secret, truth, None, None),
(225, 1, Your guess is too low., out, None, None),
(230, 1, guess_count==2, truth, None, None),
(235, 1, Take a guess., out, None, None),
(240, 1, 2, in, None, None),
(245, 1, guess==i1, truth, None, None),
(250, 1, guess<secret, truth, None, None),
(255, 1, Your guess is too low., out, None, None),
(260, 1, guess_count==3, truth, None, None),
(265, 1, Take a guess., out, None, None),
(270, 1, 10, in, None, None),
(275, 1, guess==i1, truth, None, None),
(280, 1, guess>secret, truth, None, None),
(285, 1, Your guess is too high., out, None, None),
(290, 1, guess_count==4, truth, None, None),
(295, 1, Take a guess., out, None, None),
(300, 1, 9, in, None, None),
(305, 1, guess==i1, truth, None, None),
(310, 1, guess>secret, truth, None, None),
(315, 1, Your guess is too high., out, None, None),
(320, 1, guess_count==5, truth, None, None),
(325, 1, Take a guess., out, None, None),
(330, 1, 8, in, None, None),
(335, 1, guess==i1, truth, None, None),
(340, 1, guess>secret, truth, None, None),
(345, 1, Your guess is too high., out, None, None),
(350, 1, guess_count >= 5, truth, None, None),
(355, 1, Nope. The number I was thinking of was 3., out, None, None)]"""
        # print(exemplar.dump_table("example_lines"))
        self.assertEqual(expected, exemplar.dump_table("example_lines"))

    def test_fill_conditions_table_jokes(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, for)]"""
        # print("test_fill_conditions_table3", exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_fill_conditions_table_guess3(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, for),
(20, 0, i1 == name, i1==name, i1, ==, name, None, assign),
(30, 0, i1 == secret, i1==secret, i1, ==, secret, None, assign),
(40, 0, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, for),
(55, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(60, 0, guess > secret, guess>secret, guess, >, secret, None, if),
(70, 0, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, for),
(85, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(90, 0, guess < secret, guess<secret, guess, <, secret, None, if),
(100, 0, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, for),
(115, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(120, 0, secret == guess, guess==secret, secret, ==, guess, None, if),
(125, 0, guess_count+1 == 3, guess_count+_==_, guess_count+1, ==, 3, None, assign)]"""
        # print(exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_fill_conditions_table_guess4(self):
        # Processing this input should cause the following calls for INSERTion.
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, None, for),
(20, 0, i1 == name, i1==name, i1, ==, name, None, assign),
(30, 0, i1 == secret, i1==secret, i1, ==, secret, None, assign),
(40, 0, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, for),
(55, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(60, 0, guess > secret, guess>secret, guess, >, secret, None, if),
(70, 0, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, for),
(85, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(90, 0, guess < secret, guess<secret, guess, <, secret, None, if),
(100, 0, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, for),
(115, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(120, 0, secret == guess, guess==secret, secret, ==, guess, None, if),
(125, 0, guess_count+1 == 3, guess_count+_==_, guess_count+1, ==, 3, None, assign),
(135, 1, 1 == __example__, _==__example__, 1, ==, __example__, None, for),
(150, 1, i1 == name, i1==name, i1, ==, name, None, assign),
(160, 1, i1 == secret, i1==secret, i1, ==, secret, None, assign),
(170, 1, 0 == guess_count, _==guess_count, 0, ==, guess_count, None, for),
(185, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(190, 1, guess > secret, guess>secret, guess, >, secret, None, if),
(200, 1, 1 == guess_count, _==guess_count, 1, ==, guess_count, None, for),
(215, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(220, 1, guess < secret, guess<secret, guess, <, secret, None, if),
(230, 1, 2 == guess_count, _==guess_count, 2, ==, guess_count, None, for),
(245, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(250, 1, guess < secret, guess<secret, guess, <, secret, None, if),
(260, 1, 3 == guess_count, _==guess_count, 3, ==, guess_count, None, for),
(275, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(280, 1, guess > secret, guess>secret, guess, >, secret, None, if),
(290, 1, 4 == guess_count, _==guess_count, 4, ==, guess_count, None, for),
(305, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(310, 1, guess > secret, guess>secret, guess, >, secret, None, if),
(320, 1, 5 == guess_count, _==guess_count, 5, ==, guess_count, None, for),
(335, 1, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(340, 1, guess > secret, guess>secret, guess, >, secret, None, if),
(350, 1, guess_count >= 5, guess_count>=_, guess_count, >=, 5, None, if)]"""
        # print(exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_get_el_id_guess4(self):
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = 120
        self.assertEqual(expected, exemplar.get_line_item(100, 4))
        expected = 150
        self.assertEqual(expected, exemplar.get_line_item(80, 14))
        expected = 20
        self.assertEqual(expected, exemplar.get_line_item(115, -19))

    def test_get_unconditional_post_control_guess4(self):
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = ["out", "in", "assign"]  # in/out/assign/for
        self.assertEqual(expected, exemplar.get_unconditionals_post_control(100))

    def test_conditions_load_for_loops_jokes(self):
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, for0:0, for)]"""  # All correct
        # print("test_load_for_loops1", exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_conditions_load_for_loops_guess3(self):
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        expected = """[all conditions:
(el_id, example_id, condition, scheme, left_side, relop, right_side, control_id, condition_type)
(5, 0, 0 == __example__, _==__example__, 0, ==, __example__, for0:0, for),
(20, 0, i1 == name, i1==name, i1, ==, name, None, assign),
(30, 0, i1 == secret, i1==secret, i1, ==, secret, None, assign),
(40, 0, 0 == guess_count, _==guess_count, 0, ==, guess_count, for0:1, for),
(55, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(60, 0, guess > secret, guess>secret, guess, >, secret, None, if),
(70, 0, 1 == guess_count, _==guess_count, 1, ==, guess_count, for0:1, for),
(85, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(90, 0, guess < secret, guess<secret, guess, <, secret, None, if),
(100, 0, 2 == guess_count, _==guess_count, 2, ==, guess_count, for0:1, for),
(115, 0, i1 == guess, i1==guess, i1, ==, guess, None, assign),
(120, 0, secret == guess, guess==secret, secret, ==, guess, None, if),
(125, 0, guess_count+1 == 3, guess_count+_==_, guess_count+1, ==, 3, None, assign)]"""  # All looks good.
        # print("test", exemplar.dump_table("conditions"))
        self.assertEqual(expected, exemplar.dump_table("conditions"))

    def test_cbt_load_for_loops_jokes(self):
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 80, None, for0:0)]"""  # All correct
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def test_cbt_load_for_loops_guess3(self):
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 130, None, for0:0),
(for0:1_40, 0, 40, None, None, 65, None, for0:1),
(for0:1_70, 0, 70, None, None, 95, None, for0:1),
(for0:1_100, 0, 100, None, 120, 130, 130, for0:1)]"""  # All correct 5/9/19.
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def test_cbt_load_for_loops_guess4(self):
        # Processing this input should cause the following insert calls.
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 130, None, for0:0),
(for0:1_40, 0, 40, None, None, 65, None, for0:1),
(for0:1_70, 0, 70, None, None, 95, None, for0:1),
(for0:1_100, 0, 100, None, 120, 130, 130, for0:1),
(for1:0_135, 1, 135, None, None, 355, None, for1:0),
(for1:1_170, 1, 170, None, None, 195, None, for1:1),
(for1:1_200, 1, 200, None, None, 225, None, for1:1),
(for1:1_230, 1, 230, None, None, 255, None, for1:1),
(for1:1_260, 1, 260, None, None, 285, None, for1:1),
(for1:1_290, 1, 290, None, None, 315, None, for1:1),
(for1:1_320, 1, 320, None, 340, None, 355, for1:1),
(for1:1_320, 1, 320, 345, None, None, None, for1:1),
(for1:1_320, 1, 320, 355, None, None, None, for1:1)]"""
        # All correct.
        # print(exemplar.dump_table("control_block_traces"))
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def delme_test_control_conflict_guess5(self):
        example_lines = exemplar.from_file("guess5.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        expected = """"""
        print(exemplar.dump_table("example_lines"))
        self.assertEqual(expected, exemplar.dump_table("example_lines"))
        # get_control_conflicts(first_el_id: int, last_el_id_maybe: int) -> int:

    def test_fill_cbt_jokes(self):  # One FOR, no IFs, so expected == test_load_for_loops_jokes()'s expected1
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        exemplar.get_functions("jokes.exem")
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 80, None, for0:0)]"""  # All correct.
        # 5 is the correct first_el_id and 80 is the correct last_el_id
        # print(exemplar.dump_table("control_block_traces"))
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def test_fill_cbt_guess3(self):
        example_lines = exemplar.from_file("guess3.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        exemplar.get_functions("guess3.exem")
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 130, None, for0:0),
(for0:1_40, 0, 40, None, None, 65, None, for0:1),
(for0:1_70, 0, 70, None, None, 95, None, for0:1),
(for0:1_100, 0, 100, None, 120, 130, 130, for0:1),
(if0:0_60, 0, 60, None, None, 65, None, if0:0),
(if0:1_90, 0, 90, None, None, 95, None, if0:1),
(if0:2_120, 0, 120, None, None, 130, None, if0:2)]"""  #
        # Re: for0_5, 5 - 130 is correct. Re: for1_40 (guess_count), 40 is the correct first_el_id and 105 is the
        # correct last_el_id_1st_possible.
        # print(exemplar.dump_table("control_block_traces"))
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def test_fill_cbt_guess4(self):
        example_lines = exemplar.from_file("guess4.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        # print(exemplar.dump_table("example_lines"))
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        exemplar.get_functions("guess4.exem")
        expected = """[all control_block_traces:
(cbt_id, example_id, first_el_id, last_el_id_maybe, last_el_id_min, last_el_id, last_el_id_max, control_id)
(for0:0_5, 0, 5, None, None, 130, None, for0:0),
(for0:1_40, 0, 40, None, None, 65, None, for0:1),
(for0:1_70, 0, 70, None, None, 95, None, for0:1),
(for0:1_100, 0, 100, None, 120, 130, 130, for0:1),
(for1:0_135, 1, 135, None, None, 355, None, for1:0),
(for1:1_170, 1, 170, None, None, 195, None, for1:1),
(for1:1_200, 1, 200, None, None, 225, None, for1:1),
(for1:1_230, 1, 230, None, None, 255, None, for1:1),
(for1:1_260, 1, 260, None, None, 285, None, for1:1),
(for1:1_290, 1, 290, None, None, 315, None, for1:1),
(for1:1_320, 1, 320, None, 340, None, 355, for1:1),
(for1:1_320, 1, 320, 345, None, None, None, for1:1),
(for1:1_320, 1, 320, 355, None, None, None, for1:1),
(if0:0_60, 0, 60, None, None, 65, None, if0:0),
(if0:1_90, 0, 90, None, None, 95, None, if0:1),
(if0:2_120, 0, 120, None, None, 130, None, if0:2),
(if1:0_190, 1, 190, None, None, 195, None, if1:0),
(if1:1_220, 1, 220, None, None, 225, None, if1:1),
(if1:1_250, 1, 250, None, None, 255, None, if1:1),
(if1:0_280, 1, 280, None, None, 285, None, if1:0),
(if1:0_310, 1, 310, None, None, 315, None, if1:0),
(if1:0_340, 1, 340, 345, None, None, None, if1:0),
(if1:0_340, 1, 340, 355, None, None, None, if1:0),
(if1:2_350, 1, 350, None, None, 355, None, if1:2)]"""
        # print(exemplar.dump_table("control_block_traces"))
        self.assertEqual(expected, exemplar.dump_table("control_block_traces"))

    def test_add_control_info_to_example_lines_jokes(self):
        example_lines = exemplar.from_file("jokes.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        exemplar.get_functions("jokes.exem")
        expected = """[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, for0:0, None),
(10, 0, What do you get when you cross a snowman with a vampire?, out, None, for0:0),
(15, 0, , in, None, for0:0),
(20, 0, Frostbite!, out, None, for0:0),
(25, 0, , out, None, for0:0),
(30, 0, What do dentists call an astronaut\\'s cavity?, out, None, for0:0),
(35, 0, , in, None, for0:0),
(40, 0, A black hole!, out, None, for0:0),
(45, 0, , out, None, for0:0),
(50, 0, Knock knock., out, None, for0:0),
(55, 0, , in, None, for0:0),
(60, 0, Who\\'s there?, out, None, for0:0),
(65, 0, , in, None, for0:0),
(70, 0, Interrupting cow., out, None, for0:0),
(75, 0, , in, None, for0:0),
(80, 0, Interrupting cow wh-MOO!, out, None, for0:0)]"""  # All correct.
        # 5 is the correct first_el_id and 80 is the correct last_el_id
        # print(exemplar.dump_table("control_block_traces"))
        self.assertEqual(expected, exemplar.dump_table("example_lines"))

    def renamed_test_add_control_info_to_example_lines_guess5(self):
        example_lines = exemplar.from_file("guess5.exem")
        exemplar.reset_db()
        exemplar.fill_example_lines(example_lines)
        exemplar.remove_all_c_labels()
        exemplar.fill_conditions_table()
        exemplar.store_fors()
        exemplar.get_functions("guess5.exem")
        expected = """[all example_lines:
(el_id, example_id, line, line_type, control_id, controller)
(5, 0, __example__==0, truth, for0:0, None),
(10, 0, eg == 0, truth, for0:1, for0:0),
(15, 0, Hello! What is your name?, out, None, for0:1),
(20, 0, Albert, in, None, for0:1),
(25, 0, name==i1, truth, None, for0:1),
(30, 0, 4, in, None, for0:1),
(35, 0, secret==i1, truth, None, for0:1),
(40, 0, Well, Albert, I am thinking of a number between 1 and 20., out, None, for0:1),
(45, 0, guess_count==0, truth, for0:2, for0:1),
(50, 0, Take a guess., out, None, for0:2),
(55, 0, 10, in, None, for0:2),
(60, 0, guess==i1, truth, None, for0:2),
(65, 0, guess>secret, truth, if0:0, for0:2),
(70, 0, Your guess is too high., out, None, for0:2),
(75, 0, guess_count == 1, truth, for0:2, for0:1),
(80, 0, Take a guess., out, None, for0:2),
(85, 0, 2, in, None, for0:2),
(90, 0, guess==i1, truth, None, for0:2),
(95, 0, guess<secret, truth, if0:1, for0:2),
(100, 0, Your guess is too low., out, None, for0:2),
(105, 0, guess_count==2, truth, for0:2, for0:1),
(110, 0, Take a guess., out, None, for0:1),
(115, 0, 4, in, None, for0:1),
(120, 0, guess==i1, truth, None, for0:1),
(125, 0, guess==secret, truth, if0:2, for0:1),
(130, 0, guess_count + 1 == 3, truth, None, for0:1),
(135, 0, Good job, Albert! You guessed my number in 3 guesses!, out, None, for0:1),
(140, 0, eg == 1, truth, for0:1, if0:2),
(145, 0, Hello! What is your name?, out, None, for0:1),
(150, 0, John, in, None, for0:1),
(155, 0, name==i1, truth, None, for0:1),
(160, 0, 3, in, None, for0:1),
(165, 0, secret==i1, truth, None, for0:1),
(170, 0, Well, John, I am thinking of a number between 1 and 20., out, None, for0:1),
(175, 0, guess_count==0, truth, for0:2, for0:1),
(180, 0, Take a guess., out, None, for0:2),
(185, 0, 11, in, None, for0:2),
(190, 0, guess==i1, truth, None, for0:2),
(195, 0, guess>secret, truth, if0:0, for0:2),
(200, 0, Your guess is too high., out, None, for0:2),
(205, 0, guess_count == 1, truth, for0:2, for0:1),
(210, 0, Take a guess., out, None, for0:2),
(215, 0, 1, in, None, for0:2),
(220, 0, guess==i1, truth, None, for0:2),
(225, 0, guess<secret, truth, if0:1, for0:2),
(230, 0, Your guess is too low., out, None, for0:2),
(235, 0, guess_count==2, truth, for0:2, for0:1),
(240, 0, Take a guess., out, None, for0:2),
(245, 0, 2, in, None, for0:2),
(250, 0, guess==i1, truth, None, for0:2),
(255, 0, guess<secret, truth, if0:1, for0:2),
(260, 0, Your guess is too low., out, None, for0:2),
(265, 0, guess_count==3, truth, for0:2, for0:1),
(270, 0, Take a guess., out, None, for0:2),
(275, 0, 10, in, None, for0:2),
(280, 0, guess==i1, truth, None, for0:2),
(285, 0, guess>secret, truth, if0:0, for0:2),
(290, 0, Your guess is too high., out, None, for0:2),
(295, 0, guess_count==4, truth, for0:2, for0:1),
(300, 0, Take a guess., out, None, for0:2),
(305, 0, 9, in, None, for0:2),
(310, 0, guess==i1, truth, None, for0:2),
(315, 0, guess>secret, truth, if0:0, for0:2),
(320, 0, Your guess is too high., out, None, for0:2),
(325, 0, guess_count==5, truth, for0:2, for0:1),
(330, 0, Take a guess., out, None, for0:2),
(335, 0, 8, in, None, for0:2),
(340, 0, guess==i1, truth, None, for0:2),
(345, 0, guess>secret, truth, if0:0, for0:2),
(350, 0, Your guess is too high., out, None, if0:0),
(355, 0, guess_count >= 5, truth, if0:3, if0:0),
(360, 0, Nope. The number I was thinking of was 3., out, None, if0:0)]"""
        # print(exemplar.dump_table("example_lines"))
        self.assertEqual(expected, exemplar.dump_table("example_lines"))

    ''' Under maintenance
    def test_remove_all_c_labels1(self):
        # Reset db, put a few rows in examples table, and probe it before and after a call to remove_all_c_labels().

        exemplar.reset_db()  # Empty the database.
        # Simulating a 3-example .exem file with c labels in 2 rows, viz., 1 'output' field and 2 'reason' fields.
        exemplar.fill_example_lines(["1\n", "False\n", "i1 == 1\n", "\n",
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
            exemplar.fill_example_lines(["2\n", "True\n", "i1 == 2c\n", "\n"])  # Simulating a 1-example .exem file.
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