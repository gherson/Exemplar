import sys
import sqlite3  # See reset_db()
import re
from inspect import currentframe, getframeinfo  # For line #
import importlib  # To import and run the test file we create.
import unittest
from typing import List, Tuple, Dict, Any
import os

DEBUG = True  # Set to True for more feedback.
DEBUG_DB = True  # Set to True to enable table to screen dumps.

"""
reverse_trace(file) reverse engineers a function from the examples in the named .exem `file`.

Version 3, started 1/26/2019, models state and user interaction, and the input file changes from single 
i/o[/reasons] triples per example to an unbounded # of lines of <inputs, >outputs, and assertions per example. 
Version 2 finished 10/20/2018 can also generate a while loop. This version can also handle prime_number.exem. 
'reason's are now an unlimited # of conditions.  
Version 1 finished 3/25/2018 can generate one if/elif/else. This version correctly handles fizz_buzz.exem, guess2.exem, 
and leap_year.exem. These 'reason's are 0 or 1 conditions only.

Glossary:
example == A trace imagining input, output, and assertions as specification of a desired (target) function.
exem == The user's examples collected in a file of extension .exem.
loop top == An example line that represents the re/starting of a loop. The first such top is the loop 'start'.
pretest == A 'reason' that serves as an IF or ELIF condition above other ELIF/s (in a single if/elif/else).
"""


def assertion_triple(truth_line: str) -> tuple:
    """
    List the relations in truth_line in a standard form.
    Ie, each relation should be (left_operand, relational_operator, right_operand).
    A valid identifier not of form i[0-9]+ is placed on the right in equality expressions.
    Double quotes are swapped for single.
    :database: not involved.
    :param truth_line:
    :return: the operands and relational operator in truth_line.
    """
    # assertions = list_conditions(truth_line)
    # for assertion in assertions:
    assertion = truth_line.translate(str.maketrans({'"': "'"}))  # " -> ' for consistency. todo ignore escaped "s
    # Create the relation triple: left_operand, relational_operator, right_operand.
    left_operand, relational_operator, right_operand = '', '', ''
    for char in assertion:
        if char in " \t\r\n":
            continue
        elif char in "=<>!":
            relational_operator += char
        else:
            if relational_operator:  # Then we're up to the right-hand side of relation.
                right_operand += char
            else:
                left_operand += char
    if relational_operator == '==' and left_operand.isidentifier() and not re.match('i[0-9]+', left_operand):
        # Except for i[0-9]+ (input variable) names, put identifier in the equivalence on *right* for consistency.
        temporary = left_operand
        left_operand = right_operand
        right_operand = temporary
    return left_operand, relational_operator, right_operand


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


def clean(examples: List[str]) -> List[str]:
    """
    Remove header and line comments and trim each line.
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
        line = denude(line)  # denude() defined above.

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
    return result


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


# Unused. 2/20/19
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
    # Remove unquoted whitespace.
    for whitespace in ' \n\t\r':
        possibly_shortened = ''
        for i in range(len(condition)):
            if i not in positions_outside_strings(condition, whitespace):
                possibly_shortened += condition[i]
        condition = possibly_shortened  # Latest whitespace character removed.

    triple = assertion_triple(condition)  # Standardize assertion form.
    condition = triple[0] + triple[1] + triple[2]

    # Only reduce to underscore those integers not immediately following a valid Python identifier (via negative
    # lookbehind) AND not immediately before a 'c' or period (via negative lookahead).
    regex = re.compile(r'(?<![A-z_])\d+(?![\.c])')
    underscored = regex.sub(r'_', condition)
    return underscored


if __name__ == '__main__':
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


def insert_line(line_id: int, example_id: int, example_step: int, line: str) -> int:
    """
    Called as examples are processed to insert the given line into the database.
    :database: Tables examples and example_lines are inserted.
    :param line_id: becomes an el_id
    :param example_id: becomes eid
    :param example_step: becomes step_id
    :param line: a line or comma separated value from exem, with only leading < or > removed.
    :return: line_id and example_step incremented by five for each INSERTion.
    """
    if line.startswith('<'):
        line_type = 'in'
    elif line.startswith('>'):
        line_type = 'out'
    else:
        line_type = 'truth'  # True condition

    if example_step == 0:  # New example.
        cursor.execute('''INSERT INTO examples (eid) VALUES (?)''', (example_id,))

    if line_type == 'in' or line_type == 'out':
        line = line[1:]  # Skip less/greater than symbol.
        cursor.execute('''INSERT INTO example_lines (el_id, example_id, step_id, line, line_type) 
                                    VALUES (?,?,?,?,?)''',
                       (line_id, example_id, example_step, remove_c_labels(line), line_type))
    else:
        for assertion in list_conditions(line):
            cursor.execute('''INSERT INTO example_lines (el_id, example_id, step_id, line, line_type) 
                                VALUES (?,?,?,?,?)''',
                           (line_id, example_id, example_step, remove_c_labels(assertion), line_type))
            line_id += 5
            example_step += 5
        line_id -= 5
        example_step -= 5
    # cursor.execute('''SELECT * FROM example_lines''')
    # print("fetchall:", cursor.fetchall())
    return line_id, example_step


def process_examples(examples: List) -> None:
    """
    Go through .exem file to build `examples` and example_lines tables.
    :database: insert_line() inserts into examples and example_lines tables.
    :param examples: all the lines from exem.
    """
    line_id = 5  # += 5 each insert call
    example_id = -1
    example_step = 5  # += 5 each intra-example step
    previous_line = 'B'

    examples = clean(examples)
    for line in examples:

        if previous_line == 'B':  # Then starting on a new example.
            assert line, "This line must be part of an example, not be blank."
            example_step = 5
            example_id += 1
            line_id, example_step = insert_line(line_id, example_id, example_step, line)
            previous_line = 'E'

        elif previous_line == 'E':  # Then current line must continue the example or be blank.
            if not line:
                previous_line = 'B'
            else:
                example_step += 5  # 5 instead of 1 in order to allow INSERT.
                line_id, example_step = insert_line(line_id, example_id, example_step, line)

        else:
            assert False, "previous_line must be B(lank) or E(xample), not " + previous_line

        line_id += 5  # (The increment is higher than 1 in order to allow inserting rows, in build_reason_evals())


# todo also need to mark each condition as indicating the *start* of a loop or iteration, because an iterative condition
# can be repeated due to a loop in an enclosing scope.
# This whole thing may be redundant with the fill_*_table() functions... 3/9/19
def mark_loop_likely() -> None:
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
        if not variable_name_of_i1(relation):
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


def build_reason_evals() -> None:
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
    cursor.execute("SELECT DISTINCT line FROM example_lines WHERE line_type = 'truth' AND loop_likely = 0 AND step_id = 1")
    all_reasons = cursor.fetchall()

    # All step 0 inputs not involved in looping.
    cursor.execute("SELECT DISTINCT line FROM example_lines WHERE line_type = 'in' AND loop_likely = 0 AND step_id = 5")
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

            # Substitute an_inp for i1 in a_reason and exec() to see if true or false. MAGIC
            exec("reason = " + a_reason, {"i1": an_inp}, locals_dict)
            reason_value = locals_dict['reason']

            # Determine and store reason_explains_io, which indicates whether inp is associated with 'reason'
            # in the examples.
            cursor.execute('''SELECT * FROM example_lines reason, example_lines inp WHERE 
                                reason.example_id = inp.example_id and reason.line = ? AND inp.line = ? AND 
                                reason.loop_likely = 0 and inp.loop_likely = 0''', (a_reason, an_inp,))
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
        cursor.execute("SELECT example_id, step_id FROM example_lines WHERE el_id = ? ORDER BY example_id, "
                       "el_id, step_id", (el_id,))  # First, fetch inp's el_id
        row_one = cursor.fetchone()
        el_id += 1
        example_id = row_one[0]
        reason = "i1 == " + inp
        step_id = row_one[1] + 1
        cursor.execute("""INSERT INTO example_lines (el_id, example_id, step_id, line, line_scheme, line_type) VALUES 
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

    # Here we find the safe pretests to a_reason (again, those `reason`s false with all of a_reason's inputs).
    for reason_eid in all_reason_eids:
        reason_eid = reason_eid[0]  # The zeroth is the only element.

        sql = """
            SELECT DISTINCT reason AS potential_pretest FROM reason_evals WHERE 0 =     -- 0x that potential_pretest  
                (SELECT count(*) FROM reason_evals re2 WHERE re2.reason = 
                    potential_pretest AND re2.reason_value = 1                          -- is true 
                    AND re2.inp IN 
                (SELECT e.line FROM example_lines e WHERE e.line_type = 'in' AND        -- with input
                    e.example_id = ? AND e.loop_likely = 0))                            -- of a_reason's example  
              """  # given with a_reason (below).
        # E.g., 'i1 % 5 == 0' is a legal pretest to 'i1 % 3 == 0' (and v.v.) in Fizz_Buzz because example inputs for the
        # latter, such as 3 and 9, are not also evenly divisible by 5. And an input that is, such as 15, is an example
        # input for neither.
        cursor.execute(sql, (reason_eid,))
        pretests = cursor.fetchall()  # E.g., ('i1 % 3 == 0 and i1 % 5 == 0',)
        for pre in pretests:  # Store each.
            pre = pre[0]                                # (pretest, condition)
            cursor.execute("""INSERT INTO pretests VALUES (?,?)""", (pre, reason_eid))  # All columns TEXT


def reset_db() -> None:
    """
    Clear out the database. (A database is used for the advantages of SQL, not for multi-session persistence.)
    :database: CREATEs all tables.
    :return: None
    """
    db = sqlite3.connect(':memory:')
    global cursor  # So db is available to all functions.
    cursor = db.cursor()

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
    cursor.execute("""DROP TABLE IF EXISTS iterations""")
    cursor.execute("""CREATE TABLE iterations (
                        python TEXT NOT NULL,
                        target_line INTEGER NOT NULL,
                        last_line INTEGER NOT NULL)""")
    cursor.execute("""CREATE UNIQUE INDEX ipt ON iterations(python, target_line)""")

    # selections (1:1 with suspected IFs) with columns python (eg, 'if i<5'), target_line to place that code within
    # the sequential program, an elif column to point to the selection_id of the next IF in the structure (if any).
    # For records housing the last IF in a selection structure, two more columns may be non-null: an else_line column
    # (holding, eg, 55, for line 55) to place an else in the sequential program, and last_line (required), to note where
    # the selection's block ends.
    cursor.execute("""DROP TABLE IF EXISTS selections""")
    cursor.execute("""CREATE TABLE selections (
                        python TEXT NOT NULL,
                        target_line INTEGER NOT NULL,
                        elif ROWID,
                        else_line INTEGER,
                        last_line INTEGER)""")
    cursor.execute("""CREATE UNIQUE INDEX spt ON selections(python, target_line)""")

    cursor.execute("""DROP TABLE IF EXISTS sequential_function""")
    cursor.execute("""CREATE TABLE sequential_function (
                        line_id INTEGER NOT NULL,
                        line TEXT NOT NULL)""")

    # In addition to tying control structures to the generated code, E has to know how these relate to the
    # example lines. There can be many example lines, even within a single example, pointing to the same
    # control structure.  So, to relate example line conditions to control structures many-to-one (and possibly many-
    # to-many), two associative tables are needed. iterations_conditions and selections_conditions have two columns:
    # condition_id and iteration_id or selection_id, respectively.
    cursor.execute("""DROP TABLE IF EXISTS iterations_conditions""")
    cursor.execute("""CREATE TABLE iterations_conditions (
                        condition_id ROWID NOT NULL, -- From the examples
                        iteration_id ROWID NOT NULL)""")  # From E's imagination
    cursor.execute("""CREATE UNIQUE INDEX icci ON iterations_conditions(condition_id, iteration_id)""")

    cursor.execute("""DROP TABLE IF EXISTS selections_conditions""")
    cursor.execute("""CREATE TABLE selections_conditions (
                        condition_id ROWID NOT NULL, -- From the examples
                        selection_id ROWID NOT NULL)""")  # From E's imagination
    cursor.execute("""CREATE UNIQUE INDEX sccs ON selections_conditions(condition_id, selection_id)""")

    cursor.execute("""DROP TABLE IF EXISTS loops""")  # 1-to-1 with code loops (for's and while's).
    cursor.execute("""CREATE TABLE loops (
                        control_id ROWID NOT NULL,
                        python TEXT NOT NULL)""")
    cursor.execute("""CREATE UNIQUE INDEX lc ON loops(control_id)""")

    # To predict where a loop ends, build a table of loop iteration patterns, then search it for the best match (matches?).
    # POssible problem: pattern can change based on interpretation of the exem.
    cursor.execute("""DROP TABLE IF EXISTS loop_patterns""")  # 1-to-1 with each iteration in the exem.
    cursor.execute("""CREATE TABLE loop_patterns (
                        control_id ROWID NOT NULL, 
                        ct_id ROWID NOT NULL,
                        iteration INTEGER NOT NULL,
                        pattern TEXT NOT NULL,   
                            FOREIGN KEY (control_id) REFERENCES loops(control_id),
                            FOREIGN KEY (ct_id) REFERENCES control_traces(ct_id))""")
    cursor.execute("""CREATE UNIQUE INDEX lpci ON loop_patterns(ct_id, iteration)""")

    # 1 row for each clause of a re/started code control. (Each time an outer loop starts an inner counts as a start.)
    # 1-to-many with conditions table, because latter has a record of all loop iterations, not just the first and last.
    # many-to-1 with code controls (control_traces.control_id values are 1-to-1 with code controls).
    cursor.execute('''DROP TABLE IF EXISTS control_traces''')  # conditions table has the non-terminal el_ids.
    cursor.execute('''CREATE TABLE control_traces (
                        ct_id ROWID NOT NULL,
                        python TEXT NOT NULL, -- MOVE TO LOOPS 
                        indents INTEGER NOT NULL DEFAULT 1, -- # of indents to place before the code in field 'python'.
                        first_el_id INTEGER NOT NULL,
                        last_el_id_sorta INTEGER, -- hypothesized last_el_id
                        last_el_id_1st_possible INTEGER, -- 1st possible last line of the control trace. 
                        last_el_id INTEGER, -- Actual last line of the control trace. (>=1 of these 3 is always set.)
                        last_el_id_last_possible INTEGER, -- Last possible last line of the control trace. (Duplicated across IF clauses.)
                        control_id TEXT NOT NULL)''')  # if#/for#/while#
    cursor.execute('''CREATE UNIQUE INDEX cpf ON control_traces(python, first_el_id)''')

    # 1 row for each example_line of line_type 'truth'
    cursor.execute("""DROP TABLE IF EXISTS conditions""")
    cursor.execute("""CREATE TABLE conditions ( -- 1 row for each comma-delimited condition from the 'truth' lines. 
                        el_id INTEGER NOT NULL,
                        example_id INTEGER NOT NULL,
                        condition TEXT NOT NULL,
                        scheme TEXT NOT NULL, 
                        left_side TEXT NOT NULL,
                        relop TEXT NOT NULL,
                        right_side TEXT NOT NULL,
                        loop_likely INTEGER,
                        control_id INTEGER,
                        condition_type TEXT)""")  # assign/if/for/while
                        #-- python TEXT)
                        #-- schematized(condition)
                        # --type TEXT NOT NULL, -- 'simple assignment', 'iterative', or 'selective'
                        # --intraexample_repetition INTEGER NOT NULL DEFAULT 0
    # lp todo For these repetitions, how many can be considered to be followed with the same # of code
    # lines of exactly 1 further indent? 2/10/19
    # satisfies INTEGER NOT NULL DEFAULT 0, -- Python code satisfies all examples?
    # approved INTEGER NOT NULL DEFAULT 0)""")  # Python code is user confirmed?
    cursor.execute("""CREATE UNIQUE INDEX ce ON conditions(el_id)""") #, condition)""")  WHY condition?

    cursor.execute('''DROP TABLE IF EXISTS example_lines''')
    cursor.execute('''CREATE TABLE example_lines (
                        el_id INTEGER NOT NULL, -- explicitly assigned a line number
                        example_id INTEGER NOT NULL, -- example #
                        step_id INTEGER NOT NULL, -- relative line # within the example
                        line TEXT NOT NULL,
                        loop_likely INTEGER NOT NULL DEFAULT -1, -- see mark_loop_likely()
                        line_type TEXT NOT NULL)''')  # in/out/truth
    cursor.execute('''CREATE UNIQUE INDEX eles ON example_lines(example_id, step_id)''')

    # One record per user example.
    cursor.execute('''DROP TABLE IF EXISTS examples''')
    cursor.execute('''CREATE TABLE examples (
                        eid ROWID)''')

    # # of `reason`s * # of inputs == # of records. To show how every `reason` evaluates across every example input.
    # For if/elif/else generation.
    cursor.execute('''DROP TABLE IF EXISTS reason_evals''')
    cursor.execute('''CREATE TABLE reason_evals(
                        inp TEXT NOT NULL, 
                        reason TEXT NOT NULL, 
                        reason_explains_io INTEGER NOT NULL, -- 1 iff this inp has this reason in examples (unused)  
                        reason_value INTEGER NOT NULL)''')
    cursor.execute('''CREATE UNIQUE INDEX reir ON reason_evals(inp, reason)''')

    # # of 'reason's * (# of 'reason's - 1) == # of records.  To show
    # for every `reason`, those (single condition) reasons that can be listed above it in an elif.
    cursor.execute('''DROP TABLE IF EXISTS pretests''')
    cursor.execute('''CREATE TABLE pretests(
                        pretest TEXT NOT NULL, 
                        condition TEXT NOT NULL)''')
    cursor.execute('''CREATE UNIQUE INDEX ppc ON pretests(pretest, condition)''')


# Unused but may be better than the simpler approach in assertion_triple(). 2/20/19
def find_rel_op(condition: str) -> Tuple:
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


# Unused because predates move to new </>/assertion format. 2/20/19
def same_step(loop_step: str, condition: str) -> int:
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
    """
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


# Unused because predates move to new </>/assertion format. 2/20/19
def get_inc_int_pos(condition: str) -> Tuple[int, int]:
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
def get_increment(condition: str) -> int:
    """
    Find and return the inc/dec-rement in the given condition.
    E.g., 'i1 % (i1-1) != 0c' --> -1
    :database: not involved.
    :param condition: str
    :return signed increment, 0 if none found:
    """
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


# Unused because predates move to new </>/assertion format. 2/20/19
def define_loop() -> Tuple[List, List]:
    """
    Decipher the loop by noting its sequence of example lines. Define and return loop_steps, loop_step_increments and
    update the ??termination table.
    # todo figure out what to do about steps not given, e.g., (i1-1)>2c, if printing step errors isn't enough.
    :database: SELECTs example_lines. UPDATEs termination.
    :param None
    :return loop_steps, loop_step_increments:
    """
    loop_width = 0
    first_condition = ""
    loop_steps = []  # Are here built.
    loop_step_increments = []  # The change to the loop control variable from the prior iteration
    ## before each condition's relational operator (includes *all* reasons (perhaps uselessly)).

    cursor.execute("""SELECT * FROM example_lines ORDER BY example_id, el_id""")
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


def quote_if_str(incoming: str) -> str:
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


if __name__ == "__main__":
    assert ('10', '==', 'guess') == assertion_triple("guess==10"), "We instead got " + str(assertion_triple("guess==10"))
    assert ('10', '>', '4') == assertion_triple("10>4"), "We instead got " + str(assertion_triple("10>4"))
    assert ('1', '==', 'guess_count') == assertion_triple("guess_count==1"), \
        "We instead got " + str(assertion_triple("guess_count==1"))


# Unused after switching back to i1-style references.
def variable_name_of_value(truth_line: str, value: any) -> str:
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


def variable_name_of_i1(truth_line: str, input_variable: str = 'i[0-9]+') -> str:
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


if __name__ == "__main__":
    assert 'guess' == variable_name_of_i1('guess==i1')
    assert '' == variable_name_of_i1('     guess==1')
    assert 'guess' == variable_name_of_i1('guess==i1', 'i1')
    assert '' == variable_name_of_i1('   guess == i1', 'i5')
    assert 'guess' == variable_name_of_i1('guess==i5', 'i5')
    assert 'guess' == variable_name_of_i1('guess==i5')


def store_code(code):
    code_lines, line_id = [], 0
    for line in code.split('\n'):
        code_lines.append((line_id, line))
        line_id += 5
    cursor.executemany("INSERT INTO sequential_function (line_id, line) VALUES (?, ?)", code_lines)


def get_range(first_el_id: int, line: str) -> Tuple[Tuple[int, int], int]:
    """
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
        # Below check commented out because it fails with inner loops and the check is done better anyway in fill_control_traces(). 3/3/19
        # else:
        #     if row_int - last_value != increment:
        #         exit("Line " + condition + "'s expected increment " + str(increment) + " was instead " + str(row_int - last_value))
        last_value = row_int
        last_el_id_top = row_el_id  # '_top' because we are looking only at example_lines matching given scheme.

    # Armed with the line id of the last top of the likely loop, determine the loop's pattern and loop bottom.
    loop_pattern, last_el_id = get_last_el_id_of_loop(first_el_id, last_el_id_top)
    # todo Use info to end loop block's indent etc in controlled_code.

    return (first_value, last_value + increment), last_el_id, loop_pattern  # Old: Eg, (0, 2 + 1), 115, 'toitto, toittt'


def if_or_while(el_id: int, condition: str, second_pass: int) -> str:
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
        IF clauses (alone) are open to re-ordering, and switching between if/elif/else.  As with for loops, the 
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


def get_last_el_id_of_loop(first_el_id: int, last_el_id_top: int) -> Tuple[str, int]:
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


def likely_data_type(variable_name: str) -> str:
    """
    Determine variable_name's data type by the example inputs noted in the sequential_function, which stores lines like
    "secret = input('secret:')  # Eg, 3".  The '3' is what would be used here.
    Preference is given to int, then float, then string (as string is the most lax).
    :database: SELECTs sequential_function. UPDATEs sequential_function.
    :param variable_name:
    :return: data_type
    """
    # Eg,             SELECT line FROM sequential_function WHERE line LIKE '% secret = %'
    cursor.execute("""SELECT line FROM sequential_function WHERE line LIKE '% ' || ? || ' = %'""", (variable_name,))
    rows = cursor.fetchall()
    assert len(rows) > 0, "Table sequential_function is unexpectedly empty."
    data_type = 'int'
    for row in rows:  # Example row[1]:     guess = input('guess:')  # Eg, 10
        line = row[0]
        start = line.index("  # Eg, ") + len("  # Eg, ")
        value = line[start:]
        if not value.isnumeric():
            data_type = 'str'
            break
        elif not value.isdigit():
            data_type = float

    # Wrap sequential_function's input()'s with the determined (non-string) data_type.
    if data_type != 'str':
        cursor.execute("""UPDATE sequential_function SET line = REPLACE(line,   ')  # Eg, ',   '))  # Eg, ') 
        WHERE line LIKE '% ' || ? || ' = input(%'""", (variable_name,))  # Double right parentheses needed after:
        cursor.execute("""UPDATE sequential_function SET line = REPLACE(line,   ' = input(',   ' = ' || ? || '(input(') 
        WHERE line LIKE '% ' || ? || ' = input(%'""", (data_type, variable_name))
    return data_type


def replace_hard_code(prior_values: Dict[str, Any], line: str) -> str:
    """
    Replace any word in 'line' that matches a prior input value with that value's variable name.
    :database: not involved.
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
        match = re.search(r'\b' + prior_values[variable_name] + r'\b', line)
        if match:  # position > -1:
            new_line = line[0:match.start()] + "' + str(" + variable_name + ')'  # It is good to meet you, ' + v0

            # Add remainder of line, if any.
            remainder_of_line = line[match.start() + len(match.group(0)):]
            if remainder_of_line:
                new_line += " + '" + remainder_of_line
            line = new_line
    return line


def generate_code() -> List[str]:
    """
    Use the tables to generate exem-conforming Python code -- a sequential version w/o control structures on 1st call
    then a version with if/elif/else and for/while control.
    :database: SELECTs sequential_function, example_lines. UPDATEs conditions, sequential_function (indirectly).
    :return: Python code as 'code'
    """

    code, code_stripped = [], []  # 'code' is to be returned
    prior_input, preceding_equality, indent, loop_start = {}, {}, "    ", -1
    # On 1st call, a version of the target function w/o control structures is saved to this table:
    cursor.execute("SELECT COUNT(*) FROM sequential_function")
    second_call = cursor.fetchone()[0]  # If this is our 1st call, second_call will be "false"

    # Loop over every example_line.
    sql = """SELECT el.el_id, el.line, el.line_type, el.loop_likely, c.condition_type, c.control_id 
    FROM example_lines el LEFT JOIN conditions c ON el.el_id = c.el_id ORDER BY el.el_id"""
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0:
        print("*Zero* example lines found.")

    # todo Distinguish arguments from variable assignments and input() statements...
    for_suspects = []
    i = 0  # example_lines line counter
    for row in rows:
        el_id, line, line_type, loop_likely, condition_type, control_id = row

        # Code an input (datum unspecified except in the tests and comments).
        if line_type == 'in':

            if line.strip() == '':  # In line, *no* example input was provided.
                code.append(indent + "input()")
                code_stripped.append("input()")
                continue

            line = line.translate(str.maketrans({"'": r"\'"}))  # Escape single quotes in the exem input lines.

            # Create a default name for the variable, then look for a better one.
            variable_name = "v" + str(el_id)
            if i+1 < len(rows):
                next_row = rows[i+1]  # el_id, line, line_type
                # If the next row is truth and has an equality "naming" 'line's value, make that name the variable name.
                if next_row[2] == 'truth' and \
                        variable_name_of_i1(next_row[1], 'i1'):  # Eg, name_of_input('guess==i1')
                    variable_name = variable_name_of_i1(next_row[1], 'i1')  # Eg, 'guess'

            # Non-string inputs need a cast.
            if second_call and likely_data_type(variable_name) != "str":
                cast = likely_data_type(variable_name)  # Updates sequential_function after looking at its 'Eg's.
                assignment = variable_name + " = " + cast + "(input('" + variable_name + ":'))"
                # cursor.execute("UPDATE sequential_function SET line = ? WHERE el_id = ?", (assignment, el_id))
            else:  # Casting is added later for the first call, via the database.
                assignment = variable_name + " = input('" + variable_name + ":')"

            # If it's new, add the input() assignment to the code (with the example datum behind "# Eg, ").
            if not second_call or assignment not in code_stripped[loop_start:]:
                assignment = indent + assignment + "  # Eg, " + line
                code.append(assignment)
                code_stripped.append(denude(assignment))
            prior_input[variable_name] = line  # Eg, prior_input['name'] = 'Albert'

        elif line_type == 'out':  # This line models a print()
            # todo Distinguish return from print()'s...
            line = line.translate(str.maketrans({"'": r"\'"}))  # Escape ' (should this simply be done for all lines??)

            # Replace anything in 'line' that matches a prior value with that value's variable.
            prior_values = prior_input  # Combine prior_input and
            prior_values.update(preceding_equality)  # the preceding_equality.
            line = replace_hard_code(prior_values, line)

            print_line = "print('" + line + "')"
            # Add the print() to the code, if it's new or we're creating the STF.
            if not second_call or print_line not in code_stripped[loop_start:]:
                code.append(indent + print_line)
                code_stripped.append(denude(print_line))

        else:  # truth/assertions/reasons/conditions

            # Grab control info.
            if control_id:
                cursor.execute("""SELECT ct.python, ct.first_el_id, ct.last_el_id, ct.last_el_id_sorta 
                FROM control_traces ct WHERE ct.control_id=?""", (control_id,))
                row = cursor.fetchone()
                """
                control_traces has the python code and first_el_id of each control. 
                Use the python code when el_id == first_el_id.
                """
                python, first_el_id, last_el_id, last_el_id_sorta = row
                print("el_id, python, first_el_id:", el_id, python, first_el_id)

            left, operator, right = assertion_triple(line)  # Break up 'line' into its 3 parts.

            # Lines that equate a digit to a (non-input) variable are noted for
            # substitution in print()s and, if their scheme repeats, as for_suspects.
            # ((Below condition is spelled out because it differs from the loop_likely classes'. 2/17/19))
            # Eg,           3                  ==                                                 guess_count
            if left.isdigit() and operator == '==' and not re.match(r'i\d', right) and re.match('[A-z]', right):

                # Storing, eg, preceding_equality['guess_count'] = 3 allows swapping guess_count for 3 in a later print.
                # guess_count==*3* + "You guessed in *3* guesses!" => "You guessed in " + guess_count + " guesses!".
                preceding_equality[right] = left  # preceding_equality['guess_count'] = 3

                if right.isidentifier():  # Rule out un-assignable left hand sides like 'guess_count + 1'
                    # A non-input identifier rhythmically asserted equal to an integer implies a **** FOR loop ****
                    # (And assertions showing a non-input variable growing without explanation is proof of a FOR loop.)

                    if not second_call:  # then force the assertion's truth with an assignment:
                        code.append(indent + str(line).replace('==', '=', 1))  # Eg, guess_count = 2
                        code_stripped.append(denude(str(line).replace('==', '=', 1)))
                        code.append(indent + "assert " + str(line))
                        code_stripped.append(denude("assert " + str(line)))
                    if scheme(line) not in for_suspects:  # scheme(line) is new. todo Search with indent + line
                        range_pair, last_el_id_of_loop, loop_pattern = get_range(el_id, line)
                        if len(loop_pattern) > 1:  # The scheme repeats w/in an example.
                            control = indent + "for " + right + " in range" + str(range_pair) + ':'
                            if second_call:
                                code.append(control)
                                code_stripped.append(denude(control))
                                loop_start = len(code)
                                indent += '    '  # indent is never augmented on first pass.
                            for_suspects.append(scheme(line))  # todo add indent for better discrimination

            # re: below "not", verify it corresponds to an assignment. lp todo
            # elif not an assignment from input, then assume IF or WHILE.
            elif not (operator == '==' and re.match(r'i[\d]$', left) and re.match(r'[A-z]', right)):
                control = if_or_while(el_id, line, second_call)  # ********* IF OR WHILE ********
                while_or_if = control.partition(' ')[0]
                if second_call:
                    if 'if' in while_or_if or 'while' in while_or_if:
                        pass
                    elif 'elif' in while_or_if or 'else:' in while_or_if:
                        indent = indent[0:-4]  # Out-dent
                    else:
                        assert False, "Control statement " + control + " starts with an unexpected word."
                    # Append control to code if it's not in loop.
                    if control not in code_stripped[loop_start:] and \
                            (indent + control[2:]) not in code_stripped[loop_start:]:  # ignoring possible "el" start.
                        code.append(indent + control)
                        code_stripped.append(denude(control))
                    indent += '    '  # indent is augmented only on pass 2.
                    control = ''
                if control:
                    code.append(indent + "assert " + str(line) + "  #" + control)  # Tuck control into a comment.
                    code_stripped.append(denude("assert " + str(line)))

        i += 1  # example_lines line counter

    return code  # Below will be selectively re-activated as more example problems are handled.

    # Next, we gen code from the ************** IF/ELIF/ELSE ************** conditions, in that order.
    # (old: Reasons where loop_likely==0 map to conditions 1:1.)

    sql = """
        SELECT line, example_id, step_id AS r1 FROM example_lines WHERE line_type = 'truth' AND loop_likely = 0
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
        SELECT line AS r1 FROM example_lines WHERE line_type = 'truth' AND loop_likely = 1 ORDER BY step_id DESC, 
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
    cursor.execute('''SELECT final_cond, output, loop_step FROM termination WHERE loop_likely = 1 ORDER BY step_num''')
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
def get_output(reason_eid: int, step_id: int) -> str:
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
    fetchone = cursor.fetchone()
    if fetchone is None:
        cursor.execute("""SELECT step_id FROM example_lines WHERE line_type = 'out' AND example_id = ?  AND 
                        loop_likely = 0 ORDER BY step_id""", (reason_eid,))
        print("With example_id "+str(reason_eid)+" and step_id "+str(step_id)+
              ", this query returned zero rows:\n"+query)
        step_ids = ''
        for row in cursor.fetchall():
            step_ids += str(row[0]) + ', '
        sys.exit("The step_id's matching those criteria are " + step_ids)
    return fetchone[0]


def dump_table(table: str) -> str:
    """
    When global variable DEBUG_DB is True this prints, eg,
    [all example_lines:
    (el_id, example_id, step_id, line, loop_likely, line_type)
    (0, 0, 0, Hello! What is your name?, -1, out),
    (5, 0, 5, Albert, -1, in),
    (10, 0, 10, name==i1, -1, truth), ...
    :database: SELECTs given table.
    :return void:
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


def inputs(example_id: int) -> List:
    """
    Return all inputs (that came from the exem) for the given example. (This is useful for testing.)
    :database: SELECT example_lines.
    :param example_id:
    :return:
    """
    cursor.execute("""SELECT line FROM example_lines WHERE example_id=? AND line_type='in' ORDER BY el_id""",
                   (example_id,))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(row[0])
    return result


def generate_tests(function_name: str) -> str:
    """
    Generate unit tests using the .exem's examples (specifically, their i/o).
    :database: SELECT examples.
    :param function_name: used for test function name and calling the function under test.
    """
    # # For each example, ??
    # cursor.execute('''SELECT inp.line, output.line, inp.example_id FROM example_lines inp, example_lines output
    #                     WHERE inp.example_id = output.example_id AND inp.line_type = 'in' AND output.line_type = 'out'
    #                     AND (inp.step_id = 5 OR output.step_id = 5) ORDER BY inp.example_id, output.step_id DESC''')
    # # The above DESC and the 'continue' below implement MAX(output.step_id) per example_id.

    cursor.execute("SELECT eid FROM examples ORDER BY eid")
    all_examples = cursor.fetchall()
    test_code = ""
    i = 1  # For appending to the test name.
    # previous_example_id = -1
    for row in all_examples:
        # inp, output, example_id = row
        # Create one test per example.
        # if example_id == previous_example_id:
        #     previous_example_id = example_id
        #     continue
        test_code += "\ndef test_" + function_name + str(i) + "(self):\n"
        # code += "    i1 = " + inp + "\n"  # (i1 may be referenced by output as well.)
        # code += "    self.assertEqual(" + output + ", " + f_name + "(i1))\n\n"
        test_code += "    global in_trace\n"
        test_code += "    in_trace = ['" + "', '".join(inputs(row[0])) + "']  # From an example of the .exem\n"  # Eg, ['Albert','4','10','2','4']
        test_code += "    " + function_name + "()  # The function under test is used to write to out_trace.\n"  # TODO need formal params!!
        #                                       Return the named .exem (stripped of comments):
        if len(function_name) > 4 and function_name[-4:] == '_stf':  # Remove "_stf" when naming the .exem file.
            test_code += "    self.assertEqual(self.get_expected('" + function_name[0:-4] + ".exem'), out_trace)\n"
        else:
            test_code += "    self.assertEqual(self.get_expected('" + function_name + ".exem'), out_trace)\n"

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


if __name__ == "__main__":
    assert 'TestPrimeNumber' == underscore_to_camelcase('test_prime_number')
    assert 'Get_ThisValue' == underscore_to_camelcase('get__this_value'), underscore_to_camelcase('get__this_value')
    assert '_Get_ThisValue' == underscore_to_camelcase('_get__this_value'), underscore_to_camelcase('_get__this_value')
    assert '_Get_ThisValue_' == underscore_to_camelcase('_get__this_value_'), underscore_to_camelcase('_get__this_value')
    assert 'GetThisValue' == underscore_to_camelcase('get_this_value'), underscore_to_camelcase('get_this_value')
    assert 'Get_This_Value' == underscore_to_camelcase('get__this__value'), underscore_to_camelcase('get__this__value')


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
    Use the examples and Python's type() to create a formal parameters declaration.
    Each example should have the same # of arguments and they occur before any output, in the same order.
    These facts are used here to determine the data type each argument correlates to, in the examples.
    :database: SELECTs example_lines.
    :return: formal parameters declaration, eg, i1: str, i2: int
    """
    result = ''
    # Ordering by example_id to glean arguments one example at a time.
    # Ordering by step_id within examples to determine argument order.
    sql = "SELECT example_id, line, line_type FROM example_lines ORDER BY example_id, step_id"
    cursor.execute(sql)
    rows = cursor.fetchall()
    previous_example_id = ''
    arguments = {}  # Associates a counter with a data type.
    argument_index = 0
    arguments_count = sys.maxsize  # Total # of args, minus 1.
    goto_next_example = False
    i = 0
    for row in rows:
        example_id, line, line_type = row

        if i > 0 and example_id != previous_example_id:  # Then up to a new example in the rows.
            argument_index -= 1  # Correct a +1 overshoot.
            if arguments_count == sys.maxsize:  # Hasn't been set,
                arguments_count = argument_index  # until now.
            elif arguments_count != argument_index:  # Each example should have the same # of arguments.
                sys.exit("In example " + str(example_id) + ', ' + str(arguments_count+1) + " arguments expected, " +
                         str(argument_index+1) + " arguments found.")
            argument_index = 0  # We've returned to the first input argument (if it exists).
            goto_next_example = False  # Reset this because we've arrived at the next example.

        if line_type == 'out':  # Then we're past any possible arguments for the current example.
            if arguments_count == sys.maxsize:
                arguments_count = -1  # There are no arguments.
            elif argument_index < arguments_count < sys.maxsize:  # Then we didn't see enough arguments.
                sys.exit("Last " + str(arguments_count - argument_index) + " arguments are missing (of " +
                         str(arguments_count) + ") in example " + str(example_id))
            goto_next_example = True  # Because we're past any possible arguments in this example.

        if line_type == 'in' and not goto_next_example:  # Then row refers to an argument.
            # # ast module isn't needed.  data_type = type(ast.literal_eval(line))  # Determine its data type.

            # Determine line's data type. (SQLite v Python: NULL==None, REAL==float, TEXT==str, BLOB==bytes)
            data_type = type(line)

            if arguments_count == sys.maxsize:  # Then we're still counting.
                arguments[argument_index] = data_type
                argument_index += 1
            elif arguments_count < sys.maxsize and argument_index not in arguments:
                sys.exit("Too many arguments in example " + str(example_id) + " (Line content: " + line + ')')
            elif data_type is not arguments[argument_index]:
                if data_type is str:
                    print("arguments[" + argument_index + "] was thought to be of type " +
                          arguments[argument_index] + " but is now TEXT to allow value '" + line + "'")
                    arguments[argument_index] = str
                elif data_type is float and arguments[argument_index] is int:
                    print("Example " + str(example_id) + " has argument " + line + " where a value of type INT was expected."
                        + " The argument's data type is now FLOAT to accommodate it.")
                    arguments[argument_index] = float
                else:
                    sys.exit("Example " + str(example_id) + " has argument " + line + " where a value of type " +
                             arguments[argument_index] + " was expected.")

        # Set up for next row.
        previous_example_id = example_id
        i += 1

    for i in arguments:
        result += 'i' + i+1 + ": " + arguments[i+1] + ", "  # Creating formal param list. Eg, i1: str, i2: int,
    return result.rstrip(", ")


def most_repeats_in_an_example(assertion=None, assertion_scheme=None):
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
    :database: SELECTs example_lines. INSERTs conditions.
    :return:
    """
    # Step 1: Dump example_lines into conditions table.
    all_conditions = []
    cursor.execute("SELECT el_id, example_id, line FROM example_lines WHERE line_type = 'truth'")
    example_lines = cursor.fetchall()

    for example_line in example_lines:
        el_id, example_id, condition = example_line
        left, operator, right = assertion_triple(condition)  # Format
        condition = left + ' ' + operator + ' ' + right      # condition.

        all_conditions.append((el_id, example_id, condition, scheme(condition), left, operator, right))

    cursor.executemany("""INSERT INTO conditions (el_id, example_id, condition, scheme, left_side, relop, 
    right_side) VALUES (?,?,?,?,?,?,?)""", all_conditions)

    # Step 2: Fill in condition.condition_type. (This is a separate step so that the below most_repeats_in_an_example()
    # call can work: it selects from the conditions table.)
    cursor.execute("SELECT el_id, example_id, condition FROM conditions")
    rows = cursor.fetchall()

    for row in rows:
        el_id, example_id, condition = row
        left, operator, right = assertion_triple(condition)  # Format

        condition_type = ''  # We now attempt to fill this in.
        # Lines that equate a digit to a (non-input) variable are noted, if their scheme repeats intra-example, as
        # **** FOR_SUSPECTS ****
        # ((Below condition is spelled out because it differs from the loop_likely classes'. Except for .isidentifier(),
        # below condition is re-used in generate_code(). 3/4/19))
        # Eg,          3                   == guess_count
        if left.isdigit() and operator == '==' and not re.match(r'i\d', right) and re.match('[A-z]', right) and \
                right.isidentifier() and most_repeats_in_an_example(assertion_scheme=condition)[0] > 1:

            # A non-input variable rhythmically asserted (alone) equal to an integer implies a ****** FOR loop ******
            # (And assertions showing a non-input variable growing without explanation is proof of a FOR loop.)
            # if scheme(condition) not in for_suspects:  # scheme(line) is new. todo Search with indent + line
                # get_range() doesn't know scopes, because they take alot of info to guess the ends of, so I had to comment
                # this out. 3/4/19
                # range_pair, last_el_id_of_loop, loop_pattern = get_range(el_id, condition)
                # if len(loop_pattern) > 1:  # The scheme repeats.
            # for_suspects.append(scheme(condition))  # todo add indent for better discrimination
            # Ideally, a scheme repetition only counts in the scope of a putative control structure but to start with
            # we're going with example scope (with the above most_repeats_in_an_example() call). 3/9/19
            condition_type = "for"

        # A condition like 'i1 == count' or '3 == count + 1' indicates a simple assignment.
        elif operator == "==" and (re.match(r'i[\d]$', left) or not right.isidentifier()):  # ***** ASSIGN *****
            condition_type = "assign"

        # elif 'condition', in addition to all the other things it's not, is also not an assignment from input,
        # then assume it's an IF or WHILE.
        elif not (operator == '==' and re.match(r'i[\d]$', left) and re.match(r'[A-z]', right)):  # Eg, not 'i1 == a'
            control = if_or_while(el_id, condition, second_pass=0)  # ********* IF OR WHILE ********
            condition_type = control.partition(' ')[0]  # 1st word of 'control'

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
        if variable_name_of_i1(condition, 'i1') and intraexample_repetition == 0:
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


def run_tests(filename: str) -> str:
    """
    Run the unittest tests of the named file and print and return the results.
    :database: not involved.
    :param filename:
    :return: results of the tests
    """
    class_name = "Test" + underscore_to_camelcase(filename[0:-5])  # Eg, prime_number.exem -> TestPrimeNumber
    sys.path.append(exemplar_path())  # imports don't take absolute paths.
    TestClass = importlib.import_module(class_name)
    suite = unittest.TestLoader().loadTestsFromModule(TestClass)
    test_results = unittest.TextTestRunner().run(suite)
    print("There were", len(test_results.errors), "errors and", len(test_results.failures), "failures.")
    return test_results


def insert_for_loop(ct_id: int, python: str, first_el_id: int, el_id: int, control_id: int, assertion_scheme: str) -> int:
    """
    :database: INSERTs control_traces and loops, UPDATEs conditions.
    :param ct_id:
    :param python:
    :param first_el_id:
    :param el_id:
    :param control_id:
    :param assertion_scheme:
    :return:
    """
    # todo This needs to be postponed until have a best guess as to last el_id of the control in question.
    # cursor.execute("UPDATE conditions SET control_id=? WHERE scheme=? AND el_id>=? AND el_id<?",
    #                (control_id, scheme(condition), first_el_id, el_id2))

    cursor.execute("""INSERT OR REPLACE INTO loops VALUES (?,?)""", (control_id, python))

    cursor.execute("UPDATE conditions SET control_id=? WHERE scheme=? AND el_id>=? AND el_id<=?",
                   (control_id, assertion_scheme, first_el_id, el_id))

    cursor.execute("""INSERT INTO control_traces (ct_id, python, first_el_id, control_id) VALUES (?,?,?,?)""",
                   (ct_id, python, first_el_id, control_id))
    return cursor.lastrowid  # The ct_id just created.
    # todo The newly inserted control_traces records still need indents and last_el_id2 set.


def el_id_peek(start_el_id: int, distance: int) -> int:
    """
    el_id_peek(15, 1) means return the closest el_id value to 15 that is >15.
    el_id_peek(15, -2) means return the 2nd closest el_id value to 15 that is <15.
    :database: SELECTs example_lines
    :param start_el_id:
    :param distance: the # of el_id values from the given el_id.
    :return: the el_id value 'distance' ordered records from 'el_id' in table example_lines.
    """
    if distance < 0:
        direction = 'DESC'
        sign = '<'
    else:
        direction = 'ASC'
        sign = '>'
    cursor.execute("SELECT el_id FROM example_lines WHERE el_id " + sign + " ? ORDER BY el_id " + direction + " LIMIT ?",
                   (start_el_id, abs(distance)))
    rows = cursor.fetchall()
    for row in rows:
        el_id = row[0]
    return el_id
    # todo return -1 if no such value or error out?


def load_for_loops() -> None:  # into control_traces, noting scopes.
    """
    We store the loop variable's first and last values, the starting Python line, and a unique id per control structure.
    todo last_el_id2 and indents via another loop.
    todo deal with for-loop false positives (non-loops). Perhaps by updating that condition_type to 'assign' in
    conditions and removing the related control record as soon as last_el_id2's are determined. 3/4/19
    :database: SELECTs conditions. INSERTs control_traces indirectly. UPDATEs control_traces
    :return:
    """
    schemes_seen = []  # To avoid redundant analyses.

    # Scope the FOR loops by creating 1 control record for every time a loop structure is started.
    # First, pull all the assignments to FOR loop variables (id'ed in fill_conditions_table()).
    cursor.execute("SELECT el_id, condition FROM conditions WHERE condition_type='for' ORDER BY el_id")
    rows = cursor.fetchall()
    control_count = {'for': 0}
    for row in rows:
        el_id, condition = row
        assertion_scheme = scheme(condition)
        if assertion_scheme not in schemes_seen:  # (We assume loop variables aren't re-used.)
            # Second, pull all the possible increments to 'condition's FOR loop variable (ie, 'condition's schemes)
            # to note the loop variable's first and last values, the control id, and starting Python line. Also confirm
            # that the loop variable always starts with the same integer and increments by the same amount.
            cursor.execute("SELECT el_id, condition FROM conditions WHERE scheme = ? ORDER BY el_id",
                           (assertion_scheme,))
            rows2 = cursor.fetchall()
            loop_variable, loop_increment = None, None
            iteration = 0
            for row2 in rows2:
                el_id2, condition2 = row2
                left, operator, right = assertion_triple(condition2)  # Eg, 5, ==, guess_count
                left = int(left)
                if not loop_variable:  # Our first iteration
                    loop_variable = right
                    first_value = left
                    first_el_id = el_id2
                elif not loop_increment:  # 2nd iteration
                    loop_increment = left - first_value
                    last_value = left
                elif left != first_value:  # >2nd iteration.
                    assert loop_increment == left - last_value, str(left - last_value) + \
                        " found where FOR loop increment " + str(loop_increment) + " was expected, at assertion: " + condition2
                    last_value = left
                else:  # The loop variable is back to (usually) 0, meaning that an outer loop has restarted this one.
                    # Save the loop info.
                    control_id = 'for' + str(control_count['for'])
                    ct_id = str(control_id) + '_' + str(first_el_id)
                    python = 'for ' + loop_variable + ' in range(' + str(first_value) + ', ' + str(last_value + 1) + ')'
                    new_row_id = insert_for_loop(ct_id, python, first_el_id, el_id2, control_id, assertion_scheme)
                    # The elid in front of el_id2 is the *last possible* last_el_id of the loop just ended (as there can
                    # be lines between the end of an inner loop and the end of an outer loop). Store that info:
                    cursor.execute("UPDATE control_traces SET last_el_id_last_possible = ? WHERE ROWID = ?",
                                   (el_id_peek(el_id2, -1), new_row_id))
                    first_value = left
                    first_el_id = el_id2
                    loop_increment = None
                assert loop_variable == right, right + " found where FOR loop variable " + loop_variable + \
                    " was expected, at assertion: " + condition2
                iteration += 1

            # scheme(condition) exhausted.
            # todo account for possibility that above loop was broken (via break) right after the above
            # insert_for_loop(), making below insert_for_loop() call redundant. 3/8/19
            control_id = 'for' + str(control_count['for'])
            ct_id = str(control_id) + '_' + str(first_el_id)
            # python is eg, 'for guess_count in range(0, 6)'
            python = 'for ' + loop_variable + ' in range(' + str(first_value) + ', ' + str(last_value + 1) + ')'
            new_row_id = insert_for_loop(ct_id, python, first_el_id, el_id2, control_id, assertion_scheme)
            # We know only the *1st possible* last_el_id of the current loop trace: the *one after* the el_id2 with
            # which we exited the above loop. Store that info:
            if loop_variable == '__example__':  # Special case
                cursor.execute("""UPDATE control_traces SET last_el_id = (SELECT MAX(el_id) FROM example_lines) 
                WHERE ROWID = ?""", (new_row_id,))
            else:
                cursor.execute("""UPDATE control_traces SET last_el_id_1st_possible = ? WHERE ROWID = ?""",
                               (el_id_peek(el_id2, 1), new_row_id))
            schemes_seen.append(assertion_scheme)
            control_count['for'] += 1


def fill_control_traces() -> None:  # Note scopes.
    """
    We store the loop variable's first and last values, the starting Python line, and a unique id per control structure.
    todo last_el_id2 and indents via another loop.
    todo deal with for-loop false positives (non-loops). Perhaps by updating that condition_type to 'assign' in
    conditions and removing the related control record as soon as last_el_id2's are determined. 3/4/19
    :database: All indirectly: SELECTs conditions. INSERTs control_traces. UPDATEs conditions, control_traces.
    :return:
    """
    load_for_loops()  # Loops before IFs to allow determination of whether an IF is in a loop.
    load_ifs()


# todo Pick a last_el_id_sorta... 3/17/19
def start_of_open_loop(el_id):
    """
    If the latest for-loop start <= 'el_id' is of a for-loop still open at 'el_id', return that starting el_id.
    :param el_id: The given el_id
    :return: first_el_id or None
    """
    # Determine if the latest for-loop start <= 'el_id' is still open at 'el_id'.
    cursor.execute("SELECT MAX(first_el_id) FROM control_traces WHERE SUBSTR(control_id,0,3)='for' AND first_el_id<=?",
                   (el_id,))
    row = cursor.fetchone()
    if row[0]:  # Then get its details.
        first_el_id = row[0]
        # Determining if that loop is still open at line 'el_id' requires knowing the loop's last line.
        # We usually don't, in which case 'el_id' divides the possibilities. Follow both possibilities with fork().
        cursor.execute("""SELECT last_el_id_sorta, last_el_id_1st_possible, last_el_id, last_el_id_last_possible, 
        ct_id FROM control_traces WHERE SUBSTR(control_id,0,3)='for' AND first_el_id = ?""", (first_el_id,))
        last_el_id_sorta, last_el_id_1st_possible, last_el_id, last_el_id_last_possible, ct_id = cursor.fetchone()
        if last_el_id:  # Certain loop stop line.
            if last_el_id >= el_id:
                return first_el_id
            else:
                return None
        elif last_el_id_sorta:  # Loop stop location already chosen.
            if last_el_id_sorta >= el_id:
                return first_el_id
            else:
                return None
        elif last_el_id_1st_possible and last_el_id_1st_possible >= el_id:
            return first_el_id
        elif last_el_id_last_possible and last_el_id_last_possible < el_id:
            return None
        else:  # We decide on two last_el_id_sorta values, one per fork.
            pid = os.fork()
            if pid == 0:  # child
                print("child")
                last_el_id_sorta = el_id  # Loop's open, and we make it end at 'el_id'.
            else:  # parent
                print("parent")
                last_el_id_sorta = el_id_peek(el_id, -1)  # We'll say that loop ends just before 'el_id'.
            cursor.execute("UPDATE control_traces SET last_el_id_sorta=? WHERE ct_id=?", (last_el_id_sorta, ct_id))
            if pid == 0:
                return first_el_id
            else:
                return None  # Closest prior loop considered closed.


# To first learn what it is i'm trying to do, the IFs become independent IFs rather than nested... 3/9/19
def load_ifs() -> None:  # into control_traces table (to track their scope).
    """
    We iterate through all IFs in 'conditions', attempting to insert into CT table only those that represent unique
    code lines, by excluding those repeated per a loop. Where repeats are found, 'conditions' is updated to note the
    pre-existing control_id.
    :database: SELECTs conditions. INSERTs control_traces. UPDATEs conditions.
    :return:
    """
    # First, pull all conditions adjudicated by fill_conditions_table()) to be IF related.
    cursor.execute("SELECT el_id, condition FROM conditions WHERE condition_type='if' ORDER BY el_id")
    rows = cursor.fetchall()
    control_count = {'if': 0}

    for row in rows:
        el_id, condition = row
        # Before adding to the code load, determine if the 'el_id' IF duplicates one in the closest prior loop,
        # if that loop is indeed open at 'el_id'.
        loop_start = start_of_open_loop(el_id)  # MAX(first_el_id) <= 'el_id'. Or None if that loop's closed.
        if loop_start:  # Then see if there's a match on 'line' anywhere between loop_start and 'el_id'.
            cursor.execute("SELECT control_id FROM conditions WHERE condition=? AND el_id>=? AND el_id<?",
                           (condition, loop_start, el_id))
            row = cursor.fetchone()
        if not loop_start or row[0] is None:  # No match.
            # Prepare for INSERT and UPDATE.
            control_id = 'if' + str(control_count['if'])
            ct_id = control_id + '_' + str(el_id)  # Eg, 'if3_45'
            python = "if " + condition + ':'
            cursor.execute("INSERT INTO control_traces (ct_id, python, first_el_id, control_id) VALUES (?,?,?,?)",
                           (ct_id, python, el_id, control_id))
            # Back in 'conditions', note the control_id just constructed for el_id.
            cursor.execute("UPDATE conditions SET control_id=? WHERE el_id=?", (control_id, el_id))
            control_count['if'] += 1
        elif row[0]:  # Instead of adding to the control_traces table, pull the found IF's control_id from
            # 'conditions' and update'conditions' at later row 'el_id'.
            control_id = row[0]
            cursor.execute("UPDATE conditions SET control_id=? WHERE el_id=?", (control_id, el_id))


"""def fill_loop_patterns_table():

    # Now fill the loop_patterns table using the known example_lines of first to penultimate iterations.
    Should that be 'in', out line, scheme(condition)? or simply the raw example_lines?
    ***Actually, I'm not convinced this is cost effective***  First scope the starts to all control structures. 3/8/19 
    cursor.execute("INSERT INTO loop_patterns VALUES (?,?,?,?)", (control_id, ct_id, iteration, pattern))"""


# todo Doc
def generate_code2():
    code = ''
    indents = 0
    cursor.execute("""SELECT el.el_id, el.example_id, el.step_id, el.line, el.loop_likely, el.line_type, c.control_id 
    FROM example_lines el LEFT JOIN conditions c ON el.el_id = c.el_id ORDER BY el_id""")
    rows = cursor.fetchall()
    for row in rows:
        el_id, example_id, step_id, line, loop_likely, line_type, control_id = row

        if line_type == 'truth':
            # Grab control info if it exists.
            if control_id:
                cursor.execute("""SELECT ct.python, ct.first_el_id, ct.last_el_id, ct.last_el_id_sorta FROM conditions c 
                LEFT JOIN control_traces ct ON c.control_id = ct.control_id WHERE c.el_id=?""", (el_id,))
                row = cursor.fetchone()
                """
                control_traces has the python code and scope of each control. 
                Use the python code when el_id == first_el_id.
                """
                python, first_el_id, last_el_id, last_el_id_sorta = row
                # below needs further qualification, as control_traces are per iteration, not per control....
                if el_id == last_el_id or el_id == last_el_id_sorta:
                    indents -= 1
                if el_id == first_el_id:
                    code += python
                    indents += 1




def reverse_trace(file: str) -> str:
    """
    Reverse engineer a function from given 'file':
    Pull i/o/truth examples from the .exem, work up their implications in database, then generate_code() and
    generate_tests() until tests pass?
    :database: SELECTs sequential_function. Indirectly, all tables are involved.
    :param file: An .exem file of examples
    :return code: A \n delimited string
    """
    #global f  # Just for use
    #f = file  # in debugging.

    # Read input .exem
    print("\nProcessing", file)
    examples = from_file(file)

    reset_db()
    process_examples(examples)  # Insert the .exem's lines into the database.
    remove_all_c_labels()  # Remove any (currently unused) constant (c) labels.
    #print(dump_table("example_lines"))

    fill_conditions_table()  # The table of true conditions aka assertions.
    #print(dump_table("conditions"))

    fill_control_traces()  # control trace clauses, ie, non-assignment assertions, type for/while/if/elif/else.
    if DEBUG_DB:
        print(dump_table("control_traces"))
    # fill_loop_patterns_table()
    # if DEBUG_DB:
    #     print(dump_table("loop_patterns"))

    mark_loop_likely()  # Set the loop_likely column in the example_lines and condition tables.
    if DEBUG_DB:
        print(dump_table("example_lines"))
        print(dump_table("conditions"))
        # Unused, as are the below tables, currently. print(dump_table("termination"))

    # For if/elif/else order, determine how every `reason` evaluates on every input.
    # build_reason_evals()
    # if DEBUG_DB:
    #     print(dump_table("reason_evals"))

    # Gather more info for determining if/elif/else order.
    # find_safe_pretests()
    # if DEBUG_DB:
    #     print(dump_table("pretests"))
    # Once stabilized, put below into a create_test_class() function. 3/1/19

    #                                 **********************
    # Use the info in the database to **** GENERATE STF ****
    # First build the 1D, sequential target function (STF).
    function_name = file[0:-5]  # Remove ".exem" extension.
    signature = "def " + function_name + '(' + formal_params() + "):\n"
    sequential_version = signature + '\n'.join(generate_code())
    store_code(sequential_version)  # (Table sequential_function will be updated by likely_data_type(), called by
    # generate_code() on 2nd pass.)

    # The second call to generate_code() is a first attempt at adding control structure.
    #                                                ***********************
    code = signature + '\n'.join(generate_code())  # **** GENERATE CODE ****
    print("\n" + code + "\n")  # Show off generated function.
    if DEBUG_DB:
        print("After second pass.\n" + dump_table("conditions"))
        print(dump_table("sequential_function"))

    # Create unit tests for the sequential version of the target function.
    starter = "".join(from_file("starter"))  # Contains mocked print() and input functions etc.
    cursor.execute("SELECT line FROM sequential_function ORDER BY line_id")
    rows = cursor.fetchall()
    sequential_version = ''
    for row in rows:
        sequential_version += row[0] + '\n'
    starter = starter.replace('<stf>', sequential_version, 1)

    class_name = "Test" + underscore_to_camelcase(function_name)
    class_signature = "class " + class_name + "(unittest.TestCase):"
    starter = starter.replace('<class signature>', class_signature, 1)

    # *** GENERATE TESTS ***
    # for line in generate_tests(function_name + "_stf").splitlines(True):  # First for the sequential function.
    #     starter += "    " + line  # Indent each line, as each test is part of a class.
    for line in generate_tests(function_name).splitlines(True):
        starter += "    " + line

    starter += "\n\nif __name__ == '__main__':\n    unittest.main()\n"
    # starter += "\n\n''' The source .exem, for reference:\n"
    # for line in examples:
    #     starter += line
    # starter += "'''\n"
    # to_file(class_name + ".py", starter)
    # print("\n" + starter + "\n")

    to_file(class_name + ".py", starter)
    print("Testing STF: ", end='')
    test_results = run_tests(file)  # **** RUN TESTS ****
    if len(test_results.errors) == 0 and len(test_results.errors) == 0:  # The STF works. Proceed to optimization.
        #print("error and failure count is 0")

        # Prep file ahead of next run_tests() call.
        test_file = starter.replace('#<function under test>', code, 1)  # CODE
        to_file(class_name + ".py", test_file)

        optimized = False  # Determine if code is optimized somehow...
        # (Optimized===controls added to function make all assertions matter (altered the function beyond a comment,
        # assertion, or pointless assignment) and all tests pass.)
        while len(test_results.errors) or len(test_results.errors) or not optimized:  # todo Make last a function call
            if not test_file:  # test_file is "true" only on first execution of this line.
                # Find better code.
                code = signature + '\n'.join(generate_code())  # **** GENERATE CODE ****
                print("\n" + code + "\n")  # Show off generated function.
                test_file = starter.replace('#<function under test>', code, 1)  # CODE
                to_file(class_name + ".py", test_file)
                test_file = ''
            print("Running and testing", file + ": ", end='')
            test_results = run_tests(file)  # **** RUN TESTS ****
            optimized = True  # temporary hack

    return code


if __name__ == "__main__":
    if len(sys.argv) == 1 or not sys.argv[1].strip() or sys.argv[1].lower()[-5:] != ".exem":
        sys.exit("Usage: exemplar my_examples.exem")

    reverse_trace(file=sys.argv[1])  # Treat argument as the name of an .exem file holding traces of a desired function.
