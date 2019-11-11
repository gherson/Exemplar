# License GPL. Email copyright 2019 holder gherson-@-snet dot-net for other terms.
import sys
import sqlite3  # See reset_db()
import re
from inspect import currentframe, getframeinfo  # For line #
import importlib  # To import and run the test file we create.
import unittest
from typing import List, Tuple, Dict, Any
import factoradic  # Credit https://pypi.org/project/factoradic/ Author: Robert Smallshire
import math

DEBUG = True  # True turns on testing and more feedback.
DEBUG_DB = False  # True sets database testing to always on.
pid = ''  # Tracks parent vs child forks.
SUCCESS = True

# (For speed, replace the db filename with ':memory:') (isolation_level=None for auto-commit.)
db = sqlite3.connect('exemplar.db', isolation_level=None, check_same_thread=False)  # 3rd arg is for repl.it
# For Row objects instead of tuples. Use row[0] or row['column_name'] (The objects are opaque to the debugger.)
#db.row_factory = sqlite3.Row
cursor = db.cursor()

"""
reverse_trace(file) reverse engineers a function from the examples in the named .exem `file`.

Version 3, started 1/26/2019, models state and user interaction. The input file has changed from examples of a single 
i/o[/reasons] triple to examples of an unbounded # of lines of <inputs, >outputs, and assertions. 
Version 2 finished 10/20/2018 can also generate a while loop. This version can also handle prime_number.exem. 
'reason's are now an unlimited # of conditions.  
Version 1 finished 3/25/2018 can generate one if/elif/else. This version correctly handles fizz_buzz.exem, guess2.exem, 
and leap_year.exem. These 'reason's are 0 or 1 conditions only.

Glossary:
code == Python code generated.
control_id == id of a control structure. Could be for0:0 from 'for' + example_id + ':' + control_count['for']
example == An imagined trace of a complete input/output interaction with a function to be generated, with added 
assertion/hints, provided by the user.
exem == The user's trace examples collected in a file of extension .exem.
line == An example_lines.line.
loop top == An example line that represents the re/starting of a loop. The first such top is the loop 'start'.
pretest == A 'reason' that serves as an IF or ELIF condition above other ELIF/s (in a single if/elif/else).
trace == record of a function execution, imagined in our case

Prefixes:
are_ == Boolean function
cbt_ == control_block_traces. E.g., cbt_id could be for0:0_40 from control_id + '_' + first_el_id.
ctlei_ == cbt_temp_last_el_ids table
el_ == example_line
fill_ == function that fills a table.
insert_ == function that inserts one table record per call.
is_ == Boolean function
store_ == function that lifts lower level data into a higher level table.
"""


def assertion_triple(truth_line: str) -> Tuple[any]:
    """
    Return the input as a standardized triplet of operand, relop, operand, if possible. Else, return Nones.
    Ie, (left_operand, relational_operator, right_operand) or (None, None, None).
    A valid identifier not of form i[0-9]+ is placed on the right in equality expressions.
    Double quotes are swapped for single.
    :database: not involved.
    :param truth_line:
    :return: The left operand, rel op, and right operand in truth_line (or 3 Nones)
    """
    # Qualify truth_line to be a simple relational comparison, or return Nones.
    t = truth_line
    if "==" not in t and "!=" not in t and '<' not in t and '>' not in t:
        return None, None, None  # None relational
    if " and " in t or " or " in t:
        return None, None, None  # Compound
    # if '%' in t or '*' in t or '+' in t or '/' in t or '-' in t:
    #     return None, None, None  # Also compound

    assertion = truth_line.translate(str.maketrans({'"': "'"}))  # Single quotes for consistency. todo ignore escaped "s
    # Create the relation triple: left_operand, relational_operator, right_operand.
    left_operand, relational_operator, right_operand = '', '', ''
    for char in assertion:  # Separate assertion into 3 parts, the left, relop, and right.
        if char in " \t\r\n":  # Ignore whitespace.
            continue
        elif char in "=<>!":
            relational_operator += char
        else:
            if relational_operator:  # Then we're up to the right-hand side of relation.
                right_operand += char
            else:
                left_operand += char
    if relational_operator == '==' and left_operand.isidentifier() and not re.match('i[0-9]+', left_operand):
        # Except for i[0-9]+ (input variable) names, put identifier in an equivalence on *right* for consistency.
        temporary = left_operand
        left_operand = right_operand
        right_operand = temporary
    return left_operand, relational_operator, right_operand


if DEBUG and __name__ == "__main__":
    assert ('input-1', '==', 'i') == assertion_triple("input-1==i")
    assert ('i1%400', '==', '0') == assertion_triple("i1%400==0")
    assert ('10', '==', 'guess') == assertion_triple("guess==10"), "We instead got " + str(
        assertion_triple("guess==10"))
    assert ('10', '>', '4') == assertion_triple("10>4"), "We instead got " + str(assertion_triple("10>4"))
    assert ('1', '==', 'guess_count') == assertion_triple("guess_count==1"), \
        "We instead got " + str(assertion_triple("guess_count==1"))
    assert ('3', '==', 'count+1') == assertion_triple('3==count + 1'), "\nExpected: '3', '==', 'count+1'\nActual: " + \
                                                                         str(assertion_triple("3==count + 1"))


def positions_outside_strings(string: str, character: str) -> List[int]:
    """
    Find and return the positions of the given character, unescaped and outside of strings, in the given string.
    :database: not involved.
    :param string:
    :param character: item to search for.
    :return list of `character` positions, [] if `character` not found:
    """
    positions = []
    open_string = False
    previous_char = ''
    i = 0
    for c in string:
        if c == '"' and previous_char != '\\':
            if not open_string:
                open_string = '"'  # Note we're in a "-delimited string.
            else:  # Already in a string.
                if open_string == '"':  # String closed.
                    open_string = False
        # Repeat above, for single quote.
        if c == "'" and previous_char != '\\':
            if not open_string:
                open_string = "'"
            else:
                if open_string == "'":
                    open_string = False
        if c == character and not open_string and previous_char != '\\':
            positions.append(i)
        previous_char = c  # Set up for next iteration.
        i += 1
    return positions


if DEBUG and __name__ == '__main__':
    assert [47, 51, 53, 54], positions_outside_strings("'# These ttt will be ignored' including \this but not tthese", 't')


def denude(line: str) -> str:
    """
    Remove any surrounding whitespace and line comment from `line` and return it.
    :database: not involved.
    :rtype: str
    :param line:  String to denude.
    :return:
    """
    hash_positions = positions_outside_strings(line, '#')
    if not hash_positions:  # Hash not found.
        return line.strip()
    else:
        return line[0:hash_positions[0]].strip()


if DEBUG and __name__ == '__main__':
    assert "code" == denude('  code  ')
    assert "code" == denude(" code # This should be removed. # 2nd comment ")
    assert "code \# This should NOT be removed." == denude(" code \# This should NOT be removed. # 1st comment ")
    assert "code '# This should NOT be removed.'" == denude(" code '# This should NOT be removed.' # 1st comment ")


def clean(examples: List[str]) -> List[str]:
    """
    Remove header and line comments, trim each line, and escape single quotes.
    :database: not involved.
    :param examples:  An exem file's contents.
    :return:
    """
    previous_line = ''
    triple_quote = "'''"
    result = []
    for line in examples:
        if len(line.lstrip()) and line.lstrip()[0] == '#':
            continue  # Skip full line comments.
        line = denude(line)  # (def denude() is above.)
        line = line.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes.

        if previous_line == '':  # Then on first line.
            if line == '':  # Skip initial blank lines.
                continue
            # assert line, "The examples must begin with a triple quoted comment or an actual example, not a blank."
            if line.startswith('"""') or line.startswith("'''"):
                previous_line = 'M'  # Will now skip lines until end of Multi-line string.
                if line.startswith('"""'):
                    triple_quote = '"""'  # Instead of single quotes.
                if len(line) > 3 and line.endswith(triple_quote):
                    previous_line = 'B'  # Pretending line is blank to expect an example to start on the next line.
                assert previous_line == 'M' or previous_line == 'B'
            else:  # We're at start with no header comment.
                previous_line = 'E'  # In an example.
                result.append(line)

        elif previous_line == 'M':  # Then still in the header comment.
            if line.endswith(triple_quote):
                previous_line = 'B'  # Pretending line is blank so as to expect an example on next line.

        elif previous_line == 'B':
            if not line:
                continue  # Allow a blank line after a blank line and after the multiline comment.
            # assert line, "An example, not another blank line, must follow blank lines and the header comment."
            previous_line = 'E'
            result.append(line)

        elif previous_line == 'E':
            if not line:
                previous_line = 'B'  # On the next line must start an example.
            result.append(line)  # Retain both examples and their delimiters, blank lines.
    if not line:
        result.pop(len(result) - 1)  # Remove last, blank line.
    return result


if DEBUG and __name__ == '__main__':
    assert ["code"] == clean(['  code  '])
    assert ["code"] == clean([" code # This should be removed. # 2nd comment "])
    assert ["code \# This should NOT be removed."] == clean([" code \# This should NOT be removed. # 1st comment "])
    # Why 3 backslashes? "'".translate(str.maketrans({"'": r"\'"})) returns only 2: "\\'"
    assert ['code \\\'# This should NOT be removed.\\\''] == clean([" code '# This should NOT be removed.' # 1st comment "])
    assert ["code"] == clean(["  ",'  code  ',''])
    assert ["code"] == clean([" code # This should be removed. # 2nd comment ","   "])
    assert ["code \# This should NOT be removed."] == clean([' '," code \# This should NOT be removed. # comment ",""])
    assert ["code \\\'# This should NOT be removed.\\\'"] == clean([''," code '# This should NOT be removed.' # comment ",""])
    assert ["co\\\'de"] == clean(["  co'de  "])


# c labels aren't being used. 2/20/19
def remove_c_labels(trace_line: str) -> str:
    """
    Created 2018-10-13.
    For each "c" found:
        Remove it if it is not quoted AND character to left is a digit AND character to right (if present) is not
        alphanumeric.
    Example: 'i1 % (i1-1) != 0c, (i1-1)>2c' --> 'i1 % (i1-1) != 0, (i1-1)>2'
    :database: not involved.
    :param trace_line:
    :return return_value The trace_line without its c labels:
    """
    if not hasattr(trace_line, '__iter__'):  # trace_line isn't iterable.
        return trace_line
    open_string = False
    check_for_alphanumeric = False
    return_value = ""
    previous_character = ""
    for character in trace_line:
        if character == '"' and previous_character != '\\':
            if not open_string:
                open_string = '"'  # Note we're in a "-delimited string.
            else:  # Already in a string.
                if open_string == '"':  # String closed.
                    open_string = False
        # Repeat above, for single quote.
        if character == "'" and previous_character != '\\':
            if not open_string:
                open_string = "'"
            else:
                if open_string == "'":
                    open_string = False

        if check_for_alphanumeric:
            if not character.isalnum():
                return_value = return_value[0:-1]  # Elide prior "c".

        if character == "c" and previous_character.isdigit():
            check_for_alphanumeric = True  # Check during next character's processing (or after loop if at end of
            # trace_line).
        else:
            check_for_alphanumeric = False

        previous_character = character  # Set up for next iteration.
        return_value += character  # return_value built one character at a time.

    # After loop.
    if check_for_alphanumeric:  # Last two characters were a digit and "c".
        return_value = return_value[0:-1]

    return return_value


if DEBUG and __name__ == '__main__':
    assert 'i1 % (i1-1) != 0, (i1-1)>2' == remove_c_labels('i1 % (i1-1) != 0c, (i1-1)>2c')


def get_last_condition(reason: str) -> str:
    """
    Find the last condition in reason. (This is useful because often it's a loop-termination condition.)
    E.g., 'i1 % (i1-1) != 0c, (i1-1)>2c' --> '(i1-1)>2c'
    :database: not involved.
    :param reason:
    :return the last condition in reason:
    """
    commas = positions_outside_strings(reason, ',')
    if not commas:  # `reason` does not have multiple conditions.
        return reason
    return reason[commas[-1] + 1:].strip()  # return last condition.


# Replaced with scheme() 2/12/19
def replace_increment(condition: str) -> str:
    """
    Find the increment in the given condition, eg, 23, and replace with underscore.
    Used to match iterations of the same loop step.  Example:
    Matching starts--v here. v--ends here.
          'i1 % (len(i1)-23) <= 0c'  ->
          'i1 % (len(i1)-_) <= 0c'
    todo Remove spaces not in quotes
    :database: not involved.
    :param condition:
    :return: 'condition' with the dec/increment replaced with underscore.
    """
    #                               #                           i1)-23) => i1)-_)
    regex = re.compile(r'('         # Start of capture group 1. (This is a metacharacter.)
                       r'i'         # i                         i
                       r'\d+'       # #                         1
                       r'\)*'       # optional right parens     )
                       r'\s?'       # optional space            
                       r'(\+|-)'    # +|-                       -
                       r'\s?'       # optional space            
                       r'(\+|-)?'   # optional +|-              
                       r')'         # End of capture group 1.   (Another metacharacter.)
                       r'\d+'       # #, ie, the inc            23
                       r'('         # Start of capture group 4.
                       r'\)*'       # optional right parens     )
                       r'\s?'       # optional space    
                       r'((==)|(!=)|(>=)|>|(<=)|<)?'  # optional relop, e.g., <=
                       r')')  # End of capture group 4. (Groups 2 and 3 are within group 1.)
    # Replace regex's matches in condition with capture groups 1 and 4 separated by underscore. Eg, i1)-23) => i1)-_)
    return regex.sub(r'\1_\4', condition)


def scheme(condition: str) -> str:
    """
    Replace the (non-c-suffixed) integers with underscore.
    And remove unquoted whitespace so that scheme('guess_count==0') == scheme('guess_count == 1')...
    Ie, replace any number not appended to a valid name and not followed immediately by a period or 'c'.
    Used to find instances of looping, i.e., to match iterations of the same loop step in the target function.
    The regex is from https://regexr.com/48b5v 2/12/19.
    :database: not involved.
    :param condition:
    :return:
    """
    # Protect the whitespace around "and" and "or".
    condition = condition.replace(" and ", "⋅and⋅")
    condition = condition.replace(" or ", "⋅or⋅")
    # Remove unquoted whitespace.
    for whitespace in ' \n\t\r':
        possibly_shortened = ''
        for i in range(len(condition)):
            if i not in positions_outside_strings(condition, whitespace):  # Then condition[i] is not unquoted whitespace,
                possibly_shortened += condition[i]  # so preserve it.
        condition = possibly_shortened  # Latest whitespace character (blank, \n, \t, or \r) removed.

    triple = assertion_triple(condition)  # Standardize assertion form.
    if triple[0] is not None:
        condition = triple[0] + triple[1] + triple[2]
    condition = condition.replace("⋅and⋅", " and ")
    condition = condition.replace("⋅or⋅", " or ")

    # Only reduce to underscore those integers not immediately following a valid Python identifier (via negative
    # lookbehind) AND not immediately before a 'c' or period (via negative lookahead).
    regex = re.compile(r'(?<![A-z_])\d+(?![\.c])')
    underscored = regex.sub(r'_', condition)
    return underscored


if DEBUG and __name__ == '__main__':
    assert "guess+_==_" == scheme('guess + 1 == 3'), scheme('guess + 1 == 3')
    assert scheme('guess_count==0') == scheme('guess_count == 1')
    assert 'guess_count1' == scheme('guess_count 1'), scheme('guess_count 1')
    assert 'guess_count1' == scheme('guess_count1')
    assert '_==guess_count' == scheme('guess_count == 1')
    assert '_==guess_count' == scheme('guess_count==1')
    assert '1c==guess_count' == scheme('guess_count == 1c')  # Leave constants alone.
    assert '1.==guess_count' == scheme('guess_count==1.')  # Leave floats alone.
    assert '_==guess_count' == scheme('1 == guess_count'), scheme('1 == guess_count')
    assert '_==guess_count' == scheme('1==guess_count')
    assert '1.==guess_count' == scheme('1. == guess_count')
    assert '1c==guess_count' == scheme('1c==guess_count')
    assert 'i1>_' == scheme('i1>4')
    assert '_<i1' == scheme('4<i1')
    assert "guess+_==_" == scheme(scheme('guess + 1 == 3')), scheme(scheme('guess + 1 == 3'))
    assert scheme('_==guess_count') == scheme(scheme('guess_count == 1'))
    assert 'guess_count1' == scheme(scheme('guess_count 1')), scheme(scheme('guess_count 1'))
    assert 'guess_count1' == scheme(scheme('guess_count1'))
    assert 'guess_count==_' == scheme(scheme('guess_count == 1')), scheme(scheme('guess_count == 1'))
    assert 'guess_count==_' == scheme(scheme('guess_count==1'))
    assert '1c==guess_count' == scheme(scheme('guess_count == 1c'))  # Leave constants alone.
    assert '1.==guess_count' == scheme(scheme('guess_count==1.'))  # Leave floats alone.
    assert 'guess_count==_' == scheme(scheme('1 == guess_count')), scheme(scheme('1 == guess_count'))
    assert 'guess_count==_' == scheme(scheme('1==guess_count'))
    assert '1.==guess_count' == scheme(scheme('1. == guess_count'))
    assert '1c==guess_count' == scheme(scheme('1c==guess_count'))
    assert 'i1>_' == scheme(scheme('i1>4'))
    assert '_<i1' == scheme(scheme('4<i1'))
    assert "i1%(len(i1)-_)<=0c" == scheme('i1 % (len(i1)-13) <= 0c'), scheme('i1 % (len(i1)-13) <= 0c')


def list_conditions(reason: str) -> List[str]:
    """
    Determine 'reason's list of conditions (in two steps to strip() away whitespace).
    :database: not involved.
    :param reason: str
    :return list of conditions, e.g., ["i1 % (i1-1) != 0c","(i1-1)==2c"]:
    """
    commas = positions_outside_strings(reason, ',')
    result = []
    start = 0
    for comma in commas:
        condition = reason[start: comma]
        result.append(condition.strip())
        start = comma + 1
    result.append(reason[start:].strip())  # Append last condition in 'reason'
    return result


if DEBUG and __name__ == '__main__':
    assert ['i1 % (i1-1) != 0c'] == list_conditions('  i1 % (i1-1) != 0c  ')
    assert ['i1 % (i1-1) != 0c', '(i1-1)=="hi, joe"'] == list_conditions('  i1 % (i1-1) != 0c  , (i1-1)=="hi, joe"  ')
    assert [''] == list_conditions('')


def insert_line(line_id: int, example_id: int, line: str) -> int:
    """
    Insert the given line into the database and return next line_id to use.
    :database: INSERTs example_lines.
    :param line_id: becomes an el_id
    :param example_id:
    :param line: a line or comma separated value from exem, with only leading < or > removed.
    :return: line_id incremented by five for each INSERT (# of conditions in a 'line' of 'truth').
    """
    if line.startswith('<'):
        line_type = 'in'
    elif line.startswith('>'):
        line_type = 'out'
    else:
        line_type = 'truth'  # True condition

    if line_type == 'in' or line_type == 'out':
        line = line[1:]  # Skip less/greater than symbol.
        cursor.execute('''INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)''',
                       (line_id, example_id, remove_c_labels(line), line_type))
        line_id += 5
    else:
        for assertion in list_conditions(line):
            cursor.execute('''INSERT INTO example_lines (el_id, example_id, line, line_type) VALUES (?,?,?,?)''',
                           (line_id, example_id, remove_c_labels(assertion), line_type))
            line_id += 5
    # cursor.execute('''SELECT * FROM example_lines''')
    # print("fetchall:", cursor.fetchall())
    return line_id


def store_examples(example_lines: List) -> None:
    """
    Go through .exem file to build example_lines table.
    :database: indirectly INSERTs example_lines.
    :param example_lines: all the lines from exem.
    """
    example_id = 0
    line_id = 5  # += 5 each insert call
    previous_line_blank = True  # If there was a previous line, it'd be blank.

    example_lines = clean(example_lines)
    example_lines.insert(0, "__example__==0")  # `line` 0
    for line in example_lines:

        if previous_line_blank:  # Then starting on a new example.
            assert line, "This line must be part of an example, not be blank."
            line_id = insert_line(line_id, example_id, line)
            previous_line_blank = False

        else:  # Previous line not blank, so current line can either continue the example or be blank.
            if not line:  # Current line is blank, signifying a new example.
                example_id += 1
                line_id = insert_line(line_id, example_id, "__example__==" + str(example_id))
                previous_line_blank = True
            else:  # Example continues.
                line_id = insert_line(line_id, example_id, line)


# also need to mark each condition as indicating the *start* of a loop or iteration, because an iterative condition
# can be repeated due to a loop in an enclosing scope.
# This whole thing may be redundant with the fill_*_table() functions... 3/9/19
def unused_mark_loop_likely() -> None:
    """
    Assign the example_lines.loop_likely and conditions.loop_likely columns per
    -1 default, 0==IF, 1==FOR, 2==WHILE  (These designations may be refined by if_or_while().)
    Old: To identify WHILE reasons, UPDATE examples.loop_likely and termination.loop_likely to 1 (true)
    to indicate those examples with 'reason's judged likely to indicate a loop in the target function.
    The criterion is simply, does the schematized(line) reappear in any 1 example?  if yes, mark all
    matches on schematized(line) in all examples as loop_likely.  This strategy can create false positives
    but is hopefully cost effective.
    loop_likely=-1-setting mark_sequences() is called at the end, leaving loop_likely's value 0, for selection,
    the default.
    todo CONFIRM The corresponding terminal conditions are then likewise set (see last cursor.execute() below).
    :database: SELECTs example_lines, conditions. UPDATEs example_lines, conditions.
    :return void:
    """
    # Identical 'out' messages within an example: loop likely==1 (not too meaningful: these are just print()s)
    cursor.execute('''SELECT example_id, line FROM example_lines WHERE line_type = 'out' 
                        GROUP BY example_id, line HAVING COUNT(*) > 1''')
    repeats = cursor.fetchall()
    for row in repeats:
        example_id, line = row  #                             vVv
        cursor.execute("UPDATE example_lines SET loop_likely = 1 WHERE line_type='out' AND example_id = ? AND line = ?",
                       (example_id, line))

    # Scheme repeats within an example with relop ==, an identifier, and a integer: also loop_likely==1 (for)
    cursor.execute('''SELECT example_id, scheme FROM conditions GROUP BY example_id, scheme HAVING COUNT(*) > 1''')
    rows = cursor.fetchall()
    for row in rows:  # These rows are scheme dupes, now see if they have relop ==, an identifier, and an integer.
        example_id, scheme = row
        scheme_qualified = False
        cursor.execute('''SELECT left_side, relop, right_side FROM conditions 
        WHERE example_id=? AND scheme=?''', (example_id, scheme))
        rows2 = cursor.fetchall()
        for row2 in rows2:
            left_side, relop, right_side = row2
            if relop == '==' and left_side.isdigit() and right_side.isidentifier():
                if not scheme_qualified:
                    scheme_qualified = True
                else:  # This is the second scheme in this example.
                    #                      vVv
                    cursor.execute("UPDATE example_lines SET loop_likely = 1 WHERE el_id IN ("
                                   "SELECT el_id FROM conditions WHERE example_id = ? AND scheme = ?)",
                                   (example_id, scheme))

    """
    Below produces:
    el_id_operators: {
'0|2|guess_count': [(90, '==')], 
'0|i1|secret':     [(20, '==')], 
'0|guess|secret':  [(50, '>'), (80, '<'), (110, '<'), (140, '>'), (170, 
'>'), (200, '>')], 
'0|i1|name':       [(10, '==')], 
'0|1|guess_count': [(60, '==')], 
'0|4|guess_count': [(150, '==')], 
'0|guess|i1':      [(45, '=='), (75, '=='), (105, '=='), (135, '=='), (165, 
'=='), (195, '==')], 
'0|3|guess_count': [(120, '==')], 
'0|0|guess_count': [(30, '==')], 
'0|5|guess_count': [(180, '==')]}
So the guess vs. secret relationship involves both IF and WHILE: the IFs are tested within the loop while their 
equality should be tested in the WHILE loop top. how can that be seen from examples?

    # WHILE (loop_likely==2) is likely if same scheme repeats with possible exception that in their terminal 
    appearance the relop can change.
    # Create a dict with key example_id | operand1 | operand2 and value [(el_id, relop), ...] where operand1
    # and operand2 are in alphabetical order.
    cursor.execute('''SELECT DISTINCT example_id, el_id, left_side, relop, right_side FROM conditions 
    ORDER BY example_id, el_id''')
    rows = cursor.fetchall()
    el_id_operators = {}
    for row in rows:
        example_id, el_id, left_operand, operator, right_operand = row
        if left_operand < right_operand:
            key = str(example_id) + '|' + left_operand + '|' + right_operand
        else:
            key = str(example_id) + '|' + right_operand + '|' + left_operand
        if key not in el_id_operators:
            el_id_operators[key] = [(el_id, operator)]
        else:
            el_id_operators[key].append((el_id, operator))
    print("el_id_operators:", str(el_id_operators))
    # for el_id_operator in el_id_operators:
    #     if len(el_id_operator) > 1:
    """

    # The remainder, i.e., unique assertion schemes /not/ equating an identifier to an input variable
    # (eg, /not/ guess==i1): loop_likely==0 (if/elif/else)
    cursor.execute('''SELECT el_id, line FROM example_lines WHERE loop_likely == -1 AND line_type = 'truth' ''')
    selections = []
    rows = cursor.fetchall()
    for row in rows:
        el_id, relation = row
        if not get_variable_name(relation):
            selections.append(el_id)
    if len(selections) > 0:  #                                vVv
        cursor.execute("UPDATE example_lines SET loop_likely = 0 WHERE el_id IN (" + ','.join('?' * len(selections)) +
                       ')', selections)

    # Put what we learned today into conditions table, to obviate JOINs.
    cursor.execute("""UPDATE conditions SET loop_likely = 
    (SELECT el.loop_likely FROM example_lines el WHERE conditions.el_id = el.el_id)""")

    return


# c labels aren't being used. 2/20/19
def remove_all_c_labels() -> None:
    # :database: SELECTs example_lines. UPDATEs example_lines.
    # The "c" labels are not needed. (Constants can have a "c" suffix in `reason` and
    # `output`.) Since they interfere with eval(), update each such record to remove_c_labels().

    cursor.execute('''SELECT el_id, line FROM example_lines WHERE line_type != 'in' ''')  # WHERE loop_likely = 0''')
    #non_looping = cursor.fetchall()
    for row in cursor.fetchall():  #non_looping:
        el_id = row[0]
        line = remove_c_labels(row[1])
        query = "UPDATE example_lines SET line = ? WHERE el_id = ?"
        cursor.execute(query, (line, el_id))


# Next time, note date of retirement so the old code can be found and stepped thru
def unused_build_reason_evals() -> None:
    """
    FOR IF CONDITION ORDERING
    Using the data of the `example_lines` table, build a `reason_evals` table that has columns for
    inp (text), `reason` (text), and reason_value (Boolean).
    reason_evals.reason_value shows T/F result of each inp being substituted for i1 in each `reason`.

    Loop step == Each condition of a loop_likely 'reason' maps to one of a limited # steps that is the target loop.
    Pretest == A 'reason' that serves as an IF or ELIF condition above other ELIF/s (in a single if/elif/else).
    Reason == The conditions the user expects will be true for the associated input in the target function ==
        SELECT line FROM example_lines WHERE line_type = 'truth'
    :database: SELECTs example_lines, reason_evals. INSERTs reason_evals, example_lines.
    """

    # All step 5 'reason's not involved in looping.
    cursor.execute("SELECT DISTINCT line FROM example_lines WHERE line_type = 'truth' AND loop_likely = 0") # AND step_id = 1")
    all_reasons = cursor.fetchall()

    # All step 0 inputs not involved in looping.
    cursor.execute("SELECT DISTINCT line FROM example_lines WHERE line_type = 'in' AND loop_likely = 0") # AND step_id = 5")
    all_inputs = cursor.fetchall()
        
    locals_dict = locals()  # Used in our exec() calls.

    if DEBUG:
        print("Function", getframeinfo(currentframe()).function, "line #", getframeinfo(currentframe()).lineno)
    for a_reason in all_reasons:
        a_reason = a_reason[0]  # There is only element 0.

        for an_inp in all_inputs:  # All inputs.
            an_inp = an_inp[0]
            if an_inp.isdigit():  # Let numbers be numbers (rather than text).
                an_inp = int(an_inp)

            # Substitute an_inp for i1 in a_reason and exec() to see if true or false. *** MAGIC ***
            #                            globals overrides locals (it doesn't usually)
            exec("reason = " + a_reason, {"i1": an_inp}, locals_dict)  # Eg i1 < 5 ?
            reason_value = locals_dict['reason']

            # Determine and store reason_explains_io, which indicates whether inp is associated with 'reason'
            # in the examples.
            cursor.execute('''SELECT * FROM example_lines reason, example_lines inp WHERE 
                                reason.example_id = inp.example_id and reason.line = ? AND inp.line = ? AND 
                                reason.loop_likely = 0 and inp.loop_likely = 0''', (a_reason, an_inp,))
            # These also should have been illustrated with an example:              ^^^^^^^^^^^^^^^^
            if cursor.fetchone():  
                # Yes, the current an_inp value shares an example with a_reason.
                reason_explains_io = 1  
            else:
                reason_explains_io = 0

            if DEBUG:
                print("input:", an_inp, " reason:", a_reason, " reason_explains_io:", reason_explains_io,
                      " reason_value:", reason_value)  # (Sqlite inserts Python None values as null.)

            # Store determinations.
            cursor.execute('''INSERT INTO reason_evals VALUES (?,?,?,?)''',
                           (an_inp, a_reason, reason_explains_io, reason_value))

    # EXPLAIN THE INPUTS WITHOUT EXPLANATION
    # Provide a   *** i1==input ***   'reason' for all reason-less examples whose input does not make any of the given
    # 'reason's true, i.e., those examples whose input does not make /any/ 'reason's true (even if there are no 'reason's)
    # fixme This should prolly go in another function.  And the above prolly needs to be re-run once new 'reason's are created.
    # 10/29/19 my archeology is inadequate to explain this.

    if 'a_reason' in locals():  # Select inputs that do not make any extant 'reason's true.
        # (Interestingly, locals_dict works here only if the line is breakpointed. 1/22/19)
        cursor.execute("SELECT inp FROM reason_evals GROUP BY inp HAVING max(reason_value)=0")

    # This whole method needs rethinking... todo
    else:  # There are /no/ 'reason's, so select /all/ inputs (from loop unlikely rows).
        cursor.execute("SELECT el_id, line FROM example_lines WHERE loop_likely = 0 AND line_type = 'in'")  #line as inp fixme

    special_cases = 0
    for row in cursor.fetchall():
        el_id = row[0]
        inp = quote_if_str(row[1])
        #special_cases.append(case[0])

        # Using inp's value, with the below modifications.
        cursor.execute("SELECT example_id, 'step_id' FROM example_lines WHERE el_id = ? ORDER BY example_id, "
                       "el_id, 'step_id'", (el_id,))  # First, fetch inp's el_id
        row_one = cursor.fetchone()
        el_id += 1
        example_id = row_one[0]
        reason = "i1 == " + inp
        step_id = row_one[1] + 1
        cursor.execute("""INSERT INTO example_lines (el_id, example_id, 'step_id', line, 'line_scheme', line_type) VALUES 
                            (?,?,?,?,?,?)""", (el_id, example_id, step_id, reason, scheme(reason), 'truth'))
            # "SET line = ('i1 == ' || line) WHERE line IN (" + ','.join('?' * len(special_cases)) + ')'
        special_cases += 1
    #print("I just gave ", cursor.execute(query, special_cases).rowcount, "example_lines reason ('i1 == ' || line)")
    print("I just gave", str(special_cases), "example_lines reason i1 == inp")

    if DEBUG:
        print()


def find_safe_pretests() -> None:
    """
    For if/elif/else generation.
    Build table pretests that shows for every reason A, each reason ("safe pretest") B that is *false* with *all* of A's
    example inputs (thereby allowing those inputs to reach A if B was listed above it in an if/elif).
    :database: SELECTs example_lines, reason_evals. INSERTs pretests.
    """

    # All if/elif/else reasons.
    cursor.execute('''SELECT DISTINCT example_id FROM example_lines WHERE line_type = 'truth' AND loop_likely = 0''')
    all_reason_eids = cursor.fetchall()

    # Here we find the safe pretests to each reason (again, those `reason`s false with all of its inputs).
    for reason_eid in all_reason_eids:
        reason_eid = reason_eid[0]  # The zeroth is the only element.

        sql = """
            SELECT DISTINCT reason AS potential_pretest FROM reason_evals WHERE 0 =     -- potential_pretest never  
                (SELECT count(*) FROM reason_evals re2 WHERE re2.reason = 
                    potential_pretest AND re2.reason_value = 1                          -- true 
                    AND re2.inp IN 
                (SELECT e.line FROM example_lines e WHERE e.line_type = 'in' AND        -- with input
                    e.example_id = ? AND e.loop_likely = 0))                            -- of reason_eid  
              """
        # Eg, 'i1 % 5 == 0' is a safe pretest to 'i1 % 3 == 0' (and v.v.) in Fizz_Buzz because example inputs for the
        # latter, such as 3 and 9, are *not* also evenly divisible by 5. And an input that is (ie, multiples of 15) is
        # never an example input for either.
        cursor.execute(sql, (reason_eid,))
        pretests = cursor.fetchall()  # Eg, ('i1 % 3 == 0 and i1 % 5 == 0',)
        for pre in pretests:  # Store each.
            pre = pre[0]
            cursor.execute("""INSERT INTO pretests VALUES (?,?)""", (pre, reason_eid))  # All columns TEXT


def debug_db() -> None:
    """
    Run the integration/database tests if DEBUG_DB or (DEBUG and it's been >1 hour).
    :return: None
    """
    cursor.execute("""CREATE TABLE IF NOT EXISTS history (prior_db_test_run INTEGER NOT NULL)""")

    global DEBUG_DB
    if False:  # DEBUG:
        hour_in_seconds = 60 * 60  # minutes in an hour * seconds in a minute
        cursor.execute("""SELECT STRFTIME('%s','now'), prior_db_test_run FROM history""")
        row = cursor.fetchone()
        if row:
            now, prior_db_test_run = row
            if (int(now) - prior_db_test_run) > hour_in_seconds:
                DEBUG_DB = True
                cursor.execute("""UPDATE history SET prior_db_test_run = STRFTIME('%s','now')""")
        else:
            DEBUG_DB = True  # (May have been True already.)
            cursor.execute("""INSERT INTO history (prior_db_test_run) VALUES (STRFTIME('%s','now'))""")
    if DEBUG_DB:
        # Run TestExemplarIntegration tests.
        TestClass = importlib.import_module('TestExemplarIntegration')
        suite = unittest.TestLoader().loadTestsFromModule(TestClass)
        test_results = unittest.TextTestRunner().run(suite)
        print("In TestExemplarIntegration there were", len(test_results.errors), "errors and",
              len(test_results.failures), "failures.")
        # Uncomment when Exemplar is no longer in development:
        # if (len(test_results.errors) + len(test_results.failures)) > 0:
        #     cursor.execute("""DELETE FROM history""")


def reset_db() -> None:
    """
    With the exception of table history, clear out the database. (A database is used for the advantages of SQL, not for multi-session persistence.)
    :database: CREATEs all tables.
    :return: None
    """
    # cursor.execute("""DROP TABLE IF EXISTS io_log""")
    # cursor.execute("""CREATE TABLE io_log (
    #                     iid ROWID,
    #                     entry TEXT NOT NULL)""")
    #sequential_function (line_number, line)

    # cursor.execute("""DROP TABLE IF EXISTS """)
    # cursor.execute("""CREATE TABLE  ()""")
    # cursor.execute("""CREATE UNIQUE INDEX  ON ()""")

    # Below top tables, down to loops, will be deleted.  3/8/19
    # iterations (1:1 with suspected loops) with columns python (eg, 'while i<4:', 'for i in range(5):', target_line to
    # place that code within the sequential program, and last_line, to note the # of the control block's last line.
    # cursor.execute("""DROP TABLE IF EXISTS iterations""")
    # cursor.execute("""CREATE TABLE iterations (
    #                     python TEXT NOT NULL,
    #                     target_line INTEGER NOT NULL,
    #                     last_line INTEGER NOT NULL)""")
    # cursor.execute("""CREATE UNIQUE INDEX ipt ON iterations(python, target_line)""")

    # selections (1:1 with suspected IFs) with columns python (eg, 'if i<5'), target_line to place that code within
    # the sequential program, an elif column to point to the selection_id of the next IF in the structure (if any).
    # For records housing the last IF in a selection structure, two more columns may be non-null: an else_line column
    # (holding, eg, 55, for line 55) to place an else in the sequential program, and last_line (required), to note where
    # the selection's block ends.
    # cursor.execute("""DROP TABLE IF EXISTS selections""")
    # cursor.execute("""CREATE TABLE selections (
    #                     python TEXT NOT NULL,
    #                     target_line INTEGER NOT NULL,
    #                     elif INTEGER,
    #                     else_line INTEGER,
    #                     last_line INTEGER)""")
    # cursor.execute("""CREATE UNIQUE INDEX spt ON selections(python, target_line)""")

    # This table is to note contiguous FOR blocks (iteration traces) so as to constrain the possible last_el_id's.
    # Controls can nest but not straddle (since an outer scope must enclose /all/ of any local block scopes that open
    # within it, an entire FOR loop must end before those controls w/an earlier first_el_id).
    cursor.execute('''DROP TABLE IF EXISTS for_loops''')
    cursor.execute('''CREATE TABLE for_loops (
                            control_id TEXT NOT NULL, -- Eg, 'for0:1'. Not unique because an outer loop can restart inner. Retained across examples. 
                            example_id INTEGER NOT NULL,
                            first_el_id INTEGER NOT NULL,
                            last_el_id INTEGER,  
                            period INTEGER, 
                            increment INTEGER
                            )''')
    cursor.execute('''CREATE UNIQUE INDEX flcf ON for_loops(control_id, first_el_id)''')

    # The last_el_id data herein provides all cbt end points for a given synthesis. (And no extra.) Note that
    # the cbt includes all trace blocks (iteration traces) of a loop, not just the first and last.
    cursor.execute("""DROP TABLE IF EXISTS cbt_temp_last_el_ids""")
    cursor.execute("""CREATE TABLE cbt_temp_last_el_ids (
                        cbt_id TEXT PRIMARY KEY, 
                        example_id INTEGER NOT NULL,
                        first_el_id INTEGER NOT NULL,
                        control_id TEXT NOT NULL,
                        last_el_id INTEGER NOT NULL)""")

    # 1-to-1 with *code* controls: if's and for's. (while's are todo.)
    #  Does not assign a last_el_id because it is usually unknown.
    cursor.execute("""DROP TABLE IF EXISTS controls""")
    cursor.execute("""CREATE TABLE controls (
                        control_id TEXT PRIMARY KEY,
                        example_id INTEGER NOT NULL, -- example of first occurrence
                        python TEXT NOT NULL,
                        first_el_id INTEGER NOT NULL,
                        indents INTEGER NOT NULL DEFAULT 1)""")  # Unused

    # Control block extent information to track all possible control endpoints.
    # 1 row for each block (eg, iteration) in the trace corresponding to a control (FOR or IF).
    # 1-to-1 with conditions table. (N.B. There are also non-control conditions -- the 'assign's.)
    # Many-to-1 with controls.control_id, as that represents target code, not a trace.
    cursor.execute('''DROP TABLE IF EXISTS control_block_traces''')
    cursor.execute('''CREATE TABLE control_block_traces (
                        cbt_id TEXT NOT NULL, -- Eg, 'for0:0_40'. Not unique due to last_el_id_maybe rows. 
                        example_id INTEGER NOT NULL,
                        first_el_id INTEGER NOT NULL, -- "first" for the block, not the control.
                        last_el_id_maybe INTEGER, -- These are manufactured to demarcate all possible last_el_ids.
                        last_el_id_min INTEGER, -- Earliest possible last line of the control trace. 
                        last_el_id INTEGER, -- Actual last line of the control trace. 
                        last_el_id_max INTEGER, -- Last possible last line of the control trace. (Duplicated across IF clauses.)
                        iteration INTEGER, -- 0 based global count (FOR only)
                        local_iteration INTEGER, -- 0 based local count (FOR only)
                        control_id TEXT NOT NULL)''')  # if#/for# (while# is todo)
    cursor.execute('''CREATE UNIQUE INDEX cbtfl ON control_block_traces(first_el_id, last_el_id_maybe)''')

    # 1 row for each comma-delimited assertion in lines of (ie, example_line of line_type) 'truth'.
    # Each row, most importantly types the condition and assigns it a control_id.
    cursor.execute("""DROP TABLE IF EXISTS conditions""")
    cursor.execute("""CREATE TABLE conditions (   
                        el_id INTEGER PRIMARY KEY,
                        example_id INTEGER NOT NULL,
                        condition TEXT NOT NULL,
                        scheme TEXT NOT NULL, 
                        left_side TEXT, 
                        relop TEXT, 
                        right_side TEXT, 
                        control_id TEXT, -- eg, 'for0:0'. (Unassigned 10/4/19)
                        condition_type TEXT, -- assign/if/for/while
                        FOREIGN KEY(el_id) REFERENCES example_lines(el_id))""")
                        #-- python TEXT)
                        #-- schematized(condition)
                        # --type TEXT NOT NULL, -- 'simple assignment', 'iterative', or 'selective'
                        # --intraexample_repetition INTEGER NOT NULL DEFAULT 0
    # lp todo For these repetitions, how many can be considered to be followed with the same # of code
    # lines of exactly 1 further indent? 2/10/19
    # satisfies INTEGER NOT NULL DEFAULT 0, -- Python code satisfies all examples?
    # approved INTEGER NOT NULL DEFAULT 0)""")  # Python code is user confirmed?

    # Many to 1 with trace lines, as comma-delimited assertions are broken out.
    cursor.execute('''DROP TABLE IF EXISTS example_lines''')
    cursor.execute('''CREATE TABLE example_lines (
                        el_id INTEGER PRIMARY KEY, -- will follow line order of given exem
                        example_id INTEGER NOT NULL,
                        line TEXT NOT NULL,
                        line_type TEXT NOT NULL, -- in/out/truth 
                        control_id TEXT, -- from conditions.control_id
                        controller TEXT -- the control_id most directly controlling this line, ie, the nearest, earlier 
                        -- control_id whose block hasn't ended. (Unused 10/4/19)
                        )''')

    # # # of `reason`s * # of inputs == # of records. To show how every `reason` evaluates across every example input.
    # # For if/elif/else generation.
    # cursor.execute('''DROP TABLE IF EXISTS reason_evals''')
    # cursor.execute('''CREATE TABLE reason_evals(
    #                     inp TEXT NOT NULL,
    #                     reason TEXT NOT NULL,
    #                     reason_explains_io INTEGER NOT NULL, -- 1 iff this inp has this reason in examples (unused)
    #                     reason_value INTEGER NOT NULL)''')
    # cursor.execute('''CREATE UNIQUE INDEX reir ON reason_evals(inp, reason)''')
    #
    # # # of 'reason's * (# of 'reason's - 1) == # of records.  To show
    # # for every `reason`, those (single condition) reasons that can be listed above it in an elif.
    # cursor.execute('''DROP TABLE IF EXISTS pretests''')
    # cursor.execute('''CREATE TABLE pretests(
    #                     pretest TEXT NOT NULL,
    #                     condition TEXT NOT NULL)''')
    # cursor.execute('''CREATE UNIQUE INDEX ppc ON pretests(pretest, condition)''')


# Unused but may be better than the simpler approach in assertion_triple(). 2/20/19
def unused_find_rel_op(condition: str) -> Tuple:
    """
    Return the position of condition's relational operator.
    :database: not involved.
    :param condition:
    :return two string positions, or () if a rel op is not found
    """
    open_string = False
    previous_character = ""
    i = 0
    start = 0
    stop = 0
    for character in condition:
        if character == '"' and previous_character != '\\':
            if not open_string:
                open_string = '"'  # Note we're in a "-delimited string.
            else:  # Already in a string.
                if open_string == '"':  # String closed.
                    open_string = False
        # Repeat above, for single quote.
        if character == "'" and previous_character != '\\':
            if not open_string:
                open_string = "'"
            else:
                if open_string == "'":
                    open_string = False
        if not start:  # Looking for >, <, ==, <=, >=, and !=.
            if not open_string and (character == '>' or character == '<' or character == '=' or character == '!'):
                start = i
        else:  # Now looking for end of relational operator.
            if character == '=':  # This is only legit 2nd character for a relational operator.
                stop = i + 1
            else:  # Must be a > or <.
                if condition[i-1] != '>' and condition[i-1] != '<':
                    sys.exit("Misplaced", condition[i-1], "character found in condition", condition)
                stop = i
            break
        i += 1

    if not stop:
        return ()
    return start, stop


"""if DEBUG and __name__ == '__main__':
    assert (18, 20) == find_rel_op("i1 % (len(i1)-13) <= 0c")
    assert (18, 19) == find_rel_op("i1 % (len(i1)-13) < 0c")
    assert () == find_rel_op("")
    assert (12, 14) == find_rel_op("i1 % (i1-1) != 0c")"""


# Unused because predates move to new </>/assertion format. 2/20/19
def unused_same_step(loop_step: str, condition: str) -> int:
    """
    Determine whether condition1 and condition2 represent the same loop step of a 'reason' while-loop, which they do iff
    o they share an identical side,
    o their non-identical sides vary at most in variable-value/s (Is it better to say dec/increment?).
    E.g., same_step("i1 % (i1-_) != 0", "i1 % (i1-1) != 0") --> True
    :database: not involved.
    :param loop_step: a condition from loop_steps
    :param condition: current condition
    #:param last_condition: was needed when: last condition's rel op must change to terminate loop
    :return Boolean:
    ""
    # opposite_rel_op = {'==': '!=', '!=': '==', '>': '<=', '<=': '>', '<': '>=', '>=': '<'}

    pos1 = find_rel_op(loop_step)

    pos2 = find_rel_op(condition)
    if not pos1:
        print("No relational operator found in", loop_step)
    if not pos2:
        print("No relational operator found in", condition)

    # rel1 = condition1[pos1[0]:pos1[1]]
    # rel2 = condition2[pos2[0]:pos2[1]]
    # my_split disproved 10/23/18 old "hurdle 1", viz., if rel1 == rel2 or (last_condition and rel1 != rel2)
    if loop_step[0:pos1[0]] == condition[0:pos2[0]]:  # Left sides identical.
        return scheme(loop_step[pos1[1]:]) == scheme(condition[pos2[1]:])  # Check other side.
    elif loop_step[pos1[1]:] == condition[pos2[1]:]:  # Right sides identical.
        return scheme(loop_step[0:pos1[0]]) == scheme(condition[0:pos2[0]])  # Check "    "
    return False
    """

# Unused because predates move to new </>/assertion format. 2/20/19
def unused_get_inc_int_pos(condition: str) -> Tuple[int, int]:
    """
    Find and return the start and stop+1 positions of the increment integer. Example: i1 % (i1-1) != 0c --> (9, 10)
    :database: not involved.
    :param condition: non-schematized
    :return _pos: (start, stop+1) tuple of positions of given condition's increment integer. Or () iff missing.
    """
    # Collect any initial underscore positions into _positions.
    start = 0
    _positions = []
    for i in range(0, condition.count('_')):
        _positions.append(condition.find('_', start))
        start = _positions[-1] + 1

    schema = scheme(condition)  # Replaces dec/increment in condition with a single underscore.

    if schema.count('_') < 1:
        return ()  # scheme() found no dec/increment value in condition.  ERROR?

    # Underscores initially found?  1 of the removed values is multiple digits long?
    if len(_positions) > 0 and len(schema)+1 < len(condition):
        # Code a fix if not a very rare situation.
        print("get_increment() cannot handle abs(increments) >9 when condition has pre-existing underscores")
        sys.exit()

    if schema.count('_') > (len(_positions) + 1):
        print("Error: multiple increments found in", condition)
        sys.exit()

    # Build return value from the digit/s found at the position of the new _.
    start = 0
    for i in range(0, schema.count('_')):  # Keep checking underscores
        _pos = schema.find('_', start)     # until new one found.
        if _pos not in _positions:  # *********** NEW _ POSITION *****
            start = _pos
            while condition[_pos].isdigit():
                _pos += 1
            return start, _pos      # *********** RETURN ***********
        start = _pos + 1
    return ()  # No increment found.  ERROR?


# Unused because predates move to new </>/assertion format. 2/20/19
def unused_get_increment(condition: str) -> int:
    """
    Find and return the inc/dec-rement in the given condition.
    E.g., 'i1 % (i1-1) != 0c' --> -1
    :database: not involved.
    :param condition: str
    :return signed increment, 0 if none found:
    ""
    _pos = get_inc_int_pos(condition)
    if not _pos:  # _ not found
        return 0
    increment = int(condition[_pos[0]:_pos[1]])

    # Determine the increment's sign.
    sign = 1
    schema = scheme(condition)
    i_pos = schema.rfind('i', 0, _pos[0])  # Find rightmost 'i' from schema[0] to schema's (replaced) increment.
    signs = []
    for j in range(i_pos, _pos[0]):
        if schema[j] == '+' or schema[j] == '-':
            signs.append(schema[j])
    if len(signs) > 2:
        print("Error: >2 +/- signs found in schema substring", schema[i_pos: _pos[0]+1])
        sys.exit()
    elif len(signs) == 0:
        print("Error: No +/- signs found in schema substring", schema[i_pos: _pos[0]+1])
        sys.exit()
    elif len(signs) == 1:
        if signs[0] == '-':
            sign = -1
    else:
        if signs[0] != signs[1]:  # + - or - +
            sign = -1

    return sign * increment
    """

# Unused because predates move to new </>/assertion format. 2/20/19
def unused_define_loop() -> Tuple[List, List]:
    """
    Decipher the loop by noting its sequence of example lines. Define and return loop_steps, loop_step_increments and
    update the ??termination table.
    # todo figure out what to do about steps not given, e.g., (i1-1)>2c, if printing step errors isn't enough.
    :database: SELECTs example_lines. UPDATEs termination.
    :param None
    :return loop_steps, loop_step_increments:
    ""
    loop_width = 0
    first_condition = ""
    loop_steps = []  # Are here built.
    loop_step_increments = []  # The change to the loop control variable from the prior iteration
    ## before each condition's relational operator (includes *all* reasons (perhaps uselessly)).

    cursor.execute("SELECT * FROM example_lines ORDER BY example_id, el_id")
    rows = cursor.fetchall()
    i = 0  # row #
    for row in rows:  # Break when reach likely end of loop.
        el_id, example_id, step_id, line, loop_likely, line_type = row
        if example_id != preceding_example_id:
            if first_loop_start != -1:  # Then a loop just ended,
                pass  # Find most likely sequential target function (STF) correlate.
            # Reset per-example variables.
            first_loop_start = -1
        if first_loop_start == -1 and loop_likely != 1:  # Each example, skip pre-loop lines.
            continue
        if first_loop_start == -1:
            first_loop_start = i

        reason = reason[0]  # 0 is the only key.
        last_condition_of_reason = False
        i = 0  # Count of conditions examined in this 'reason'.
        conditions = list_conditions(reason)
        for condition in conditions:
            increment = get_increment(condition)

            if i == (len(conditions) - 1):
                last_condition_of_reason = True
            if not loop_width:  # Still width-finding.
                if not first_condition:
                    first_condition = condition  # Needed to determine when we've cycled back to loop start.
                    loop_steps.append(condition)  # Save condition.
                else:
                    if same_step(first_condition, condition):  # Loop defined!: We've cycled back to loop start.
                        loop_width = i  # Note # of steps in while-loop. (i is correct because we're 1 past.)
                    else:  # Widen loop.
                        loop_steps.append(condition)

            if loop_width and i > loop_width:  # > needed because i resets to zero with each 'reason'.
                # While-loop already plumbed, so SANITY CHECK the `condition`, two ways.

                # 1. Each loop step must, aside from its specific increment, match its analogue in the initial loop.
                if not same_step(loop_steps[i % loop_width], condition):
                    # E.g., on step (ordinal #) 2 of a width (cardinal #) 2 loop, we must be back on step 0.
                    print("Error: Step type", scheme(loop_steps[i % loop_width]), "expected, step",
                          scheme(condition), "detected. i, loop_width, and loop_steps:\n", str(i), str(loop_width),
                          "\n", loop_steps)
                    sys.exit()

                # 2. In this single reason, the latest increment change (for this step) must equal the initial
                # increment (for this step).
                # E.g., -2    -                     [2 - 2]                !=                     [2 % 2]        at i==2
                if (increment - loop_step_increments[i - len(loop_steps)]) != loop_step_increments[i % len(loop_steps)]:
                    print("Error: Increment", increment, "is unexpected")
                    print("loop_step_increments[i - len(loop_steps)] =", loop_step_increments[i - len(loop_steps)])
                    print("loop_step_increments[i % len(loop_steps)] =", loop_step_increments[i % len(loop_steps)])
                    print("And as a result,", str(increment - loop_step_increments[i - len(loop_steps)]), "!=",
                          loop_step_increments[i % len(loop_steps)],
                          "per\n (increment - loop_step_increments[i - len(loop_steps)]) != loop_step_increments[i % len(loop_steps)]")
                    sys.exit()

            # Once for each final_cond, note its loop_step and step_num in the terminations table.
            if last_condition_of_reason:
                # Sanity check.
                if loop_width == 0:
                    print("Error: loop_width is zero at last condition. i =", i, "loop_steps =", loop_steps, "reason =",
                          reason)
                    sys.exit()
                query = '''UPDATE termination SET step_num = ?, loop_step = ?
                            WHERE loop_step IS NULL AND final_cond = ?'''
                print("query =", query)
                cursor.execute(query, (str(i % loop_width), loop_steps[i % loop_width], get_last_condition(reason)))

            loop_step_increments.append(increment)
            i += 1

        preceding_example_id = example_id
        i += 1  # row #
    return loop_steps, loop_step_increments
    """


def quote_if_str(incoming: str) -> Any:
    """
    Quote incoming and escape any embedded single quotes with backslash.
    :database: not involved.
    :param incoming:
    :return: incoming wrapped in single quotes, unless it is a number, "True", or "False"
    """
    if incoming.isnumeric() or incoming == 'True' or incoming == 'False':
        return incoming  # Hands off a number or Boolean.

    escaped = incoming.translate(str.maketrans({"'": r"\'"}))  # Escape any single quotes.
    return "'" + escaped + "'"


# Unused after switching back to i1-style references.
def unused_variable_name_of_value(truth_line: str, value: any) -> str:
    """
    Return truth_line's name for (i.e., equivalence to) `value`, if any.
    Eg, variable_name_of_value('first=="Albert"', 'Albert') => 'first'
    :database: not involved.
    :param truth_line:
    :param value:
    :return: truth_line's name for the variable storing `value`. Or '' if there's no match on `value`.
    """
    relation = assertion_triple(truth_line)
    # If relation hints at a variable name, return that name.
    if relation[1] == '==' and relation[0] == value and \
            re.match('[A-z]', relation[2]):  # Identifiers must begin with a letter.
        return relation[2]  # The identifier (eg, first) that `relation` says is equal to `value`.
    return ''


def get_variable_name(truth_line: str, input_variable: str = 'i[0-9]+') -> str:
    """
    Return truth_line's name for (i.e., equivalence to) the input_variable, if any.
    :database: not involved.
    :param truth_line:
        :param input_variable: 'i[0-9]+' by default.
    :return: what truth_line says is a name equal to input_variable, or '' if no match.
    """
    condition = assertion_triple(truth_line)  # (a non-input variable name, if any, will be in condition[2].)
    # If relation "hints" at a variable name, return that name.
    if condition[1] == '==' and "Equivalence relation" and \
            re.match(input_variable, condition[0]) and "input variable name, eg, i1, will be on the left" and \
            re.match('[A-z]', condition[2]):  # Identifiers must begin with a letter.
        return condition[2]  # Return that identifier asserted equal to input_variable.
    return ''
    # todo Ensure input variables on both sides of an equivalence do not cause a problem. 2/10/19


if DEBUG and __name__ == "__main__":
    assert 'guess' == get_variable_name('guess==i1')
    assert '' == get_variable_name('     guess==1')
    assert 'guess' == get_variable_name('guess==i1', 'i1')
    assert '' == get_variable_name('   guess == i1', 'i5')
    assert 'guess' == get_variable_name('guess==i5', 'i5')
    assert 'guess' == get_variable_name('guess==i5')


def store_code(code):
    code_lines, line_id = [], 0
    for line in code.split('\n'):
        code_lines.append((line_id, line))
        line_id += 5
    cursor.executemany("INSERT INTO sequential_function (line_id, line) VALUES (?, ?)", code_lines)


# unused
def unused_get_range(first_el_id: int, line: str) -> Tuple[int, int]:
    """
    old:
    Help gauge whether first_el_id defines the first value of a FOR loop variable by returning that variable's first
    and last value over the rows where it increments. Also return the likely loop's last row id, and the pattern of
    line_type's over the loop.
    :database: SELECTs conditions, example_lines (indirectly).
    :param first_el_id:  # Eg, 30
    :param line:  # Eg, 'guess_count==0'
    :return: (first value of loop control variable, and its last (at loop exit)), last_el_id, loop_pattern
    """
    # Eg, for line 'guess_count==1', return *0, 3* if the first match on line_scheme 'guess_count == _' in
    # conditions.line is value 'guess_count == 0' and the last match is 'guess_count == 2' (with an increment
    # of 1 between guess_count's values).
    # todo Determine if the end points differ between examples, and use the variable/s concerned instead of constants.
    # todo Return False? if pattern found appears to rule out a for loop. 3/6/19

    # todo Below is unnecessary for the for0 loops: we just GROUP BY example_id. But we should also always consider
    # inner loop repetitions only, otherwise, the repetition of a given scheme may be due to the loop it is nested in.
    # cursor.execute("SELECT el_id FROM conditions WHERE control_id='for0'")
    # rows = cursor.fetchall()  # Would also work: c.scheme='_==__example__'
    # example_ranges = []  # First element should be (el_id) 0, and the 3rd element minus the 2nd should be 5.
    # for row in rows:     # More importantly, example_ranges allows every el_id to be mapped to its example.
    #     example_ranges.append(row[0])

    # Assuming scheme is of a FOR loop, determine the example garnering the most iterations.
    count, example_id = most_repeats_in_an_example(assertion_scheme=line)
    assert count > 0, "get_range() found zero conditions matching scheme " + scheme(line)

    # If the iterations are >1, note the last_value and last_el_id_top.
    cursor.execute("SELECT el_id, condition FROM conditions WHERE scheme=? AND example_id=? ORDER BY el_id",
                   (scheme(line), example_id))
    rows = cursor.fetchall()
    first_value, last_value, increment = None, None, None
    for row in rows:
        row_el_id, condition = row
        row_int = int(assertion_triple(condition)[0])  # Eg, 'guess_count==0' => 0
        if first_value is None:  # Our first iteration
            first_value = row_int  # Eg, value('guess_count==0') => 0
            assert row_el_id == first_el_id, "The first el_id with a scheme equal to that of the given condition, " + \
                line + ", is " + str(row_el_id) + " and not " + str(first_el_id) + " as expected, implying that " + \
                "this call should have been filtered out."
            if len(rows) == 1:  # A degenerate "loop".
                return (first_value, first_value), row_el_id, 't'
        elif increment is None:  # Our second iteration
            increment = row_int - first_value
        # Below check commented out because it fails with inner loops and the check is done better anyway in fill_control_block_traces(). 3/3/19
        # else:
        #     if row_int - last_value != increment:
        #         exit("Line " + condition + "'s expected increment " + str(increment) + " was instead " + str(row_int - last_value))
        last_value = row_int
        #last_el_id_top = row_el_id  # '_top' because we are looking only at example_lines matching given scheme.

    return first_value, last_value + increment  # Old: Eg, (0, 2 + 1), 115, 'toitto, toittt'


# unused
def unused_if_or_while(el_id: int, condition: str, second_pass: int) -> str:
    """
    Determine what kind of control structure the given condition represents, based on conditions.loop_likely
    column and not much else...
    i will improve this now....
    We can refine the loop_likely designation because when second_pass is true there's more information stored.
    :database: SELECTs conditions.
    :param el_id:
    :param condition:
    :param second_pass:
    :return: an if/elif/else or while command's first line
    """
    # guess4.exem shows this as too crude, so no WHILEs for now... I believe this all needs to go in the generate-and-
    # test pot... 3/10/19
    # Return "while " + condition + ':' if 'condition' recurs in an example.
    # cursor.execute("SELECT COUNT(*) FROM conditions WHERE condition = ? AND el_id >= ? ORDER BY el_id",
    #                (condition, el_id))
    # if most_repeats_in_an_example(assertion=condition)[0] > 1:
    #     return "while " + condition + ':'

    if not second_pass:
        return "if " + condition + ':'
    else:
        """Re: IF processing: 
        IF clauses (alone) are open to re-ordering, and switching between if/elif/else.  As with for-loops, the 
        last_el_id field values are shared (duplicated) across the clauses of a single IF.  3/2/19
        A series of IFs == one IF/ELIF if their conditions are all mutually exclusive. 
        In each example, E can only count on the user providing the true IF clause of an IF/ELIF. On the + side, this  
        helps differentiate a series of IFs from an IF/ELIF. 3/5/19"""

        # Combine IF conditions into what should be clauses of the same IF and
        # decide their elif order (which will not necessarily preserve the conditions'
        # given order, of course).
        # For now, we simply gather all IF-type conditions within el_id's most
        # nested loop (via indent), and assume those with conditions (todo) mutually exclusive with el_id's
        # condition are the conditions of the same IF structure. todo Improve, eg, order via the examples.
        # todo THIS indent business doesn't make sense: the conditions aren't indented! and, catch-22, the code can't be
        # correctly indented until this function does its job... *****fixme somehow
        indent = len(condition) - len(condition.lstrip())  # condition's indent

        # Find first_clause_of_if
        cursor.execute("""SELECT el_id, condition FROM conditions 
                           WHERE loop_likely = 0 AND el_id < ? ORDER BY el_id DESC""", (el_id,))
        earlier_rows = cursor.fetchall()
        first_clause_of_if = el_id
        for row in earlier_rows:
            row_el_id, row_condition = row
            row_indent = len(row_condition) - len(row_condition.lstrip())
            if row_indent != indent:
                break
            first_clause_of_if = row_el_id

        # (last_clause_of_if unused as of 2/19/19. todo Use to implement 'else:')
        cursor.execute("""SELECT el_id, condition FROM conditions 
                           WHERE loop_likely = 0 AND el_id > ? ORDER BY el_id""", (el_id,))
        later_rows = cursor.fetchall()
        last_clause_of_if = el_id
        for row in later_rows:
            row_el_id, row_condition = row
            row_indent = len(row_condition) - len(row_condition.lstrip())
            if row_indent != indent:
                break
            last_clause_of_if = row_el_id

        if el_id == first_clause_of_if:
            return "if " + condition + ':'
        else:
            return "elif " + condition + ':'


# unused
def unused_get_last_el_id_of_loop(first_el_id: int, last_el_id_top: int) -> Tuple[str, int]:
    """
    :database: SELECTs example_lines.
    :param first_el_id: Line id of a believed for-loop top.
    :param last_el_id_top: Line id of the last top of that unravelled for-loop.
    :return: the initials of the line_types iterated through ('pattern') and the last el_id of the likely loop the
    input arguments indicate.
    """
    cursor.execute("SELECT el.el_id, el.line, el.line_type, c.condition_type FROM example_lines el LEFT JOIN "
                   "conditions c ON el.el_id = c.el_id WHERE el.el_id >= ? ORDER BY el.el_id", (first_el_id,))
    rows = cursor.fetchall()
    loop_pattern, first_scheme, loop_length = '', '', 0
    for row in rows:
        el_id, line, line_type, condition_type = row
        if not first_scheme:  # Our first iteration
            assert line_type == 'truth', "get_last_el_id_of_loop() should only be called with the el_id of a believed " + \
                "for-loop top, not a line (" + line + ") of type " + line_type + ", as el_id " + first_el_id + " is."
            first_scheme = scheme(line)
            first_line = line
            preceding_loop_length = 0
        elif scheme(line) == first_scheme:  # Then atop the loop we rode in on.
            loop_pattern += ', '
            preceding_loop_length = loop_length
            loop_length = 0

        if condition_type:
            if condition_type == "assign" or condition_type == "while":
                loop_pattern += condition_type[0]  # a or w
            else:
                loop_pattern += condition_type  # "for" or "if"
        else:
            loop_pattern += line_type[0]  # i or o
        loop_length += 1

        # fixme This is crap. Generate-and-test in order or search past loop patterns for best match. 3/8/19
        if el_id >= last_el_id_top and loop_length == preceding_loop_length:
            # We're past the last loop top and reached the loop's likely bottom.
            break

    print("loop pattern of FOR loop '" + first_line + "' (el_id", str(first_el_id) + ") is:", loop_pattern)
    return loop_pattern, el_id  # Loop pattern (eg, 'toitto, toitto, toittto'), el_id believed to be loop bottom.


def type_string(value: str) -> str:
    """
    :param value:
    :return: 'bool'|'str'|'float'|'int'
    """
    if value == 'True' or value == 'False':
        return 'eval'  # eval('False') returns False, unlike bool('False').
    elif not value.isnumeric():
        return 'str'
    elif not value.isdigit():
        return 'float'
    return 'int'


def replace_hard_code(prior_values: Dict[str, Any], line: str) -> str:
    """
    For output, replace any word in 'line' that matches a prior input value with that value's variable name.
    :database: not involved. 'It is good to meet you, Albert' => It is good to meet you, ' + v0
    # todo we shouldn't have to worry about variable names being matched in the new 'line'. 3/7/19
    # todo hard coded values should only be replaced if the variable's value matches the
    # output value without failing a unit test. So generate-and-test this or postpone it until
    # unit tests are passing so this optimization can be tested before made. 3/7/19
    :param prior_values:
    :param line:
    :return:
    """
    for variable_name in prior_values:  # Eg, prior_values is {name: Albert, guess: 5}
        if variable_name == '__example__':  # Skip that special variable.
            continue
        #  "r'\bfoo\b' matches 'foo', 'foo.', '(foo)', 'bar foo baz' but not 'foobar' or 'foo3'." -- bit.ly/2EWdcBL
        match = re.search(r'\b' + str(prior_values[variable_name]) + r'\b', line)
        if match:  # position > -1:
            new_line = line[0:match.start()] + "' + str(" + variable_name + ')'  # It is good to meet you, ' + v0

            # Add remainder of line, if any.
            remainder_of_line = line[match.start() + len(match.group(0)):]
            if remainder_of_line:
                new_line += " + '" + remainder_of_line
            line = new_line
    return line


def get_example_id(el_id: int) -> int:
    cursor.execute("SELECT example_id FROM example_lines WHERE el_id=?", (el_id,))
    return cursor.fetchone()[0]


def get_block_record(first_el_id: int) -> Tuple:
    cursor.execute("SELECT * FROM control_block_traces WHERE first_el_id=?", (first_el_id,))
    return cursor.fetchone()


def get_for_loops_record(control_id: int, el_id: int) -> Tuple:
    cursor.execute("SELECT * FROM for_loops WHERE control_id=? AND first_el_id<=? AND last_el_id>=?",
                   (control_id, el_id, el_id))
    # assert cursor.fetchone()[0] is not None, "No period exists in for_loops for: control_id, last_el_id as " + \
    #                                          control_id + ", " + last_el_id
    return cursor.fetchone()


def get_python(control_id: int, current_el_id: int) -> Tuple[str, int]:
    """
    If current_el_id isn't a controls.first_el_id, return (None, None), else return its associated
    python code and last_el_id (used to dedent).
    :param control_id:
    :param current_el_id:
    :return: (a python code line, last_el_id), or (None, None)
    """
    # For the last_el_id, minimal extent in lines is used for IFs while maximal extent is used for FORs.
    cursor.execute("""SELECT cntl.python, min(ctlei.last_el_id) as if_end, max(ctlei.last_el_id) as old_for_end
        FROM controls cntl JOIN cbt_temp_last_el_ids ctlei USING (control_id) 
        WHERE cntl.first_el_id=? AND ctlei.last_el_id>?""",  # and ctlei.example_id=?""",  # AND ctlei.first_el_id=?""",
                   (current_el_id, current_el_id))  #, get_example_id(current_el_id)))
    rows = cursor.fetchall()
    # assert len(rows) == 1, str(rows)  cast(substr(ctlei.cbt_id, instr(ctlei.cbt_id, '_') + 1) as int)=?
    if rows[0][0] is None:
        return None, None
    else:
        python, if_end, for_end = rows[0]  # See Select list above
        if python[0:2] == 'if':
            return python, if_end  # if_end is the minimum associated last_el_id.
        elif python[0:3] == 'for':
            # if current_el_id == 5:  # Special case needed for __example__ loop because of ctlei.example_id filter above.
            #     return python, get_final_el_id()  # Maximum last_el_id w/in all examples.
            row = get_for_loops_record(control_id, current_el_id)
            return python, row[3]  # python, and the last_el_id of the related loop (from for_loops table).


def cast_inputs(code: List[str], variable_types: Dict[str, str]) -> List[str]:
    """
    Add casts int() and float() where variables of those types are being created from input().
    lp todo Consider inputs() of /all/ generated functions.
    :param code: The generated function
    :param variable_types: all the input variables with their likely data type, based on the examples.
    :return: the same 'code' but with casted input lines.
    """
    code_out = []
    regex = re.compile(r'([A-z]\w+) = input\("\1:"\)  # Eg, ([^ \n]*)')  # \1 is var name (and \2 would be the data)
    for line in code:
        match = regex.search(line)
        if not match:
            code_out.append(line)  # Non-input lines are copied straight to output.
        else:
            variable = match.group(1)
            datatype = variable_types[variable]
            if datatype == 'str':
                code_out.append(line)  # String data input lines are copied straight to output.
            else:
                # Cast non-string variables, eg, code_out.append('v110 = int(input('v110:'))  # Eg, 4')
                code_out.append(regex.sub(r'\1 = ' + datatype + r'(input("\1:"))  # Eg, \2', line))
    return code_out


if DEBUG and __name__ == "__main__":
    # regex.search() somehow includes unmatched text in group \1.
    assert ['        v25 = int(input("v25:"))  # Eg, 4'] == \
           cast_inputs(['        v25 = input("v25:")  # Eg, 4'], {'v25': 'int'}), \
           cast_inputs(['        v25 = input("v25:")  # Eg, 4'], {'v25': 'int'})
    assert ['v110 = int(input("v110:"))  # Eg, 4'] == \
           cast_inputs(['v110 = input("v110:")  # Eg, 4'], {'v110': 'int'}), \
           cast_inputs(['v110 = input("v110:")  # Eg, 4'], {'v110': 'int'})
    assert ['v110 = input("v110:")  # Eg, 4', 'v110 = input("v110:")  # Eg, four'] == \
        cast_inputs(['v110 = input("v110:")  # Eg, 4', 'v110 = input("v110:")  # Eg, four'], {'v110': 'str'}), \
        cast_inputs(['v110 = input("v110:")  # Eg, 4', 'v110 = input("v110:")  # Eg, four'], {'v110': 'str'})
    assert ['v110 = float(input("v110:"))  # Eg, 4'], ['v110 = float(input("v110:"))  # Eg, 4.0'] == \
        cast_inputs(['v110 = input("v110:")  # Eg, 4', 'v110 = input("v110:")  # Eg, 4.0'], {'v110': 'int'})


# def get_longest_example() -> int:
#     cursor.execute("SELECT example_id FROM example_lines el GROUP BY example_id ORDER BY count(el.el_id) DESC, el_id")
#     return cursor.fetchone()[0]


def get_1st_line_of_iteration(last_el_id) -> str:
    """
    Return the first line of the last FOR loop iteration control_block_trace whose last_el_id equals that given. Or
    None if none.
    (See if this can be replaced with a call to get_local_el_id_of_open_loop() then Select line from example_lines. todo)
    :param last_el_id: of a control block trace
    :return: example_lines.line or None
    """
    sql = """SELECT el.line FROM example_lines el 
    JOIN control_block_traces cbt ON el.el_id=cbt.first_el_id -- Pull iteration headers.
    JOIN controls cntl USING (control_id) -- For the python code.
    JOIN cbt_temp_last_el_ids ctlei USING (control_id) -- To connect the given last_el_id.
    WHERE SUBSTR(cntl.python,1,4) = "for " AND
    cbt.last_el_id_min IS NOT NULL AND -- Filter non-terminal iterations. 
    ctlei.last_el_id = ? AND
    el.el_id < ? -- Above last_el_id,
    ORDER BY el.el_id DESC -- but closest to it. """
    cursor.execute(sql, (last_el_id, last_el_id))
    fetched_one = cursor.fetchone()
    # assert fetched_one is not None, str(last_el_id) + " not found in get_1st_line_of_iteration(last_el_id)"
    return fetched_one[0] if fetched_one else None


def last_int_of_string(line: str) -> int:
    """
    Return the last integer of given `line`.  Error if none present.
    :param line:
    :return: integer
    """
    return int(re.search(r'(\d+)\D*$', line).group(1))


def is_open(code: List[str], control_type: str) -> int:
    """
    Return whether 'code' has an open control of condition_type.
    :param code:
    :param control_type: 'if'|'for'
    :return: Boolean
    """
    control_indent = None
    for line in code:
        line_indent = len(line) - len(line.lstrip())
        if control_indent is not None and line_indent <= control_indent:  # Outermost IF has ended.
            control_indent = None
        if (line.lstrip().startswith(control_type + ' ') or (control_type == 'if' and line.lstrip().startswith('elif '))) \
                and (control_indent is None or control_indent > line_indent):
            control_indent = line_indent  # Only the indent of the outermost IF control is needed.
    return control_indent == 0 or control_indent


if DEBUG and __name__ == '__main__':
    assert not is_open(['print("hi")'], control_type='if')
    assert is_open(['elif False:', '    print("hi")'], control_type='if')
    assert not is_open(['for i in range(0,3):', '    print("hi")'], 'if')
    assert is_open(['if False:', '    for i in range(0,3):', '        print("hi")'], 'if')
    assert is_open(['if False:', '    for i in range(0,3):', '        print("hi")', '    print("bye")'], 'if')
    assert not is_open(['if False:', '    for i in range(0,3):', '        print("hi")', 'print("bye")'], 'if')
    assert is_open(['if True:', '    for i in range(0,3):', '        print("i is", i)', '    print("bye")'], 'if')

    assert is_open(['for i in range(0,3):', '    print "hi"'], 'for')  # Loop's open.
    assert is_open(['if False:', '    for i in range(0,3):', '        print "hi"'], 'for')  # Loop's open.
    assert not is_open(['if True:', '    for i in range(0,3):', '        print "i is", i', '    print "bye"'], 'for')
    assert not is_open(['print "hi"'], 'for')


def get_via_closest_prior_key(controls_at_1_indent: Dict[int, str], code_key: int, code: List[str], control: str) -> Tuple[str, int]:
    """
    Decrement code_key until we can return items in our first argument that are indexed by the code_key closest to, but
    not larger than, the original code_key.
    :param controls_at_1_indent: Dict where the keys point to all the `code` lines that start the IFs or FORs at a
    specific indent
    :param code_key: An If or For control's first line (in the code being generated).
    :param code: The function generated thus far.
    :param control: 'if'|'for'
    :return:
    """
    if code_key == len(code):
        code_key -= 1
    else:
        code_key = get_last_line_of_indent(code, code_key)
    while code_key not in controls_at_1_indent:
        assert code_key >= 0, "No key<=" + str(code_key) + " found"
        code_key -= 1
    if control == 'for':
        loop_variable = controls_at_1_indent[code_key]
        return loop_variable, code_key
    elif control == 'if':
        condition, _ = controls_at_1_indent[code_key]
        return condition, code_key
    else:
        assert False, "control '" + control + "' unrecognized"


def get_last_line_of_indent(code: List[str], key: int, any_change=True) -> int:
    """
    :param code: The codebase to inspect.
    :param key: The starting point. Also used to define the original_indent.
    :param any_change: False means to ignore indents > original_indent (inner blocks).
    :return: the key to the last line of `code` having the indent of code[original_key], or optionally greater, in an
    unbroken sequence of lines.
    """
    original_indent = len(code[key]) - len(code[key].lstrip())
    while True:
        key += 1
        if key == len(code):  # No more code to check.
            break
        indent = len(code[key]) - len(code[key].lstrip())
        if any_change:
            if original_indent != indent:  # End of block or inner block opened.
                break
        else:
            if original_indent > indent:  # End of block
                break
    return key - 1


if __name__ == "__main__":
    assert 0 == get_last_line_of_indent(["pass"], 0)  # 0 + 1 == len(code), so 1 - 1 returned.
    assert 0 == get_last_line_of_indent(["    print True", "print 'done'"], 0)  # code[0] is the only indented line
    assert 1 == get_last_line_of_indent(["    print True", "    print False", "print 'done'"], 0)  # code[1] last
    assert 1 == get_last_line_of_indent(["    print True", "    print False", "print 'done'"], 1)  # code[1] still last
    assert 0 == get_last_line_of_indent(["    if True", "        print False", "print 'done'"], 0)  # code[0] last
    assert 1 == get_last_line_of_indent(["    if True", "        print False", "print 'done'"], 0, False)  # code[1] "


def get_IF_permutation(if_branches: List[int], trial: int) -> List[int]:
    """
    Given a list of (indexes to) branches, return the permutation specified by `trial` (per
     https://en.wikipedia.org/wiki/Factorial_number_system).
    :param if_branches: ints (list of code keys)
    :param trial: 0-based permutation # (in decimal)
    :return: if_branches in a new permutation
    """
    required_f_length = len(factoradic.to_factoradic(math.factorial(len(if_branches)) - 1))  # -1 due to trials' 0 base.

    f = factoradic.to_factoradic(trial)  # This creates a permutation-choosing encoding of `trial`.
    # f is left padded, with zeroes, to the required length:
    left_pad = required_f_length - len(f)
    for j in range(left_pad):
        f.append(0)
    f.reverse()

    # Create the trial-th permutation of if_branches.
    temp = if_branches.copy()  # To allow safe deletion of used elements.
    IF_to_return = []
    for figit in f:
        IF_to_return.append(temp[figit])  # An f digit choosing from the remaining elements.
        del temp[figit]
    if DEBUG:
        print("Permutation selected:", IF_to_return)
    return IF_to_return


if __name__ == '__main__':
    assert get_IF_permutation(["red", "blue", "yellow"], 0) == ["red", "blue", "yellow"]
    assert get_IF_permutation(["red", "blue", "yellow"], 5) == ["yellow", "blue", "red"]
    assert get_IF_permutation([0, 1, 2], 0) == [0, 1, 2]
    assert get_IF_permutation([0, 1, 2], 5) == [2, 1, 0]


def get_IF_test_function(code: List[int], an_IF: List[int]) -> str:
    """
    Translate a list of keys pointing to if/elif branches into a test IF function incorporating them, for return.
    :param code:
    :param IF: List of keys into `code`, pointing to if/elif branches.
    :return: IF_function
    """
    IF_function = ["def IF_function():"]
    for branch in an_IF:
        # Strip the branch of its leading whitespace and 'if '/'elif ' for easy reconstitution.
        line = code[branch].lstrip()
        if line[0:3] == "if ":
            line = line[3:]
        elif line[0:5] == "elif ":
            line = line[5:]
        else:
            assert False, line + " unrecognized. First word should instead be 'if' or 'elif'"

        if len(IF_function) == 1:
            IF_function.append("    if " + line)
        else:
            IF_function.append("    elif " + line)
        # This will enable confirmation that the correct branch was triggered:
        IF_function.append("        return '" + line + "'")
    IF_function.append("actual_condition = IF_function()")  # Call the testing function (herein) and capture its output.
    return "\n".join(IF_function)


def IF_order_search(code: List[int], an_IF: List[int],
                    IFs: Dict[int, Dict[int, Tuple[str, int, List[Dict[str, Any]]]]]) -> List[int]:
    """
    Order given IF by trying all possible orders until 1 succeeds. Then apply that IF to reordered_code, for return.
    :param code: the Python function being generated
    :param an_IF: a list of code keys pointing to if/elif branches
    :param IFs: IFs[indents][starting code line] = (condition, is_elif, [prior_values.copy()])
    :return: reordered_code
    """
    maximum_trial = math.factorial(len(an_IF))  # The # of ways an_IF's branches can be ordered (ie, permuted).
    success = False
    IF_permutation = an_IF.copy()
    if DEBUG:
        print("Permutation selected:", IF_permutation)
    IF_function = get_IF_test_function(code, IF_permutation)
    trial = 0  # Count of permutations trialed.
    while trial < maximum_trial:  # Order an_IF successfully, or bust.
        for start in an_IF:
            indents = int((len(code[start]) - len(code[start].lstrip())) / 4)
            expected_condition, is_elif, prior_values = IFs[indents][start]
            locals_dict = {}  # Needed to retrieve actual_condition
            exec(IF_function, prior_values[0], locals_dict)         # ****** EVALUATE IF FUNCTION ******
            actual_condition = locals_dict['actual_condition']
            actual_condition = actual_condition.rstrip(':')
            triple = assertion_triple(actual_condition)  # 'g > s' => ('g','>','s')
            if triple[0] is None:
                actual_condition = actual_condition.replace(" and ", "⋅and⋅")
                actual_condition = actual_condition.replace(" or ", "⋅or⋅")
                actual_condition = actual_condition.replace(' ', '')  # 'g > s' => 'g>s'
                actual_condition = actual_condition.replace("⋅and⋅", " and ")
                actual_condition = actual_condition.replace("⋅or⋅", " or ")
            else:
                actual_condition = triple[0] + triple[1] + triple[2]  # 'g' + '>' + 's' => 'g>s'
            success = (expected_condition == actual_condition)
            if not success:
                trial += 1
                IF_permutation = get_IF_permutation(an_IF, trial)
                IF_function = get_IF_test_function(code, IF_permutation)
                break
        if success:
            break  # IF_function succeeded with all an_IF's branches.
    assert success, IF_function[0:min(len(IF_function), 80)] + "... cannot be ordered successfully"

    # Apply found branch order to reordered_code using IF and the conditions it points to.
    reordered_code = code.copy()
    # First need to know where all of IF's branches currently reside in `code`.
    IF_branches_sorted_by_line = an_IF.copy()
    IF_branches_sorted_by_line.sort()
    keys = []  # To point to all IF's branches in `code`, from first to last:
    for key in IF_branches_sorted_by_line:
        keys.append(key)
    # Then we can reorder IFs' conditions in reordered_code.
    # The idea here is to superimpose each branch of IF_permutation (the correct ordering) from the bottom up onto a
    # code copy (reordered_code) using the if/elif branch locations held in an_IF. Each iteration handles the if/elif
    # condition then the consequent.
    if_key = IF_permutation[0]
    i = len(an_IF) - 1  # We'll start from the bottom so that starting points
    IF_permutation.reverse()  # of the IF don't change indirectly.
    for branch in IF_permutation:
        # Copy each if/elif condition into position in reordered_code.
        # (Also update IFs[key][is_elif] w/our new info?)
        tc = reordered_code[keys[i]]  # tc==target condition to be replaced.
        if i == 0 and branch != an_IF[0]:  # Last step: The correct 'if' condition needs to be copied topmost.
            assert branch == if_key
            pos = code[branch].find("    elif ")  # Start of the last indent before the correct 'if' condition.
            tc = tc[0:pos + 7] + code[branch][pos + 9:]  # Replace incorrect 'if' condition with new (from an 'elif').
        elif i > 0 and branch == an_IF[0]:  # Copy incorrect 'if' condition down `code` to an 'elif' location.
            pos = code[branch].find("    if ")  # Start of the last indent before the incorrect 'if' condition,
            tc = tc[0:pos + 9] + code[branch][pos + 7:]  # superimposed onto its correct location (an 'elif' line).
        elif i > 0:  # Both source and target conditions belong to 'elif' branches.
            pos = code[branch].find("    elif ")  # Start of the last indent before the condition to be copied,
            tc = tc[0:pos + 9] + code[branch][pos + 9:]  # to this ('elif') location.
        reordered_code[keys[i]] = tc  # Adjustment made.

        # Copy each if/elif *consequent* into position in reordered_code, as well,
        # by first deleting the unwanted consequent (deleting targeted lines allows unconditionally appending new),
        last_key_of_block = get_last_line_of_indent(code, keys[i] + 1, any_change=False)  # Assumes condition is 1 line.
        target_body_length = 1 + last_key_of_block - (keys[i] + 1)
        del reordered_code[keys[i]+1 : keys[i]+1+target_body_length]
        # then adding the desired consequent.
        last_key_of_block = get_last_line_of_indent(code, branch + 1, any_change=False)
        source_body_length = 1 + last_key_of_block - (branch + 1)
        for j in range(source_body_length):
            reordered_code.insert(keys[i]+j+1, code[branch+j+1])  # Again `branch` points to desired code, and keys[i]
        i -= 1                                                    # to desired location.
    return reordered_code


def order_IFs(code: List[str], IFs: Dict[int, Dict[int, Tuple[str, int, List[Dict[str, Any]]]]]) -> List[str]:
    """
    Order the IFs' branches correctly by first grouping those branches that belong together in a single IF control aka
    if/elif.
    :param code: function being generated, as a list of statements.
    :param IFs: IFs[indents][starting code line] = (condition, is_elif, [prior_values.copy()])
    :return: `code` with its IF branches in order.
    """

    # Sort IFs' keys into list IFs_keys in order of the code lines referenced.
    # (IFs structure: IFs[indents][key] = (condition, is_elif, [prior_values.copy()]))
    IFs_keys = []
    for indents in IFs:
        for key in IFs[indents]:
            IFs_keys.append(key)
    IFs_keys.sort()

    an_IF = []
    for key in IFs_keys:  # The keys (into `code`) are appended to an_IF in order of code line.
        # Each time an entire IF is complete, if it has >1 branches, find their correct order.
        if len(an_IF) > 1 and code[key].lstrip()[0:3] == 'if ':  # IF is complete.

            code = IF_order_search(code, an_IF, IFs)  # ******** ORDER_SEARCH() ********
            an_IF = []  # Reset for next IF.
        an_IF.append(key)

    if len(an_IF) > 1:  # Sort the branches of the final IF.
        code = IF_order_search(code, an_IF, IFs)  # ******** ORDER_SEARCH() ********
    return code


def generate_code() -> List[str]:
    """
    Information gathering steps done, now the info in tables selection, conditions, controls, control_trace_blocks,
    and last_el_ids are collated into exem-conforming Python code.
    Each example_lines record is considered in turn, in example_id major order.
    Such a record's implied code is added to `code` if not already there, and sanity checked against it otherwise.
    Subsequent appearances can be from multiple examples or loop iterations. Additionally, 'assign'ments are
    captured in a lookup table used for variable mention in the output (prints).
    :database: SELECTs sequential_function, selection. UPDATEs sequential_function via likely_data_type()).
    :return: Python `code`
    """

    code = []
    FORs = dict()  # Dictionaries instead of lists because indents (the key) aren't necessarily linear.
    IFs = dict()
    variable_types, indents = {}, 1

    # Loop over all example_lines, also pulling their condition info where it exists. (Keep this select list in sync
    # with next_row indices below.)
    sql = """SELECT el.el_id, el.example_id, el.line, el.line_type, c.condition_type, c.control_id 
    FROM example_lines el 
    LEFT JOIN conditions c ON el.el_id = c.el_id 
    ORDER BY el.el_id"""
    cursor.execute(sql)
    selection = cursor.fetchall()
    if len(selection) == 0:
        print("*Zero* example lines found.")

    key = 0  # Key into `code` for comparison. It is incremented at loop top to point to the next expected code line,
    # eg, 1 beyond `code`s length.
    # todo Distinguish arguments from variable assignments and input() statements.
    latest_IF_added = ''
    last_el_ids = []
    prior_row = [None, None, None, None, None, None]
    i = 0  # selection line counter
    for row in selection:
        el_id, example_id, line, line_type, condition_type, control_id = row
        if DEBUG:
            print("i =", i)

        if example_id != prior_row[1]:  # then we're on a new user example.
            assert scheme(line) == "_==__example__"
            prior_values = {}  # Clear out (or initialize).
            key = 0  # Start comparing anew, at the top of `code`.
            #use key or control_id instead. indentation_to_instances = dict()  # Target function may have multiple controls at a given indentation.
        else:  # Default is to advance key with each `line`.
            key += 1

        # Re: input and output lines, we can simply add them to `code` if we're on its frontier.
        add_line_to_code = True if key == len(code) else False

        # Code an INPUT. (Example data to be hinted in tests and comments.)
        if line_type == 'in':

            # Use our default variable name, then see if another was assigned. todo Increment 'i1' when required.
            variable_name = "i1"  # "v" + str(el_id)
            if i+1 < len(selection):  # Unless at last 'line', look ahead.
                next_row = selection[i+1]  # el_id, line, line_type
                # If the next row is truth and has an equality "naming" 'line's value, make that name the variable name.
                if next_row[4] == 'assign' and \
                        get_variable_name(next_row[2], 'i1'):  # Eg, ('guess==i1', 'i1') => guess
                    variable_name = get_variable_name(next_row[2], 'i1')  # Eg, 'guess'

            assignment = indents * "    " + variable_name + ' = input("' + variable_name + ':")' + "  # Eg, " + line
            if add_line_to_code:
                code.append(assignment)
            else:  # Sanity check.
                pos = assignment.find("  # Eg, ")  # Exclude " # Eg, [...]" comment from the following comparison.
                assert code[key][0:pos+1] == assignment[0:pos+1], "'" + code[key][0:pos+1] + "'  *is not*  '" + \
                                                                  assignment[0:pos+1] + "'"

            if line:  # line's possibly empty (due to no example input).
                # Note the input values for later substitution with their variable in our print()s.
                prior_values[variable_name] = eval(type_string(line) + "(line)")  # == eg, pri..['name'] = str('Albert')
                #                                                                   or prior_values['guess'] = int('5')
                # Find the input's data type (to add casts around our input lines in cast_inputs()).
                if variable_name not in variable_types:
                    variable_types[variable_name] = type_string(line)
                elif variable_types[variable_name] != 'str' and type_string(line) == 'float':  # int->float
                    variable_types[variable_name] = 'float'

        elif line_type == 'out':  # An OUTPUT ie a print().
            # Replace any constants in 'line' that should instead be soft-coded (we'll know from a match on
            # prior input value or equality assertion).
            line = replace_hard_code(prior_values, line)

            if type_string(line) == 'str':
                print_line = "print('" + line + "')"
                return_text = "#return '"
            else:
                print_line = "print(" + line + ')'
                return_text = "#return "

            # Add the print() to the code if it's new to current control.
            print_line = indents * "    " + print_line
            if add_line_to_code:
                code.append(print_line)
                # Add return if `line` is not a string > 10 chars and it's not in a (non-__example__) loop
                # (todo) and its the last output and its datatype is consistent across cohort.
                if (type_string(line) != 'str' or len(line) <= 10) and not is_open(code[1:], 'for'):
                    code.append((indents * "    ") + return_text + line + return_text[-1])  # (Uncommented in Stage 2.)
                    key += 1
            else:  # Sanity check
                assert code[key] == print_line, "'" + code[key] + "'  *is not*  '" + print_line + "'"
                if key < len(code) and code[key].find(return_text) > -1:
                    key += 1  # To get past proto-return statement.

        else:  # truth/assertions/reasons/conditions

            left_operand, operator, right_operand = assertion_triple(line)  # (Order of operands not entirely intuitive)
            if condition_type == "assign":
                if not left_operand.isidentifier():  # Special case. left_operand is, eg, 'guess_count+1'
                    # Eg, prior_values['guess_count'] = 3 allows swapping in guess_count for 3 in a later print:
                    # guess_count==*3* + "You guessed in *3* guesses!" => "You guessed in " + guess_count + " guesses!".
                    if right_operand.isdigit():
                        right_operand = int(right_operand)
                    prior_values[left_operand] = right_operand  # prior_values['guess_count + 1'] = 3
                # No code added (though in the regular case  if next_row[4] == 'assign'  happens, see above) so:
                key -= 1
            else:  # for or if
                if condition_type == 'for':  # Needed for below latest_IF_added, which is used when adding IFs:
                    local_iteration = get_block_record(first_el_id=el_id)[8]  # "0 based local count"
                    if left_operand.isdigit():
                        left_operand = int(left_operand)
                    prior_values[right_operand] = left_operand  # Eg, prior_values[guess_count] = 5

                #                    **********
                python, last_el_id = get_python(control_id, el_id)  # Retrieves iff el_id is a controls.first_el_id
                #                    **********
                if python:  # Then this is a control we haven't seen, so to `code`
                    # *** ADD *** ADD *** ADD ***
                    code.append(indents * "    " + python)  # regardless of add_line_to_code's value.
                    key = len(code) - 1  # Point to last element so add_line_to_code will be set True.

                    print("Appending", last_el_id, "for added line", line)
                    last_el_ids.append(last_el_id)  # last_el_ids are tracked to determine when to dedent.

                    if condition_type == "for":  #python[0:4] == "for ":
                        latest_FOR_added = python
                    elif condition_type == "if":
                        prior_IF_added = latest_IF_added
                        latest_IF_added = {"indents": indents, "example_id": example_id, "iteration": local_iteration}
                    else:
                        assert False, "condition_type " + condition_type + " unrecognized"

                    if condition_type == 'for':
                        if indents not in FORs:
                            FORs[indents] = dict()  # dict() needed because there can be >1 FOR at a given indent.
                        FORs[indents][key] = right_operand  # To enable recall of loop's variable and 1st line (`key`).
                        FOR_period, FOR_increment = get_for_loops_record(control_id, last_el_id)[4:6]  # Loop details.

                    elif condition_type == 'if':
                        # Standardize and save the condition to avoid re-adding IFs to `code`:
                        condition = code[key].lstrip()[3:-1]  # '   if g > s:' => 'g > s'
                        triple = assertion_triple(condition)  # 'g > s' => ('g','>','s')
                        if triple[0] is None:
                            # Protect AND and OR.
                            condition = condition.replace(" and ", "⋅and⋅")
                            condition = condition.replace(" or ", "⋅or⋅")
                            condition = condition.replace(' ', '')  # 'g > s' => 'g>s'
                            condition = condition.replace("⋅and⋅", " and ")
                            condition = condition.replace("⋅or⋅", " or ")
                        else:
                            condition = triple[0] + triple[1] + triple[2]  # 'g' + '>' + 's' => 'g>s'

                        # Track all co-located IF branches to decide their ELIF order at bottom.
                        is_elif = False
                        if indents not in IFs:
                            # dict() because there are usually >1 'if' branches at a given indent, and so another key
                            IFs[indents] = dict()  # (such as starting code line) is needed to distinguish them.
                        # IFs at the same indent are most likely part of one if/elif, so if an IF is still open, and
                        elif is_open(code[:-1], 'if') and prior_IF_added != latest_IF_added:
                            # the most recently added IF is not from same example, iteration, etc, as last, "if"->"elif"
                            code[len(code) - 1] = code[len(code) - 1].replace("if ", "elif ", 1)
                            is_elif = True  # Mark ELIF

                        assert key not in IFs[indents]  # I believe that this should always be true.
                        IFs[indents][key] = (condition, is_elif, [prior_values.copy()])  # 3rd element list is for elif ordering via testing.

                    indents += 1  # A new block opens.

                else:  # Sanity checks, eg, getting `key` into matching `code`. This is based on each example
                    # necessarily re-treading the same target code, with the exception that IF conditions can
                    # continually be introduced (as examples finally make these (the related IF condition) true).
                    last_el_id = get_last_el_id(el_id, condition_type)

                    if condition_type == "for":
                        if local_iteration % FOR_period == 0:  # Then `line` starts the first iteration for this
                            indents += 1  # FOR loop in this user example, opening a new block.
                            print("Appending", last_el_id, "for non-added FOR line", line)
                            last_el_ids.append(last_el_id)
                        # Determine which FOR is being reiterated, and point to it with `key`.
                        # (loop_variable, key = FORs[indents -1] would be good enough if indents couldn't repeat.)
                        loop_variable, key = get_via_closest_prior_key(FORs[indents - 1], key, code, 'for')  # Re-assign `key`.
                        #          *** ^^^ ***

                        # indents = int((len(code[key]) - len(code[key].lstrip())) / 4) + 4
                        assert loop_variable == right_operand, "'" + loop_variable + "'  *is not*  '" + right_operand + "'"

                    else:  # IF
                        print("Appending", last_el_id, "for non-added IF line", line)
                        last_el_ids.append(last_el_id)

                        # Find key into `code` by locating `line` in IFs[indent].
                        if type(left_operand) == str:  # Collapse line for matching, below, unless it is None,
                            line = left_operand + str(operator) + str(right_operand)  # or eg, 'guess_count+1'
                        else:
                            # Protect AND and OR.
                            line = line.replace(" and ", "⋅and⋅")
                            line = line.replace(" or ", "⋅or⋅")
                            line = line.replace(' ', '')  # 'g > s' => 'g>s'
                            line = line.replace("⋅and⋅", " and ")
                            line = line.replace("⋅or⋅", " or ")

                        # IFs[indents][key] is a list of (condition, is_elif, [prior_values.copy()]) so
                        # IF_dict[key] is a list of (condition, is_elif, [prior_values.copy()])
                        # where key means line in `code`.
                        IF_dict = IFs[indents]  # IF_dict's keys (1st line of an if/elif control) index IF conditions.
                        for if_key in IF_dict:  # Eg, for key in {8: ('guess>secret', False, [{'name',...}]), 10: ...}
                            # (Searching for the exact if/elif control in `code` got too hairy.)  IF = get_via_closest_prior_key(IFs[indents], key, code, 'if')  # IF is a list of if/elif branches.

                            if line == IF_dict[if_key][0]:  # Found. Eg, 'g>s' == 'g>s'
                                break

                        # Asserting found because store_ifs() is supposed to give every unique IF a start_el_id.
                        assert IF_dict[if_key][0] == line, "\nExpected: " + IF_dict[if_key][0] + "\nActual: " + line
                        key = if_key
                        IFs[indents][key][2].append(prior_values.copy())  # For elif order testing.
                        indents += 1  # A new block (an IF consequence) will open for the next `line`.

        while last_el_ids and el_id >= last_el_ids[-1]:  # For each block just ended (at el_id).
            if latest_FOR_added:
                # If a FOR iteration block just ended, and if the innermost one did so prematurely, add "break".
                iteration_line_0 = get_1st_line_of_iteration(last_el_id)  # Eg, 'eg == 3' (or None if not a FOR block).
                # Eg, 6 > 2 from "for guess_count in range(0, *6*, 1)" and "guess_count == *2*", implying an early exit.
                if iteration_line_0 and \
                        abs(int(latest_FOR_added.split(',')[1])) > abs(last_int_of_string(iteration_line_0)):
                    if DEBUG:
                        print("Adding 'break'. len(code), el_id, iteration_line_0, latest_FOR_added: ",
                              len(code), el_id, iteration_line_0, '"' + latest_FOR_added + '"')
                    code.append(indents * "    " + "break")
                    latest_FOR_added = None

            indents -= 1  # dedent
            last_el_id = last_el_ids.pop()  # Of the blocks just ended, pops the last_el_id of the innermost one first.

        prior_row = row
        i += 1  # selection line counter

    if DEBUG:
        for for_loops_at_indent in FORs:
            print("Re: the FOR loops at indentation", str(for_loops_at_indent) + ':')
            for code_key in FORs[for_loops_at_indent]:
                print("    At `code` key", str(code_key) + ", the loop variable is:", FORs[for_loops_at_indent][code_key])
            print()
        for an_indent in IFs:
            print("The IFs at indentation", str(an_indent) + ':')
            for a_code_key in IFs[an_indent]:
                if_type = 'elif' if IFs[an_indent][a_code_key][1] else 'if'
                print("    At `code` key", str(a_code_key) + ", a condition is:", IFs[an_indent][a_code_key][0],
                      "and its if_type is '", if_type + "'")
    code = order_IFs(code, IFs)  # Each IF's branches are in random order. Re-sort them until all examples pass.

    return cast_inputs(code, variable_types)
    # Below may be selectively re-activated as more problems are handled.


    # Next, we gen code from the ************** IF/ELIF/ELSE ************** conditions, in that order.
    # (old: Reasons where loop_likely==0 map to conditions 1:1.)

    sql = """
        SELEC T line, example_id, step_id AS r1 FROM selection WHERE line_type = 'truth' AND loop_likely = 0
            ORDER BY (SELECT COUNT(*) FROM pretests WHERE pretest = r1) DESC, LENGTH(line) DESC, 
            line -- (for order stability) 
         """
    cursor.execute(sql)
    conditions = cursor.fetchall()  # E.g., [('i1 % 5 == 0',), ('i1 % 3 == 0',)]
    if len(conditions) == 0:
        print("*Zero* line_type 'truth', loop_likely==0 rows found. The exact query executed: " + sql)
    else:
        # todo To help diagnose user error, add a test ensuring that this 'reason' is a valid pretest to all other 'reason's
        code += "if " + conditions[0][0] + ":\n"  # This most selective condition is the one that can most commonly
        # serve as a pretest, therefore it should be the IF condition. (+1 Insightful)
        # Return output corresponding to this reason and step.
        code += "    return " + quote_if_str(get_output(conditions[0][1], conditions[0][2])) + '\n'
        del(conditions[0])  # IF is done.

        # Add the ELIF and ELSE conditions and their consequents based on the same criteria (order from the SELECT).
        for condition in conditions:
            reason_eid = condition[1]
            step_id = condition[2]
            condition = condition[0]
            if condition == "True":
                code += "else:\n"
            else:
                code += "elif " + condition + ":\n"
            code += "    return " + quote_if_str(get_output(reason_eid, step_id)) + '\n'

    # Finally, we gen code from the *********** WHILE *********** conditions.

    sql = """
        SELECT line AS r1 FROM selection WHERE line_type = 'truth' AND loop_likely = 1 ORDER BY step_id DESC, 
            line -- (for order stability) 
         """
    cursor.execute(sql)
    loop_likely_reasons = cursor.fetchall()  # E.g., [('i1 % 5 == 0',), ('i1 % 3 == 0',)]
    if len(loop_likely_reasons) == 0:
        return code  # *********************************** RETURNING because no WHILE loop is indicated ***

    loop_steps, loop_step_increments = define_loop(loop_likely_reasons)  # *** DEFINE_LOOP() ***
    print("loop_steps:", loop_steps)
    print("increments:", loop_step_increments)

    # Loop info has been collated. Now generate loop code using found steps, termination conditions, and return values.

    i = 1
    code += "\n"
    for step in loop_steps:
        code += "accum" + str(i) + " = " + str(-1 * loop_step_increments[i-1]) + "\n"  # E.g., "accum1 = 1\n"
        i += 1

    # Add: WHILE the ANDed termination conditions are NOT true.
    code += "while "
    cursor.execute('''S ELECT final_cond, output, loop_step FROM termination WHERE loop_likely = 1 ORDER BY step_num''')
    terminations = cursor.fetchall()
    assert len(terminations) > 0, "Error: Nothing found in termination table"

    i = 1  # Start at 1 for user-facing names.
    for row in terminations:  # Write while's condition and set up termination list.
        last_cond, output, loop_step = row  # E.g., ['(i1-3)==2c', 'True', '(i1-1)>2c']
        # Replace original condition's dec/increment with one of our accumulators.
        _pos = get_inc_int_pos(loop_step)
        # Remove its "c" labels.
        code += remove_c_labels(loop_step[0:_pos[0]] + "accum" + str(i) + loop_step[_pos[1]:]) + " and "
        # So that could be: += "(i1-accum1)>2 and "
        i += 1
    code = code[0:len(code)-5] + ":\n"  # Clip off last " and ", and WHILE line finalized with ":\n"
    # E.g., "while i1 % (i1-accum1) != 0 and (i1-accum2)>2:\n"

    # Within the loop, each step's accumulator must increment.
    i = 1
    for step in loop_steps:
        code += "    accum" + str(i) + " += " + str(-1 * loop_step_increments[i - 1]) + "\n"
        i += 1
    # E.g., \taccum1 += 1

    # Loop done, now add the if/elif/else gauntlet of termination conditions with payload.
    # cursor.execute('select final_cond, output from termination where loop_likely=1 order by step_num')
    # terminations = cursor.fetchall()
    code += "if "
    i = 1
    for row in terminations:
        last_cond, output, loop_step = row
        _pos = get_inc_int_pos(last_cond)  # E.g., (5, 6)
        code += remove_c_labels(last_cond[0:_pos[0]] + "accum" + str(i) + last_cond[_pos[1]:])
        code += ":\n    return " + output + "\nelif "  # ELIF and RETURN
        i += 1
    code = code[0:len(code)-5]  # Clip off "elif "
    # E.g., i1 % (i1-accum1) == 0:\n\treturn False

    return code


# Unused since change of .exem format. 2/20/19
def unused_get_output(reason_eid: int, step_id: int) -> str:
    """
    For given 'reason', return the corresponding 'output' from the examples.
    E.g., 'i1 == 2c' --> "True"
    N.B. 'reason' must pre-exist in examples table.
    N.B. So far this function is for if/elif/else generation only.
    N.B. Even though the same `reason` may be re-used across examples, as long as there's only one IF, `reason`
    is sufficient to determine the output because the output can reference input only via variables (i1, i2, ...),
    not constants.
    :database: SELECTs example_lines.
    :param reason: text
    :return: the output the user associated with the given reason in his/her examples.
    """
    query = '''SELECT line FROM example_lines WHERE line_type = 'out' AND example_id = ? AND step_id > ? AND 
                        loop_likely = 0 ORDER BY step_id LIMIT 1'''
    cursor.execute(query, (reason_eid, step_id))
    fetched_one = cursor.fetchone()
    if fetched_one is None:
        cursor.execute("""SELECT step_id FROM example_lines WHERE line_type = 'out' AND example_id = ?  AND 
                        loop_likely = 0 ORDER BY step_id""", (reason_eid,))
        print("With example_id "+str(reason_eid)+" and step_id "+str(step_id)+
              ", this query returned zero rows:\n"+query)
        step_ids = ''
        for row in cursor.fetchall():
            step_ids += str(row[0]) + ', '
        sys.exit("The step_id's matching those criteria are " + step_ids)
    return fetched_one[0]


def dump_table(table: str) -> str:
    """
    When global variable DEBUG is True this prints, eg,
    [all example_lines:
    (el_id, example_id, step_id, line, loop_likely, line_type)
    (0, 0, 0, Hello! What is your name?, -1, out),
    (5, 0, 5, Albert, -1, in),
    (10, 0, 10, name==i1, -1, truth), ...
    :database: SELECTs given table.
    :return str: A representation of `table`
    """
    print_me = "all " + table + ":\n("
    cursor.execute('''SELECT * FROM ''' + table)
    all_rows = cursor.fetchall()
    for description in cursor.description:
        print_me += description[0] + ", "
    print_me = print_me[0:-2] + ")\n"  # Trim last ", "

    for row in all_rows:
        print_me += '('
        for field in row:
            print_me += str(field) + ", "
        print_me = print_me[0:-2] + "),\n"
    return '[' + print_me[0:-2] + ']'  # Trims last ',\n'


def inputs(example_id: int = -1) -> List:
    """
    Return all inputs (that came from the exem) for the given example (useful for testing).
    :database: SELECT example_lines.
    :param example_id: -1 means pull inputs from all examples
    :return:
    """
    query = "SELECT line FROM example_lines WHERE line_type='in' "
    if example_id > -1:
        cursor.execute(query + "AND example_id=? ORDER BY el_id", (example_id,))
    else:
        cursor.execute(query + "ORDER BY el_id")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(row[0])
    return result


def generate_tests(function_name: str, together: int = 1) -> str:
    """
    Generate a unit test per example in the .exem: each example's input and output lines will be compared to the
    actual_io_trace filled in by the print()s and input()s called by the target function, while operating on the
    global_input.
    :database: SELECT example_lines.
    :param function_name: used for test function name and calling the function under test.
    :param together: whether to test examples together (the default) or separately.
    """
    #delete:
    # cursor.execute('''SELECT inp.line, output.line, inp.example_id FROM example_lines inp, example_lines output
    #                     WHERE inp.example_id = output.example_id AND inp.line_type = 'in' AND output.line_type = 'out'
    #                     AND (inp.step_id = 5 OR output.step_id = 5) ORDER BY inp.example_id, output.step_id DESC''')
    # # The above DESC and the 'continue' below implement MAX(output.step_id) per example_id.
    #query = "SELECT DISTINCT example_id FROM example_lines WHERE example_id=? ORDER BY example_id"
    query = "SELECT DISTINCT example_id FROM example_lines "
    cursor.execute(query + "ORDER BY example_id")
    all_examples = cursor.fetchall()
    test_code = ""
    i = 1  # For appending to the test name.
    # previous_example_id = -1
    for row in all_examples:
        example_id = row[0] if not together else -1
        # Create one test per example.
        # if example_id == previous_example_id:
        #     previous_example_id = example_id
        #     continue
        test_code += "\ndef test_" + function_name + str(i) + "(self):\n"
        # code += "    i1 = " + inp + "\n"  # (i1 may be referenced by output as well.)
        # code += "    self.assertEqual(" + output + ", " + f_name + "(i1))\n\n"
        test_code += "    global global_input\n"
        test_code += "    global_input = ['" + "', '".join(inputs(example_id)) + "']  # From an example of the .exem\n"  # Eg, ['Albert','4','10','2','4']
        test_code += "    " + function_name + "()  # The function under test is used to write to actual_io_trace.\n"  # TODO need formal params!!
        #                                       Return the named .exem (stripped of comments):
        f_name = function_name
        #if len(function_name) > 4 and function_name[-4:] == '_stf':  # Remove "_stf" when naming the .exem file.
        #    f_name = f_name[0:-4]
        test_code += "    self.assertEqual(get_expected_io('" + f_name + ".exem'"
        if not together:  # Test examples separately.
            test_code += ", example_id=" + str(example_id)
        test_code += "), actual_io_trace)\n"
        if together:
            break  # One, all-inclusive test only.

        # previous_example_id = example_id
        i += 1
    return test_code


def underscore_to_camelcase(s: str) -> str:
    """
    Take the underscore-separated value in 's' and return a CamelCase equivalent. Initial and final underscores
    are preserved, and medial pairs of underscores become single underscores.
    Credit https://stackoverflow.com/a/4303543/575012
    :database: not involved.
    :param s:  Eg, this_is_not_camel_case
    :return:  Eg,
    """
    def camelcase_words(words):
        for word in words:
            if not word:
                yield "_"
            yield word.capitalize()
    return ''.join(camelcase_words(s.split('_')))


if DEBUG and __name__ == "__main__":
    assert 'TestPrimeNumber' == underscore_to_camelcase('test_prime_number')
    assert 'Get_ThisValue' == underscore_to_camelcase('get__this_value'), underscore_to_camelcase('get__this_value')
    assert '_Get_ThisValue' == underscore_to_camelcase('_get__this_value'), underscore_to_camelcase('_get__this_value')
    assert '_Get_ThisValue_' == underscore_to_camelcase('_get__this_value_'), underscore_to_camelcase('_get__this_value')
    assert 'GetThisValue' == underscore_to_camelcase('get_this_value'), underscore_to_camelcase('get_this_value')
    assert 'Get_This_Value' == underscore_to_camelcase('get__this__value'), underscore_to_camelcase('get__this__value')
    assert "CamelCase" == underscore_to_camelcase("camel_case")
    assert 'Get_ThisValue' == underscore_to_camelcase('get__this_value')
    assert '_Get_ThisValue' == underscore_to_camelcase('_get__this_value')
    assert '_Get_ThisValue_' == underscore_to_camelcase('_get__this_value_')
    assert 'GetThisValue' == underscore_to_camelcase('get_this_value')
    assert 'Get_This_Value' == underscore_to_camelcase('get__this__value')


def from_file(filename: str) -> List[str]:
    """
    Return the named file's contents.
    :database: not involved.
    :param filename:
    :return:
    """
    # prefix = "./" if sys.platform != "win32" else ''
    try:
        handle = open(exemplar_path() + filename, "r")  # Eg, hello_world.exem
    except FileNotFoundError as err:
        print(err)
        sys.exit()
    lines = handle.readlines()
    handle.close()
    return lines


def to_file(filename: str, text: str) -> None:
    """
    :database: not involved.
    :param filename:
    :param text:
    :return:
    """
    # prefix = "./" if sys.platform != "win32" else ''
    try:
        handle = open(exemplar_path() + filename, 'w')  # Eg, TestHelloWorld.py.
    except FileNotFoundError as err:  # Any other error catchable?
        print(err)
        sys.exit()
    handle.write(text)
    handle.close()


def formal_params() -> str:
    """
    Example inputs occurring before anything else (assertions or output) are held to be arguments.
    Use the examples with Python's type() to create a formal parameters declaration. Report any inconsistency between
    the user examples in # of arguments or data type.
    :database: SELECTs example_lines.
    :return: formal parameters declaration, eg, i1: str, i2: int
    """
    result = ''
    sql = "SELECT example_id, line, line_type FROM example_lines ORDER BY el_id"  # All example lines, in order.
    cursor.execute(sql)
    rows = cursor.fetchall()
    previous_example_id = ''
    arguments = []  # List of data types.
    argument_total = -1
    goto_next_example = False
    i = 1
    for row in rows:
        example_id, line, line_type = row

        if goto_next_example and example_id != previous_example_id:
            goto_next_example = False  # Arrived at next example, so run the below gauntlet.

        if goto_next_example and example_id == previous_example_id:
            pass  # Not there yet.

        elif line_type == 'in':  # `line` is a leading input of current example.
            # Determine line's data type. (SQLite v Python: NULL v None, REAL v float, TEXT v str, BLOB v bytes)
            data_type = type(line)

            if argument_total == -1:  # Then still processing args of 1st example.
                arguments.append(data_type)
            elif len(arguments) == argument_total:  # Another input shouldn't have been reached.
                sys.exit("Too many arguments in example " + str(example_id) + " (Line content: " + line + ')')
            elif data_type is not arguments[i % argument_total]:
                if data_type is str:
                    print("arguments[" + i % argument_total + "] was thought to be of type " +
                          arguments[i % argument_total] + " but is now TEXT to allow value '" + line + "'")
                    arguments[i % argument_total] = str
                elif data_type is float and arguments[i % argument_total] is int:
                    print("Example " + str(example_id) + " has argument " + line + " where a value of type INT was " +
                          "expected. The argument's data type is now FLOAT to accommodate it.")
                    arguments[i % argument_total] = float
                else:
                    sys.exit("Example " + str(example_id) + " has argument " + line + " where a value of type " +
                             arguments[i % argument_total] + " was expected.")
        else:  # Past leading inputs of current example.
            if argument_total == -1:
                argument_total = len(arguments)  # (Assumes there'll be an assertion or output for every example.)
            goto_next_example = True

        # Set up for next row.
        previous_example_id = example_id
        i += 1

    # Done collecting argument data.
    for i in arguments:
        result += 'i' + i + ": " + arguments[i] + ", "  # Creating formal param list. Eg, i1: str, i2: int,
    return result.rstrip(", ")


def most_repeats_in_an_example(assertion=None, assertion_scheme=None) -> Tuple:
    """
    Whether we have a given assertion or assertion scheme, find the example that has the most of them.
    :param assertion: condition of interest
    :param assertion_scheme: scheme of interest
    :return: count of matching assertion/scheme in a found example_id, as a tuple. Eg, 5, 2
    """
    if assertion:
        where_clause = "condition = '" + assertion + "'"
    else:
        where_clause = "scheme = '" + scheme(assertion_scheme) + "'"
    cursor.execute("SELECT COUNT(*), example_id FROM conditions WHERE " + where_clause + """ GROUP BY example_id
            ORDER BY COUNT(*) DESC, example_id LIMIT 1""")
    row = cursor.fetchone()
    if row[0]:
        return row  # count, example_id
    else:
        return 0, -1


def fill_conditions_table() -> None:
    """
    Fill the conditions table with all the 'truth' in the .exem, formatted per assertion_triple(), after determining
    each's condition_type if possible.
    conditions.control_id gets filled in later, in condition_type-specific functions.
    :database: SELECTs example_lines. INSERTs conditions.
    :return:
    """
    # Step 1: Dump example_lines into conditions table.
    all_conditions = []
    cursor.execute("SELECT el_id, example_id, line FROM example_lines WHERE line_type = 'truth'")
    example_lines = cursor.fetchall()

    for example_line in example_lines:
        el_id, example_id, condition = example_line

        left_operand, operator, right_operand = assertion_triple(condition)  # Format condition.
        if left_operand is not None:
            condition = left_operand + operator + right_operand

        all_conditions.append((el_id, example_id, condition, scheme(condition), left_operand, operator, right_operand))

    cursor.executemany("""INSERT INTO conditions (el_id, example_id, condition, scheme, left_side, relop, right_side) 
    VALUES (?,?,?,?,?,?,?)""", all_conditions)

    # Step 2: Fill in conditions.condition_type. (This is a separate step so that our get_condition_type()'s
    # most_repeats_in_an_example() call can work (it selects from the conditions table).)
    cursor.execute("SELECT el_id, example_id, condition, scheme FROM conditions")
    rows = cursor.fetchall()

    for row in rows:
        el_id, example_id, condition, row_scheme = row

        condition_type = get_condition_type(el_id, condition)  # GET_CONDITIONS_TYPE()

        cursor.execute("UPDATE conditions SET condition_type = ? WHERE el_id = ?", (condition_type, el_id))  # .executemany some day...

    return
    """ May become useful if more condition tables are needed:
    cursor.execute(""SELECT example_id, scheme, COUNT(*) FROM conditions 
                        GROUP BY example_id, scheme HAVING COUNT(*) > 1"")
    repeats = cursor.fetchall()

    # Set intraexample_repetition column.
    # Below can be made more efficient via an executemany per value of intraexample_repetition
    for row in repeats:
        # print("debugging  row[0], row[1], row[2]", row[0], row[1], row[2])
        example_id, scheme, count = row
        cursor.execute("UPDATE conditions SET intraexample_repetition = ? WHERE example_id = ? AND scheme = ?",
                       (count, example_id, scheme))

    # Categorize all conditions as simple assignment, iterative, or selective.  Currently, the criteria is simply,
    # if i1 is being equated with 0 repetition, call it SA. Else, if there's repetition, call it iterative, else,
    # selective.
    simple_assignments, iteratives, selectives = [], [], []
    conditions = cursor.execute("SELECT rowid, condition, intraexample_repetition FROM conditions")
    for row in conditions:
        rowid, condition, intraexample_repetition = row
        # If condition names a variable and it occurs 1x.
        if get_variable_name(condition, 'i1') and intraexample_repetition == 0:
            simple_assignments.append((rowid,))
        elif intraexample_repetition > 0:
            iteratives.append((rowid,))
        else:
            selectives.append((rowid,))
    cursor.executemany("UPDATE conditions SET type = 'simple assignment' WHERE rowid IN (?)", simple_assignments)
    cursor.executemany("UPDATE conditions SET type = 'iterative' WHERE rowid IN (?)", iteratives)
    cursor.executemany("UPDATE conditions SET type = 'selective' WHERE rowid IN (?)", selectives)"""


def exemplar_path():
    if sys.platform == "win32":
        return __file__[0:__file__.rfind('\\')+1]  # Eg, C:\Users\George\Documents\
    else:
        return __file__[0:__file__.rfind('/')+1]


def run_tests(class_name: str) -> str:
    """
    Run the unittest tests of the named file and print and return the results.
    :database: not involved.
    :param class_name:
    :return: results of the tests
    """
    TestClass = importlib.import_module(class_name)
    importlib.reload(TestClass)  # Lest the first TestClass be re-run.
    suite = unittest.TestLoader().loadTestsFromModule(TestClass)
    print("Running", class_name)
    test_results = unittest.TextTestRunner().run(suite)
    print(len(test_results.errors), "errors and", len(test_results.failures), "failures")
    return test_results


def get_final_el_id() -> int:
    cursor.execute("""SELECT max(el_id) FROM example_lines""")
    return cursor.fetchone()[0]


def get_last_el_id(first_el_id: int, condition_type: str) -> int:
    """
    Pull from table for_loops for a FOR loop so that the /last/ of that loop's blocks is used.
    :param first_el_id:
    :param condition_type: 'for'|'if'
    :return: the last_el_id of the associated control
    """
    cursor.execute("""SELECT control_id FROM cbt_temp_last_el_ids WHERE first_el_id=?""", (first_el_id,))
    control_id = cursor.fetchone()[0]
    assert condition_type[0:2] == control_id[0:2], condition_type[0:2] + " is *not* " + control_id[0:2]
    if condition_type == 'if':
        cursor.execute("""SELECT last_el_id FROM cbt_temp_last_el_ids WHERE first_el_id=?""", (first_el_id,))
    else:
        cursor.execute("SELECT max(last_el_id) FROM for_loops WHERE control_id=? AND first_el_id<=? AND last_el_id>?",
                       (control_id, first_el_id, first_el_id))
    last_el_id = cursor.fetchone()[0]
    assert last_el_id is not None, "No last_el_id found for: control_id, first_el_id " + str(control_id) + ', ' + str(first_el_id)
    return last_el_id


def get_last_el_id_of_example_at(el_id: int) -> int:
    cursor.execute("""SELECT max(el_id) FROM example_lines WHERE example_id = 
    (SELECT example_id FROM example_lines WHERE el_id = ?)""", (el_id,))
    return cursor.fetchone()[0]


def get_first_el_id_of_example_at(el_id: int) -> int:
    cursor.execute("""SELECT min(el_id) FROM example_lines WHERE example_id = 
    (SELECT example_id FROM example_lines WHERE el_id = ?)""", (el_id,))
    return cursor.fetchone()[0]


def get_condition_type(el_id: int, condition=None) -> str:
    """
    Look up the condition_type of specified el_id, or instead determine it from `condition` if that is provided.
    :param el_id:
    :param condition:
    :return: 'if'|'for'|'assign'
    """
    if not condition:
        cursor.execute("SELECT condition_type FROM conditions WHERE el_id=?", (el_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None
    else:  # Determine if/for/assign
        condition_type = 'if'  # Default

        left, operator, right = assertion_triple(condition)

        # Lines that equate a digit to a (non-input) variable are noted, if their scheme repeats intra-example, as
        # **** FOR_SUSPECTS ****
        if right == "__example__":  # Special case: repeats only inter-example because it delimits them.
            condition_type = "for"
        # Eg, 3 == guess_count
        # elif left.isdigit() and   Doesn't work for prime_number.exem.
        elif "==" in condition and most_repeats_in_an_example(assertion_scheme=condition)[0] > 1:
            condition_type = "for"

        elif left is None:  # Then `condition` is compound or hasn't a relational operator (eg, 'True').
            condition_type = 'if'

        # Math operations not leading to an immediate output substitution are deemed 'if' conditions. (This should be
        # narrower or at least kept after the 'for' qualifications.)
        elif ('%' in left or '*' in left or '+' in left or '/' in left or '-' in left) and not \
            (assertion_triple(condition)[2] in get_line_item(el_id, 1, 'line') and
            get_line_item(el_id, 1, 'line_type') == 'out'):
            condition_type = 'if'

        # **** ASSIGN ***** Eg, 'myVar==i1', 'i2 == myVar', '3==count + 1' (for swapping out '3' in next line.)
        #                                                  previous line is input:
        elif "==" in condition and (('i1' in condition and get_line_item(el_id, -1, 'line_type') == 'in')
                                    or  # condition's literal is in next line, and that's an output:
                                    (assertion_triple(condition)[2] in get_line_item(el_id, 1, 'line') and
                                    get_line_item(el_id, 1, 'line_type') == 'out')):
            condition_type = "assign"  # (In future, backtrack to 'if' when this condition_type fails. todo)
        return condition_type


""" requires a mock database:
if DEBUG and __name__ == '__main__':
    assert "assign" == get_condition_type("myVar==i1")
    assert "assign" == get_condition_type("i2 == myVar")
    assert "assign" == get_condition_type("3==count + 1")
    assert "assign" == get_condition_type("name==i1")
"""

def get_unconditionals_post_control(first_el_id: int) -> List[str]:
    """
    Return the statement pattern occurring after given control statement.
    Since they reflect the same code, the types of the (pre-IF) lines of each iteration of a given FOR loop
    must be the same. todo create method to also count IF conditions, and their NOTed counterparts, repeated each iteration. why?
    :param first_el_id: of an IF or loop iteration
    :return: The list of line_types following first_el_id, eg, ['in','out','assign','for']
    """
    assert get_condition_type(first_el_id) in 'if|for'

    # Get all lines after first_el_id, in order, until the end of its example.
    cursor.execute("""SELECT el.line, el.line_type, c.condition_type FROM example_lines el 
    LEFT JOIN conditions c USING (el_id) WHERE el.el_id>? AND el.example_id=? ORDER BY el.el_id""",
                   (first_el_id, get_example_id(first_el_id)))
    rows = cursor.fetchall()
    assert len(rows), \
        "get_unconditionals_post_control()'s argument must point to a FOR or IF, which must have a line following."
    # Commented these 2 out 9/17/19 because I no longer see why an IF should be treated differently.
    # if get_condition_type(first_el_id) == 'if':
    #     return rows[0][2]  # line_type, eg, 'in'.
    # Gather the line types until end or IF reached, then return them.
    pattern = []
    for line, line_type, condition_type in rows:
        if line_type == 'truth' and condition_type == 'if':
            pattern.append('if')
            break  # Bets are off after an IF.
        else:
            if line_type == 'truth':
                line_type = condition_type
            pattern.append(line_type)  # in/out/assign/for
    return pattern  # The preamble (as we've defined it) is over.


def insert_iteration_into_cbt(loop_variable: str, last_el_id_of_iteration: int, last_or_not: int, control_id: str,
                              first_el_id: int, iteration: int, local_iteration: int) -> None:
    """
    Into control_block_traces insert record of given iteration (then update it with what is known of its endpoint).
    :database: INSERTs control_block_traces.
    :param loop_variable: '__example__' or not
    :param last_el_id_of_iteration:
    :param last_or_not: 0==false, 1==local last iteration, 2==global last iteration
    :param control_id: eg, "for1:0"
    :param first_el_id: First el_id of given loop iteration. Eg, 40
    :param iteration: 0-based global count
    :param local_iteration: 0-based local count. Needed because BREAK can end loops before their nominal endpoint.
    :return: None
    """
    cbt_id = str(control_id) + '_' + str(first_el_id)
    example_id = get_example_id(first_el_id)
    cursor.execute("INSERT INTO control_block_traces (cbt_id, example_id, first_el_id, control_id, iteration, "
                   "local_iteration) VALUES (?,?,?,?,?,?)", (cbt_id, example_id, first_el_id, control_id, iteration,
                                                             local_iteration))
    last_rowid = cursor.lastrowid  # Safer (than ?) as function calls can impact cursor.

    """Now update last_el_id* fields for the row just inserted. Each iteration's last_el_id is the el_id one prior 
    to the next iteration's first_el_id unless the loop has reached a (local or global) end, in which case endpoints 
    are handled by create_maybe_rows(). 4/8/19"""
    if loop_variable == '__example__':  # For internal use.
        cursor.execute("""UPDATE control_block_traces SET last_el_id = ? WHERE ROWID = ?""",
                       (get_last_el_id_of_example_at(first_el_id), last_rowid))
        # cursor.execute("SELECT last_el_id FROM control_block_traces WHERE ROWID=?", (lastrowid,))
        # print("debugging  last_el_id:", cursor.fetchone())

    elif not last_or_not:  # Common case.
        cursor.execute("UPDATE control_block_traces SET last_el_id = ? WHERE ROWID = ?",
                       (last_el_id_of_iteration, last_rowid))
    else:  # (Global or local) last iteration
        last_el_id_min = get_line_item(first_el_id, 1 + len(get_unconditionals_post_control(first_el_id)))
        last_el_id_max = get_last_el_id_of_example_at(first_el_id)  # improve on this too-generous max. todo
        assert last_el_id_min and last_el_id_max

        data = (cbt_id, example_id, first_el_id, control_id, iteration, local_iteration)

        # ************ CREATE_MAYBE_ROWS() **************
        one_endpoint = create_maybe_rows(first_el_id, last_el_id_min, last_el_id_max, data)  # =>None if >1 row created.

        # Store the 1st and last possible el_id of the current loop trace. one_endpoint may be defined as well.
        cursor.execute("UPDATE control_block_traces SET last_el_id_min=?, last_el_id=?, last_el_id_max=? WHERE ROWID=?",
                       (last_el_id_min, one_endpoint, last_el_id_max, last_rowid))


def get_line_item(start_el_id: int, distance: int, item = 'el_id') -> int:
    """
    get_line_item(15, 1) means return the closest el_id value to 15 that is >15.
    get_line_item(15, -2) means return the 2nd closest el_id value to 15 that is <15.
    :database: SELECTs example_lines
    :param start_el_id:
    :param distance: the # of el_id values from the given el_id.
    :param item: the example_lines field to return (el_id by default).
    :return: the el_id value 'distance' ordered records from 'el_id' in table example_lines. Or None if none.
    """
    if distance < 0:
        direction = 'DESC'
        sign = '<'
    else:
        direction = 'ASC'
        sign = '>'
    cursor.execute("SELECT " + item + " FROM example_lines WHERE el_id " + sign + " ? ORDER BY el_id " + direction +
                   " LIMIT ?", (start_el_id, abs(distance)))
    rows = cursor.fetchall()
    # assert rows, "No rows found with start_el_id " + str(start_el_id) + " and distance " + str(distance)
    return_el_id = None
    for row in rows:
        return_el_id = row[0]
    return return_el_id


def are_preambles_consistent(loop_preamble: List[str], iteration_preamble: List[str]) -> int:
    """
    iteration preambles (eg, ['in','out','if']) only have to match up to loop_preambles' first IF. (For an example of
    why, see leap_year.exem.)
    :param loop_preamble:
    :param iteration_preamble:
    :return: True or False
    """
    if loop_preamble[-1] == 'if':
        length = len(loop_preamble) - 1
        return loop_preamble[0:length] == iteration_preamble[0:length]
    else:
        return loop_preamble == iteration_preamble


def store_fors() -> None:
    """
    Create a cbt record for each instance of a for-loop scheme. The cbt row will scope the blocks. (Iteration endpoints
    aka last_el_ids are estimated in a call.)
    Create a controls record for each for-loop scheme. Its python field notes the loop variable's first and last values.
    Note the new control_id in all related 'conditions' records.
    N.B. This function runs before get_function() and its update_for_loops_table() call.
    :database: SELECTs conditions. INSERTs for_loops, control_block_traces (indirectly), controls. UPDATEs conditions.control_id.
    :return: None
    """
    schemes_seen = []  # To avoid redundant analyses.
    # Loop over every assignment to a FOR loop variable (id'ed by fill_conditions_table()).
    cursor.execute("""SELECT el_id, condition, example_id FROM conditions 
    WHERE condition_type='for' ORDER BY el_id""")  #example_id=? AND   , (example_id,))
    for_conditions = cursor.fetchall()
    control_count = {'for': 0}  # (Probably should be changed from a dict to for_count: int.)
    for row in for_conditions:  # PER SCHEME

        # Loop over every instance of `condition`
        el_id, condition, example_id = row
        assertion_scheme = scheme(condition)  # Compress and abstract the integers.
        periods = [0]  # To hold the total # of iterations per use of this loop. Can change due to BREAK.
        if assertion_scheme not in schemes_seen:  # (We assume loop variables aren't re-used. fixme bad assumption)
            # (We also assert loop variable's consistency re: increment and starting integer.)
            cursor.execute("SELECT el_id, condition FROM conditions "
                           "WHERE scheme=? ORDER BY el_id", (assertion_scheme,))  #example_id=? AND    example_id,
            iteration_instances = cursor.fetchall()
            loop_variable, loop_increment, next_constant, max_constant = None, 1, None, 0
            control_id = 'for' + str(example_id) + ':' + str(control_count['for'])
            iteration_count = 1  # Easier to start this at 1 (and subtract 1 in call to insert_iteration_into_cbt()).
            local_iteration = 0
            # Gather info for a call to insert_iteration_into_cbt() for each iteration of assertion_scheme.
            for row in iteration_instances:  # PER implied ITERATION

                iteration_el_id, iteration_condition = row
                constant, operator, variable = assertion_triple(iteration_condition)  # Eg: 5, ==, guess_count
                if type(constant) == int:
                    constant = int(constant)  # Needed for comparison with other (integer) constants.
                # Determine loop variable endpoint:
                if abs(constant) > max_constant:
                    max_constant = constant

                how_last = 0  # By default
                if iteration_count == len(iteration_instances):  # Globally last iteration
                    how_last = 2                          # of assertion_scheme.
                    last_el_id_of_iteration = None  # Ie, unknown
                else:
                    # Get the el_id that is /one el_id before/ the start of the next iteration (though see below for a
                    # conditional invalidation).
                    last_el_id_of_iteration = get_line_item(iteration_instances[iteration_count][0], -1)
                    # Get the next loop variable comparison value (for use below).
                    next_constant = int(assertion_triple(iteration_instances[iteration_count][1])[0])

                if not loop_variable:  # then this is the overall first iteration of assertion_scheme.
                    loop_variable = variable  # This doesn't change over the assertion_scheme.
                    first_value = constant
                    first_el_id = iteration_el_id
                    local_first_el_id = iteration_el_id
                    loop_preamble = get_unconditionals_post_control(first_el_id)  # Should be same each iteration.
                elif iteration_count == 2:  # 2nd iteration, globally speaking.
                    loop_increment = constant - first_value  # Doesn't change.
                    iteration_preamble = get_unconditionals_post_control(iteration_el_id)
                    assert are_preambles_consistent(loop_preamble, iteration_preamble)
                else:  # >2nd iteration. Sanity check the increment.
                    assert (loop_increment == constant - prior_value) or (constant == first_value), \
                        "FOR loop increment " + str(constant - prior_value) + " found where " + str(loop_increment) + \
                        " was expected, at condition: " + iteration_condition
                    iteration_preamble = get_unconditionals_post_control(iteration_el_id)
                    # Below commented out due to prime_number.exem causing:
                    #   "preambles inconsistent between l.p. '['in', 'assign', 'if']' and i.p. '['in', 'if']'"
                    # assert are_preambles_consistent(loop_preamble, iteration_preamble), \
                    #     "preambles inconsistent between l.p. '" + str(loop_preamble) + "' and i.p. '" + \
                    #     str(iteration_preamble) + "'"

                if constant == first_value:  # Back to square one. (Never true for the __example__ loop.)
                    local_iteration = 0
                    local_first_el_id = iteration_el_id  # Update this to allow >1 for_loops table inserts with 1 control_id.

                if next_constant == first_value:  # Then the current el_id completes the loop. (Never true for the
                    # __example__ loop.)
                    how_last = 1  # Local last, ie, the last iteration before an outer loop restarts this loop.
                    last_el_id_of_iteration = None  # Ie, unknown
                    periods.append(iteration_count - periods[len(periods) - 1])  # Append latest period.
                    cursor.execute(
                        "INSERT INTO for_loops (control_id, example_id, first_el_id, increment) VALUES "
                        "(?,?,?,?)", (control_id, example_id, local_first_el_id, loop_increment))
                    # (period filled in below and last_el_id will be filled in by update_for_loops_table().)

                assert loop_variable == variable, variable + " found where FOR loop variable " + loop_variable + \
                    " was expected, at assertion: " + iteration_condition

                # INSERT_ITERATION_INTO_CBT **********************************************************
                insert_iteration_into_cbt(loop_variable, last_el_id_of_iteration, how_last, control_id,
                                          iteration_el_id, iteration_count-1, local_iteration)  # The -1 is for 0 base.
                prior_value = constant
                iteration_count += 1
                local_iteration += 1

            # scheme(condition) exhausted.

            cursor.execute("INSERT INTO for_loops (control_id, example_id, first_el_id, increment) VALUES (?,?,?,?)",
                           (control_id, example_id, local_first_el_id, loop_increment))
            periods.append(iteration_count - periods[len(periods) - 1] -1)  # Append last period. (-1 due to += 1 above)
            assert max(periods) == (max_constant - first_value + 1) / loop_increment
            cursor.execute("UPDATE for_loops SET period=? WHERE control_id=?", (max(periods), control_id))

            # Create the control record. Eg, 'for guess_count in range(0, 6)'
            if not max_constant:  # A 1 iteration loop.
                max_constant = first_value
            # if max_constant > 0:
            tmp = max_constant + 1  # Needed due to Python's exclusive range-ing.
            # else:
            #     tmp = max_constant - 1
            # Eg, python = "for __example__ in range(0, 2, 1):"
            python = "for " + loop_variable + " in range(" + str(first_value) + ', ' + str(tmp) + ', ' + \
                     str(loop_increment) + '):'
            cursor.execute("INSERT INTO controls (control_id, example_id, python, first_el_id) VALUES (?,?,?,?)",
                           (control_id, get_example_id(el_id), python, first_el_id))

            # Note the condition's new control_id in conditions.
            cursor.execute("UPDATE conditions SET control_id=? WHERE example_id=? AND scheme=?",
                           (control_id, example_id, assertion_scheme))

            schemes_seen.append(assertion_scheme)
            control_count['for'] += 1


# UNUSED because store_for_loops() is called /before/ the last_elstore_fors, and store_ifs(), /inside/ it. 4/8/19
def unused_fill_control_block_traces() -> None:  # Note scopes.
    """
    We store each block trace's first and last el_id, the starting Python line, and a unique id per control structure.
    todo last_el_id2 and indents via another loop.
    todo deal with for-loop false positives (non-loops). Perhaps by updating that condition_type to 'assign' in
    conditions and removing the related control record as soon as last_el_id2's are determined. 3/4/19
    :database: All indirectly: SELECTs conditions. INSERTs control_block_traces. UPDATEs conditions, control_block_traces.
    :return:
    """
    store_fors()  # Loops before IFs to allow determination of whether an IF is in a loop.
    store_ifs()


def get_local_el_id_of_open_loop(extremity: str, el_id: int) -> int:
    """
    Return first or last el_id of line el_id's innermost iteration (even if el_id is 5, for '__example__==0').
    :param extremity: 'first' or 'last'
    :param el_id: current el_id
    :return: el_id of the open loop
    """
    assert extremity == 'first' or extremity == 'last'
    if extremity == 'first':
        selection = "SELECT cbt.first_el_id"
    else:
        selection = "SELECT ctlei.last_el_id"
    cursor.execute(selection + """ FROM control_block_traces cbt JOIN cbt_temp_last_el_ids ctlei USING (cbt_id) 
        WHERE cbt.example_id = ? AND 
              substr(cbt.control_id,1,3) = 'for' AND  -- (SQL's substr() is 1-based.)
              cbt.first_el_id <= ? AND 
              ctlei.last_el_id >= ? 
        ORDER BY cbt.first_el_id DESC 
        LIMIT 1""", (get_example_id(el_id), el_id, el_id))
    return cursor.fetchone()[0]


# unused
def unused_condition_type(el_id: int) -> str:
    cursor.execute("SELECT condition_type FROM conditions WHERE el_id=?", (el_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


# unused
def unused_get_last_el_ids(control_type: str, el_id: int) -> Tuple[int, int]:
    """
    The minimum and maximum possible last_el_id of the control being constructed.
    :param control_type: 'if' only. 4/8/19.
    :param el_id: first el_id of the control being built.
    :return:
    """
    # todo Another way to restrict last_el_id possibilities: if an example line only appears when one IF condition
    # is true, assume it is part of that IF's consequent and no others.

    # last_el_id_max: An IF block cannot possibly extend into another example, or any other control that doesn't
    # entirely nest within that IF.  (Begs the qn of where "that IF" ends.)
    local_last_el_id_of_open_loop = get_local_el_id_of_open_loop('last', el_id)
    # commenting below out because I cannot rule out a user naming an input (ie, an 'assign') at end of a block.
    # # Assignments do not result in a line of code so cannot serve as block ends.
    # while condition_type(last_el_id_max) == 'assign':
    #     last_el_id_max = get_line_item(last_el_id_max, -1)

    last_el_id_min = el_id
    # Below commented out because its logic is presently handled in create_maybe_rows()
    # An IF needs >=1 lines of consequent to make sense.
    # while condition_type(last_el_id_min) == 'if':
    #     last_el_id_min = get_line_item(last_el_id_min, 1)  #
    return last_el_id_min, local_last_el_id_of_open_loop


def is_IF_likely_same(el_id1: int, el_id2: int) -> int:
    """
    # Are example lines el_id1 and el_id2 the same condition, of condition_type 'if', and succeeded by similar lines?
    :param el_id1:
    :param el_id2:
    :return: Boolean
    """
    cursor.execute("SELECT condition, condition_type FROM conditions WHERE el_id=?", (el_id1,))
    row1 = cursor.fetchone()
    cursor.execute("SELECT condition, condition_type FROM conditions WHERE el_id=?", (el_id2,))
    row2 = cursor.fetchone()
    if not row1 or not row2 or not row1[0] == row2[0] or not row1[1] == row2[1] == 'if':
        return False
    else:
        return get_unconditionals_post_control(el_id1) == get_unconditionals_post_control(el_id2)


def get_control_conflicts(table="cbt_temp_last_el_ids") -> int:  # todo verify while default table is used
    """
    Any control A that straddles a control B's last_el_id_maybe, i.e., starts between control B's first_el_id and
    last_el_id_maybe and ends after last_el_id_maybe, invalidates that last_el_id_maybe, because controls can't overlap.
    :param table: Eg, "for_loops"
    :return: True if conflict found, False otherwise.
    """
    cursor.execute("SELECT * FROM " + table + " A, " + table + " B WHERE "
                   "A.first_el_id>B.first_el_id AND "  # For control A to start 
                   "A.first_el_id<B.last_el_id AND "  # within control B and 
                   "A.last_el_id>B.last_el_id")  # finish after it is impossible.
    return cursor.fetchall()
    #return True if rows else False


def create_maybe_rows(first_el_id: int, min_el_id: int, max_el_id: int, data: Tuple) -> Any:
    """
    Create a cbt row for every possible (currently that means skipping truth lines only) endpoint. 5/8/19
    :param first_el_id: first el_id of the IF or loop iteration concerned.
    :param min_el_id: Starting el_id to consider for endpoint
    :param max_el_id: Last el_id to consider for endpoint
    :param data: Data to insert alongside last_el_id_maybe
    :return: None, or the el_id of the one maybe endpoint
    """
    # assert len(data) == 5, "data elements [0] - [3]:" + str(data[0]) + ', ' + str(data[1]) + ', ' + str(data[2]) + \
    #                        ', ' + str(data[3]) + ', ' + str(data[4])
    if len(data) == 4:  # Then adjust this IF block by adding FOR-only fields.
        lis = []  # First turn `data` into a list.
        for datum in data:
            lis.append(datum)
        lis.append(None)
        lis.append(None)
        data = lis  # Restore original name.

    # cursor.execute("""SELECT el_id FROM example_lines el LEFT JOIN conditions c USING (el_id)
    # WHERE el.el_id>=? AND el.el_id<=? AND (c.condition_type!='assign' OR c.condition_type IS NULL)""", (first, last))
    cursor.execute("""SELECT el_id FROM example_lines el WHERE el.el_id>=? AND el.el_id<=? AND el.line_type!='truth'""",
                   (min_el_id, max_el_id))
    """The last_el_id can't be an assignment because that doesn't result in code, which causes a syntax error 
    when there is no code indented under a control. Example:
        guess_count + 1 == 3
    doesn't work as the last line of control 'if guess == secret:' even though that's the line that follows it,
    because then nothing appears under that IF in the generated code. 2019-04-28
    
    Endpoint can't be a FOR or IF either, as those are required to have line/s following them. 2019-04-29"""

    maybes = cursor.fetchall()
    assert len(maybes), "Error: no valid control endpoint exists between example line ids " + min_el_id + " and " + \
                        max_el_id + ", inclusive"
    if len(maybes) > 1:
        # Get greatest endpoint of the controls, if any, that opened after this iteration started.
        # get_greatest_endpoint_of_any_controls_that_opened_this_iteration(first_el_id)
        # No, instead get dead zones where a control starts and therefore the current cbt can't end until it does.

        for row in maybes:
            last_el_id_maybe = row[0]
            cursor.execute("""INSERT INTO control_block_traces (cbt_id, example_id, first_el_id, last_el_id_maybe, 
            control_id, iteration, local_iteration) VALUES (?,?,?,?,?,?,?)""",
                           (data[0], data[1], data[2], last_el_id_maybe, data[3], data[4], data[5]))
    else:
        return maybes[0][0]  # Only 1 endpoint, so it's not a "maybe". Return it.


def store_ifs() -> None:  # example_id: int) -> None:  # into control_block_traces table to track their block scope.
    """
    # Todo Differentiate elif vs else vs if 4/2/19
    Where repeats are found, their `conditions` table record is updated to note the (pre-existing) control_id.
    :database: SELECTs conditions. INSERTs control_block_traces, controls. UPDATEs conditions.
    :return None:
    """
    # First, pull all example_id's IF conditions (as detected by fill_conditions_table()).
    cursor.execute("""SELECT el_id, condition, scheme FROM conditions WHERE condition_type = 'if' --AND example_id=?
    ORDER BY condition, el_id""")
    ifs = cursor.fetchall()
    control_count = 0  #{'if': 0}
    prior_row = [None, None, None]

    for row in ifs:
        el_id, condition, scheme = row
        example_id = get_example_id(el_id)

        if prior_row[1] != condition:  # New control. Insert it.
            control_id = 'if' + str(example_id) + ':' + str(
                control_count)  # ['if'])  'if'+example_id of first occurrence
            control_count += 1
            python = "if " + condition + ':'

            cursor.execute("INSERT INTO controls (control_id, example_id, python, first_el_id) VALUES (?,?,?,?)",
                       (control_id, example_id, python, el_id))

        # Insert the current IF condition into cbt table.
        cbt_id = control_id + '_' + str(el_id)  # Eg, 'if3:1_45'
        # min, max = get_last_el_ids('if', el_id)  # Eg, 125, 130 for el_id 120 in guess4.
        last_el_id_min = get_line_item(el_id, 1)  # Next el_id.
        last_el_id_max = get_local_el_id_of_open_loop('last', el_id)  # Last el_id of el_id's innermost iteration.
        one_endpoint = last_el_id_max
        if last_el_id_min != last_el_id_max:  # Find the last_el_id_maybe el_id's and add them to cbt if there's >1:
            one_endpoint = create_maybe_rows(el_id, last_el_id_min, last_el_id_max, (cbt_id, example_id, el_id, control_id))
        if one_endpoint:
            # We have a definite last_el_id.
            cursor.execute("""INSERT INTO control_block_traces (cbt_id, example_id, first_el_id, last_el_id, control_id) 
            VALUES (?,?,?,?,?)""", (cbt_id, example_id, el_id, one_endpoint, control_id))

        prior_row = row

        """
        # Determine if this IF is already noted (assumes conditions are unique), and within the open loop started
        # most recently.  ("assumes conditions are unique" is bad fixme)
        cursor.execute("SELECT min(el_id), max(el_id) FROM conditions WHERE condition_type='if' AND condition=? AND 
        el_id<?", (condition, el_id))  # example_id,
        first, last = cursor.fetchone()  # (None, None) at minimum.
        if first:  # Candidate IF/s found.
            for past_el_id in range(last, first-1, -1):
                if is_IF_likely_same(el_id, past_el_id):
                    cursor.execute("SELECT control_id FROM conditions WHERE el_id=?", (past_el_id,))
                    control_id = cursor.fetchone()[0]
                    if get_local_el_id_of_open_loop('first', el_id) <= past_el_id:
                        # IF is w/in loop, so it must already be in CBT and have a control_id.
                        # So just update 'conditions' at IF's 'el_id' with the found control_id.
                        cursor.execute("UPDATE conditions SET control_id=? WHERE el_id=?", (control_id, el_id))
                        continue  # Advance to next IF from the conditions table.

        if not control_id:  # This IF is new.
            control_id = 'if' + str(example_id) + ':' + str(control_count['if'])
            cursor.execute("INSERT INTO controls (control_id, example_id, python, first_el_id) VALUES (?,?,?,?)",
                           (control_id, example_id, "if " + condition + ':', el_id))
            control_count['if'] += 1

        # Note current IF condition's control_id.
        cursor.execute("UPDATE conditions SET control_id=? WHERE el_id=?", (control_id, el_id))"""


def get_last_el_id_maybes() -> Tuple[List[str], List[int]]:  #example_id: int
    """
    After determining which cbt_id's (trace blocks) have an unknown endpoint to their scope, create and run a query
    whose every row has a last_el_id_maybe value for all of them.
    :return: Tuple[list of cbt_id values, list of last_el_id_maybe values], or Tuple[None, None]
    """
    # 1st determine which cbt_id blocks not already in the ctlei have an unknown endpoint.
    # (The selected cbt_id blocks will either be of for-loops or IFs, exclusively.)
    cursor.execute("""SELECT DISTINCT cbt.control_id, cbt.cbt_id, cbt.example_id, cbt.first_el_id 
       FROM control_block_traces cbt 
      WHERE cbt.last_el_id_maybe IS NOT NULL AND                                        -- Tentative endpoint and
            cbt.cbt_id NOT IN (SELECT ctlei.cbt_id FROM cbt_temp_last_el_ids ctlei)""")  # still not in place.
    # Eg, for1_100 and for1_320 for guess4.
    cbt_ids = cursor.fetchall()  # A list of (control_id, cbt_id, example_id) tuples (or the empty list).

    """
    Next, create a list of tuples with a last_el_id_maybe value for all of the cbt_id's with unknown endpoint, via  
    queries such as
    
    * 'SELECT t0.last_el_id_maybe 
       FROM control_block_traces t0 
       WHERE t0.cbt_id=\'for1_320\' AND t0.last_el_id_maybe IS NOT NULL 
       ORDER BY t0.last_el_id_maybe'
    when only one cbt_id block is missing an endpoint. 
    (Below example queries omit mention of IS NOT NULL.)
    
    * 'SELECT t0.last_el_id_maybe, t1.last_el_id_maybe 
    FROM control_block_traces t0, control_block_traces t1 
    WHERE t0.cbt_id=\'for1_100\' AND t1.cbt_id=\'for1_320\' 
    ORDER BY t0.last_el_id_maybe, t1.last_el_id_maybe'
    when there are exactly 2 cbt_id blocks missing an endpoint. This pulls an endpoint for both out of 
    the jar without replacement.
    
    * 'SELECT t0.last_el_id_maybe, t1.last_el_id_maybe, t3.last_el_id_maybe -- a join for each cbt_id with unknown end.
    FROM control_block_traces t0, control_block_traces t1, control_block_traces t2
    WHERE t0.cbt_id=\'for3_110\' AND t1.cbt_id=\'for5_780\' AND t2.cbt_id=\'for6_885\' -- a cartesian product. 
    ORDER BY t0.last_el_id_maybe, t1.last_el_id_maybe, t2.last_el_id_maybe
    when there are exactly 3 cbt_id blocks missing an exact endpoint.  
    N.B. These SELECTs require that the cbt table has a record of all last_el_id_maybe possibilities (many-to-1 cbt_id).    
    
    Note that it's fine if the cbt_ids do not share the same # of maybes because the SELECT does a cartesian product.
    """
    if not cbt_ids:
        return None, None
    else:
        # Clause starting points
        select = "SELECT t"
        from_sql = " \nFROM "
        where = " \nWHERE t"
        order_by = " \nORDER BY t"

        i = 0
        for cbt_id in cbt_ids:
            cbt_id = cbt_id[1]
            select += str(i) + ".last_el_id_maybe, t"
            from_sql += "control_block_traces t" + str(i) + ", "
            where += str(i) + ".cbt_id='" + cbt_id + "' AND t" + str(i) + ".last_el_id_maybe IS NOT NULL AND t"
            order_by += str(i) + ".last_el_id_maybe, t"
            i += 1
        query = select[0:-3] + from_sql[0:-2] + where[0:-6] + order_by[0:-3]  # Eg, see above.
        if DEBUG:
            print(query)
        cursor.execute(query)
        return cbt_ids, cursor.fetchall()  # control_id, cbt_id, and example_id are all used in caller


def add_control_info_to_example_lines() -> None:
    """
    Fill in example_lines' control_id and controller columns. The control_id is simply a copy from the conditions table.
    The controller value given is the nearest, earlier control_id whose block hasn't ended.
    :return: None
    """
    cursor.execute("""UPDATE example_lines SET control_id =
    (SELECT c.control_id FROM conditions c WHERE c.el_id=example_lines.el_id)""")

    cursor.execute("""UPDATE example_lines SET controller =
    (SELECT ctlei.control_id FROM cbt_temp_last_el_ids ctlei 
      WHERE ctlei.first_el_id<example_lines.el_id AND 
            ctlei.last_el_id>=example_lines.el_id 
    ORDER BY ctlei.last_el_id, ctlei.first_el_id DESC)""")
    # cursor.execute("SELECT * FROM example_lines")
    # rows = cursor.fetchall()
    # for row in rows:
    #     el_id = row[0]
    #     cursor.execute("SELECT control_id FROM cbt_temp_last_el_ids ctlei WHERE last_el_id>? ORDER BY last_el_id",
    #                    (el_id,))


def update_for_loops_table() -> None:
    """
    Update the for_loops table with last_el_id info now that that's available from the cbt table.
    This function requires that the c.b.t. and cbt_temp_last_el_ids tables have already had their FOR loop info filled in.
    :return None:
    """
    # For each FOR control in the target function.
    cursor.execute("""SELECT control_id FROM control_block_traces WHERE substr(control_id,1,3)='for' 
    GROUP BY control_id ORDER BY control_id""")
    control_ids = cursor.fetchall()
    for control_id in control_ids:
        control_id = control_id[0]

        # For each enactment of the current FOR loop (control_id), note its first_el_id or last_el_id if it's a
        # first or last iteration, respectively. Then insert together into for_loops.
        cursor.execute("""SELECT example_id, first_el_id, last_el_id FROM cbt_temp_last_el_ids WHERE control_id=? 
        ORDER BY first_el_id""", (control_id,))
        iterations = cursor.fetchall()
        prior = []
        # For each cbt of current control_id
        for row in iterations:
            example_id, first_el_id, last_el_id = row
            # `row` represents a new loop enactment if the prior row doesn't link up to it via last_el_id==first_el_id.
            if not prior:
                loop_first_el_id = first_el_id
            elif get_line_item(prior[2], 1) != first_el_id:
                # prior was the last of its kind. Insert it.
                cursor.execute("UPDATE for_loops SET last_el_id=? WHERE control_id=? AND first_el_id=?",
                               (prior[2], control_id, loop_first_el_id))
                loop_first_el_id = first_el_id
            prior = row  # prior[0, 1, 2] == prior["example_id", "first_el_id", "last_el_id"], respectively
        assert len(iterations) > 0, "No iterations found for control_id " + control_id
        # Update last FOR loop as well.
        cursor.execute("UPDATE for_loops SET last_el_id=? WHERE control_id=? AND first_el_id=?",
                       (prior[2], control_id, loop_first_el_id))


def remove_examples_loop(code_list: List[str]) -> List[str]:
    """
    Copy lines to output (stage 0) until "for __example__ in range(0, " reached (stage 1) then dedent.
    :param code_list: python code
    :return: python code without the __example__ loop
    """
    code_list_out = []
    stage = 0
    for line in code_list:
        if stage == 0 and line.strip()[:28] == "for __example__ in range(0, ":
            stage = 1
        elif stage == 1:
            code_list_out.append(line[4:])  # Dedent
        else:
            code_list_out.append(line)
    assert stage == 1, "Error: remove_examples_loop() never advanced beyond Stage " + str(stage)
    return code_list_out


def get_function(file_arg: str) -> int:  #, example_id: int) -> int:
    """
    Attempt to find an example-satisfying function then report success or failure in two stages.
    Stage 1 searches for a function that passes all examples as part of the same (__example__) FOR loop.
    Stage 2 renames that TestX.py (to TestX.tmp) before creating another without the artificial FOR loop and with a
    unit test per user example.
    :param file_arg:
    :return SUCCESS or not SUCCESS:
    """
    function_count = 0  # The # of generated functions

    # Add the known FOR endings (IFs are not yet ended) to the cbt_temp_last_el_ids (ctlei) table.
    cursor.execute("""INSERT INTO cbt_temp_last_el_ids 
                        SELECT cbt_id, example_id, first_el_id, control_id, last_el_id FROM control_block_traces 
                        WHERE last_el_id IS NOT NULL""")
    # (for cbt_id's whose last_el_id is not null, there should be only one cbt record (and its last_el_id_maybe
    # should be null)).

    # With the pre-determinable databased, gather all the last_el_id (block scope ending) possibilities to iterate
    # through them.
    cbt_ids, for_maybes = get_last_el_id_maybes()  # ********* get_last_el_id_maybes of for-loops ********
    if not for_maybes:
        for_maybes = [()]  # To force 1 iteration of loop below despite having 0 for-loop related last_el_id_maybe's.

    for for_maybes_row in for_maybes:  # Each iteration creates a cbt_temp_last_el_ids table with endings for consideration.

        # (No longer forking because PyCharm will only show the original process and worse, the database
        # becomes trial-specific. That makes a simple loop with database ROLLBACK a better option. 4/10/19)
        # if pid == 0:  # We're in the child, meaning the database was changed in the last iteration and needs disposal.
        #     exit()
        # # fork() to create a parent and child that each have their own copy of the database.
        # pid = os.fork()  # The parent forks off (another) identical child process.
        # if pid != 0:
        #     print("post-fork in parent before circling back")
        #     continue  # Only children get to play.)

        cursor.execute("BEGIN")  # Turn off autocommit mode, so these changes can be discarded if any test fails.
        # See what endpoint values (eg, 105 and 325 (to 130 and 355) for guess4) allow all tests to pass.
        # Rollback should obviate cursor.execute("DELETE FROM cbt_temp_last_el_ids")  # Each trial run gets its own rows.

        # Next, instantiate a possible endpoint universe, one for-loop iteration (cbt_id) at a time.
        if cbt_ids:
            for i in range(len(cbt_ids)):
                # Eg, rows (for1_100, 105) and (for1_320, 325) are inserted for guess4. 4/7/19
                print("cbt_id, last_el_id:", cbt_ids[i][1], for_maybes_row[i])
                cursor.execute("""INSERT INTO cbt_temp_last_el_ids (control_id, cbt_id, example_id, first_el_id, last_el_id) 
                VALUES (?,?,?,?,?)""", (cbt_ids[i][0], cbt_ids[i][1], cbt_ids[i][2], cbt_ids[i][3], for_maybes_row[i]))
                #               cbt.control_id, cbt.cbt_id,  cbt.example_id
        # At this point there are endpoints postulated for all for-loop iterations. Stuff them into:
        update_for_loops_table()  # Needed for for0:0, at least.
        # Any overlapping for-loops? Then go to the next for_maybes_row.
        rows = get_control_conflicts("for_loops")
        if rows:
            for row in rows:
                print("Conflict row fields control_id, example_id, first_el_id, last_el_id:", end=" ")
                for field in row:
                    print(field, end=" ")
                print()
            cursor.execute("ROLLBACK")  # Wipe all db changes since BEGIN and try next for_maybes_row
            continue

        # ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF ** IF **
        # Having (theorized) endpoints for the for-loops helps greatly in constraining the possible IF endpoints.
        store_ifs()  # Put IF info into controls and cbt tables, including all last_el_id_maybe possibilities.
        # The cbt table is now in its final form for this trial. Only finishing the ctlei table remains.

        # # First, add the known IF endings to the cbt_temp_last_el_ids (ctlei) table.
        cursor.execute("""INSERT INTO cbt_temp_last_el_ids
                            -- old: Eg, for guess4, (for0:0_5, 130), (for0:0_135, 355), (for0:1_40, 65), etc.
                            SELECT cbt_id, example_id, first_el_id, control_id, last_el_id FROM control_block_traces
                            WHERE last_el_id IS NOT NULL AND substr(control_id,1,2)='if'""")

        # Then, a round of theorized IF endpoints.
        if_cbt_ids, if_maybes = get_last_el_id_maybes()  # ************ IF get_last_el_id_maybes *************
        if not if_maybes:
            if_maybes = [()]  # To force an iteration of the below loop, despite having no IF related last_el_id_maybe's

        for if_maybes_row in if_maybes:
            cursor.execute("SAVEPOINT if_endings_trial")  # SAVEPOINT
            # Add the endings that were made-up in store_ifs().
            if if_cbt_ids:
                for i in range(len(if_cbt_ids)):  # Add each of the needed hypothesized endings to the ctlei table.
                    # Eg, ?
                    print("if cbt_id, last_el_id:", if_cbt_ids[i][1], if_maybes_row[i])
                    try:
                        cursor.execute("""INSERT INTO cbt_temp_last_el_ids (control_id, cbt_id, example_id, first_el_id, 
                        last_el_id) VALUES (?,?,?,?,?)""", (if_cbt_ids[i][0],  # control_id
                                                            if_cbt_ids[i][1],  # cbt_id
                                                            if_cbt_ids[i][2],  # example_id
                                                            if_cbt_ids[i][3],  # first_el_id
                                                            if_maybes_row[i]))  # last_el_id
                        #                     cbt.control_id,  cbt.cbt_id,       cbt.example_id
                    except sqlite3.IntegrityError as e:
                        print(e)
                        cursor.execute("SELECT * FROM control_block_traces WHERE cbt_id=?", (if_cbt_ids[i][1],))
                        print(cursor.fetchall())
                        cursor.execute("SELECT * FROM cbt_temp_last_el_ids WHERE cbt_id=?", (if_cbt_ids[i][1],))
                        print(cursor.fetchall())
                        exit()
            # Table cbt_temp_last_el_ids is done.

            # A check to optimize for time:
            if get_control_conflicts():  # (we don't check 'if's alone because adding 'while' controls is a todo.)
                cursor.execute("ROLLBACK TO if_endings_trial")
                continue  # to next if_maybes_row.

            add_control_info_to_example_lines()  # Fill in control_id and controller columns.
            if DEBUG:  # Good to dump these as PyCharm's Database tool will only show data as of their last commit.
                print(dump_table("control_block_traces"))
            print(dump_table("controls"))
            print(dump_table("for_loops"))
            print(dump_table("cbt_temp_last_el_ids"))

            # Gen code and see if it passes the unit tests made from the examples.

            function_name = file_arg[0:-5]  # Remove ".exem" extension.
            signature = "def " + function_name + '(' + formal_params() + "):\n"

            #                              ***********************
            code_list = generate_code()  # **** GENERATE CODE ****

            code0 = signature + '\n'.join(code_list)  # Includes __example__ loop.
            code = signature + '\n'.join(remove_examples_loop(code_list))
            code = code.replace("        #return ", "        return ")  # For Stage 2, enable the return's.
            function_count += 1
            if DEBUG:
                print("\nStage 1 function", str(function_count) + ":\n" + code0, "\n")  # Print generated function.

            # Create an all-in-one unit test (Stage 1).
            test = "".join(from_file("starter"))  # Contains mocked print() and input functions etc.

            class_name = "Test" + underscore_to_camelcase(function_name)
            class_signature = "class " + class_name + "(unittest.TestCase):"
            test = test.replace('<class signature>', class_signature, 1)

            # for line in generate_tests(function_name + "_stf").splitlines(True):  # First for the sequential function.
            #     test += "    " + line  # Indent each line, as each test is part of a class.
            # ********* GENERATE TESTS ******** and add them to test.
            #example_id = if_cbt_ids[i][2] if if_cbt_ids else 0
            # Create a Stage 2 Test file that (drops the for __example__ loop and) breaks out the unit tests.
            tests = test
            for line in generate_tests(function_name).splitlines(True):  # Single unit test.
                test += "    " + line
            for line in generate_tests(function_name, together=False).splitlines(True):  # Unit tests broken out.
                tests += "    " + line  # Note the plural variable name.

            test += "\n\nif __name__ == '__main__':\n    unittest.main()\n"
            tests += "\n\nif __name__ == '__main__':\n    unittest.main()\n"

            # Write a class file ahead of run_tests() call.
            test = test.replace('#<function under test>', code0, 1)  # STAGE 1: single test, code0 has __example__ loop.

            tests = tests.replace('#<function under test>', code, 1)  # STAGE 2 code and tests. ************************

            to_file(class_name + ".py", test)     # Create State 1 Test file
            test_results = run_tests(class_name)  # **** RUN Stage 1 TEST ****
            if len(test_results.errors) == 0 and len(test_results.failures) == 0:
                db.commit()
                print(function_count, "functions generated")
                print("Passed Stage 1 test - no errors or failures. Database changes committed.")
                to_file(class_name + ".tmp", test)  # Backup TestX.py to TestX.tmp, in effect.
                # Write a Stage 2 TestX.py that's without the for __example__ loop but includes multiple unit tests.
                to_file(class_name + ".py", tests)
                test_results = run_tests(class_name)  # **** RUN Stage 2 TESTS ****
                if len(test_results.errors) == 0 and len(test_results.failures) == 0:
                    print("Stage 2 success")
                    # ************ RETURN ************
                    return code, tests, SUCCESS
                else:
                    print("Unexpected failure in Stage 2")
                    return code, tests, not SUCCESS  # Used by repl.it

            # Failure. Unless it's the very last trial, ROLLBACK TO if_endings_trial.
            if (if_maybes_row != if_maybes[len(if_maybes) - 1]) or for_maybes_row != for_maybes[len(for_maybes) - 1]:
                cursor.execute("SELECT COUNT(*) FROM cbt_temp_last_el_ids")
                print("Before if_endings_trial rollback: ctlei count(*)", cursor.fetchone()[0])
                cursor.execute("ROLLBACK TO if_endings_trial")  # ROLLBACK
                cursor.execute("SELECT COUNT(*) FROM cbt_temp_last_el_ids")
                print("After if_endings_trial rollback: ctlei count(*)", cursor.fetchone()[0])

        # Unless it's the very last trial, ROLLBACK
        if for_maybes_row == for_maybes[len(for_maybes) - 1]:  # Last trial
            db.commit() # To enable analysis.
        else:
            cursor.execute("SELECT COUNT(*) FROM cbt_temp_last_el_ids")
            print("Before for loop rollback: ctlei count(*)", cursor.fetchone()[0])
            cursor.execute("ROLLBACK")  # Undo this failed iteration's experimental for-loop endings.
            cursor.execute("SELECT COUNT(*) FROM cbt_temp_last_el_ids")
            print("After for loop rollback: ctlei count(*)", cursor.fetchone()[0])
    print(function_count, "functions generated, none successful")
    return code, tests, not SUCCESS  # Used by repl.it (N.B. return above as well)


def reverse_trace(file: str) -> str:
    """
    Exemplar's top level function attempts to reverse engineer a function from a "trace".
    Pull input/output/assertion lines from the .exem, work up their implications in database, then generate_code() and
    generate_tests() until all tests pass.
    :database: SELECTs sequential_function. Indirectly, all tables are involved.
    :param file: An .exem filename of trace examples
    :return code: A \n-delimited string
    """
    # global pid, db, cursor

    # Read input .exem
    debug_db()
    reset_db()
    print("\nProcessing", file)
    example_lines = from_file(file)
    store_examples(example_lines)  # Insert the .exem's lines into the database.
    remove_all_c_labels()  # Remove any (currently unused) constant (c) labels.
    if DEBUG:
        print(dump_table("example_lines"))
    fill_conditions_table()  # The table of user assertions aka truth.
    if DEBUG:
        print(dump_table("conditions"))

    # fill_control_block_traces()  # control trace clauses, ie, non-assignment assertions, type for/while/if/elif/else.

    # *************************** FORs *************************
    store_fors()  # Put for-loop info into controls and cbt tables, including all last_el_id_maybe possibilities.

    code, test_file_contents, success = get_function(file)  # Determine for-loop endpoints, etc.

    return code, test_file_contents  # Used by repl.it


sys.path.append(exemplar_path())  # For run_tests(). (imports don't take absolute paths.)
if __name__ == "__main__":
    if len(sys.argv) == 1 or not sys.argv[1].strip() or sys.argv[1].lower()[-5:] != ".exem":
        sys.exit("Usage: exemplar my_examples.exem")

    try:
        reverse_trace(file=sys.argv[1])  # Treat argument as the name of an .exem file.
    except:
        db.commit()  # Preserve database for post-mortem analysis.
        raise
