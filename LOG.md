# Roadmap
* Enable WHILE loops
* Move from repl.it to an independent website
* Enable modeling of arbitrary function calls:

```
>getDate()   # This syntax is consistent with a function call and so that's how it's interpreted.
<2019-04-25  # Since previous line is a function call, this line is interpreted as its return value.
```    
     
* Enable JSON representation of literals  
* Enable more examples, such as: Python’s split function, a Turing Machine, an algorithm requiring inner loops, finding 
the difference in time between any two given date-time objects, a problem requiring input of three arguments (i1, i2,  
and i3), alphabetizing an input list's elements, examples that include a literal “i1” in the output 
* Replace brute force search for successful Python block endpoint with one guided by machine learning (that finds
 correlations between that goal and database state). 2019-04-23

# Done
* All unit tests created stand alone (no dependency on an .exem file). 2019-11-20 
* Assertion-less user examples (and thus easy additional unit test creation) enabled. 2019-11-20
* If/elif branch order automatically found, by (a separate) generate and test search. 2019-11-04
* Multiple example solving (by treating the examples as iterations of a temporary FOR loop). 2019-09-04
* Single-example solving, supporting IF and FOR loops, with block endpoints found by generate and test. 2019-04-18
* Automatic unit tests (1 test per user example) created and run. 2019-01-29
* The user example format changes from a single input/output/assertions triple to an unbounded # of <input, >output, and 
assertion lines, in order to exemplify, e.g., user interaction and state. 2019-01-26 
* While loop generation (since removed) and unlimited assertions (correctly handling prime_number.exem). 2018-10-20  
* Single if/elif/else generated from simple user examples of 0 or 1 assertions, correctly handling fizz_buzz.exem, 
guess2.exem, and leap_year.exem. 2018-03-25


# Log of work
Next: "Last minute" improvements before creating an official screencast: 
will now add arguments to the generated function if easy

* 2019-11-23: 15:10 - 18:40 + 19:25 - Continued to troubleshoot assertion-less examples failing when in the middle of
 other examples, until resolved. SQL Updates now assert the expected # of updated lines where that was deemed useful.
* 2019-11-22: To get fizz_buzz_variant_return_4.exem working, output substitution now only occurs if tests fail 
without it. E is back to allowing the user to choose example order, because that allows the user some control of 
the order of lines in the generated function. To that end, there is a new "examples" table, to hold el_id_count. 9.5h  
* 2019-11-21: Unified condition formatting, with deflate(). TestExemplar.py confirms all demonstration problems 
remain solved. 7h
* 2019-11-20: Finished changes to generate_test(). E can now accept assertion-less user examples to create unit tests. 
Also, the unit tests generated no longer require their source .exem file at run time. 6.25h 
* 2019-11-19: Committed code. Fixed generate_code() bugs exposed by user example re-ordering, then began changing 
generate_tests() to pull expected i/o from database rather than .exem file. 5.5h  
* 2019-11-18: Troubleshooting the bugs exposed by the re-ordering of the traces (to put longest examples first for 
assertion-less examples). 9.75h   
* 2019-11-17: adjustments to store_if(), still trying to allow assertion-less examples. 5.75hr
* 2019-11-16: Working to allow assertion-less user examples, after work on re-enabling integration testing. 9h  
* 2019-11-15: A few improvements, such as  elif True->else, and fixed a couple of issues with fizz_buzz.exem. 
Asked repl.it for help re: a database error. 6.25h 
* 2019-11-14: Improved repl.it UI and organized notes. 3.5h.
* 2019-11-13: Finished store_fors() overhaul. Got prime_number.exem working. 9.5h 
* 2019-11-12: store_fors() overhaul. 5h
* 2019-11-11: To handle more complex assertions (needed by prime_number.exem), SymPy will today replace current 
assertion normalization, eg, assertion_triple(). Start w/loop increment. 10.5h  
* 2019-11-10: Worked on prime_number.exem until deciding to recruit SymPy's help in determining loop increment
and normalizing (all) assertions. Then browsed SymPy documentation and all in use exemplar.py code. 8.5h 
* 2019-11-09: Got E working on repl.it again. fizz_buzz.exem now also working. Changed store_IFs() to better recognize 
condition novelty. 5h 
* 2019-11-05: Worked on reviving Exemplar on Repl.it. 2.5h 
* 2019-11-04: Got leap_year.exem and if/elif automatic ordering working. Latter is by brute force search completely 
independent of that for block endpoints, so a dimension is not added to the algorithmic complexity of either. 5.75h
* 2019-11-03: Had to improve input data typing for guess4.exem to deal with new IF handling. Then tested, refactored, 
and improved. Got up to: fixing if_order_search() to move 'if' consequents (in addition to conditions). 9h
* 2019-11-02: My notes say I got up to fixing expected vs actual condition, then data typing input. 10.75h
* 2019-11-01: Up to testing a factoradics approach to counting the possible permutations of if/elif order. 9h
* 2019-10-31: Finished building a data structure that tracks hopefully all the IF information needed to order the elif 
branches. 6.75h
* 2019-10-30: Implementing said solution, reaching point of altering IFs into ELIFs as needed. 10h   
* 2019-10-29: Determined my if/elif order solution, which in short is to generate-and-test IFs that Exemplar evaluates 
with eval(). 6.5h
* 2019-10-28: Documenting what I've learned, organizing notes. 6h
* 2019-10-27: Continued use of CASes Octave, Oct2Py, SymPy until, at 2am, success with sympy.solve([x<3, x<5])'s ability 
to tell Exemplar to pose IF x<3 before ELIF x<5 (by returning x < 3 in this case). 8.75h
* 2019-10-26: Continuing. 3h
* 2019-10-25: Began work to determine if/elif branch order. Studying Octave and SymPy to see if their symbolic and 
 logical abilities can help answer my questions of which IF conditions are mutually exclusive vs. have relationships
 that are specializations, intersections, or are orthogonal. 9.5h
* 2019-10-22: guess5.exem working with redone generate_code(). Co-located IFs now ELIFs after first IF. 3h
* 2019-10-21: 10 - 14:30. 16 - 18pm, 20:15 - 25:30 = 4.5 +2 + 5. 6hrs total. Committed changes after guess4.exem 
working. Studied ACM Transactions on Programming Languages and Systems' author guidelines.  Cleaning up notes.
* 2019-10-21 Done: making maximal use of trace info. guess4.exem working again. Prior 5 days: 5+6+2+9.5+11.5= 34h
* 2019-10-16 Began committing planned code changes that allow generate_code() to systematically distinguish new and 
corroborate old info from the user examples as they're turned into Python code. Prior 4 days: 6+4+11+11.5= 32.5h
* 2019-10-07 Continuing. 8h
* 2019-10-06 More planning, then began changes to generate_code(). 8h.
* 2019-10-05 Planning how to make generate_code() systematic rather than ad hoc.  5h 
* 2019-09-30 Continued work on how to recognize if/else situations (and by extension, solving leap_year.exem). Realized
a solution: consecutive IFs originating from different examples or iteration represent an if/else, not adjacent IFs. 10h  
* 2019-09-22 Good progress in getting leap_year.exem correctly interpreted again now that examples are not simply input,
assertions, and output, in that order. Created Boolean function is_loop_open(code), enabled a bool datatype interpretation 
of example data, and the generated function now both prints and returns last output where that appears desirable. 9h 
* 2019-09-18 Rewrote much of formal_args() for concision and correctness. leap_years.exem not yet (re) solved but 
TestLeapYear.py is at last being created. 4h
* 2019-09-17 Edited assertion_triple(), scheme(), get_unconditionals_post_control() and the conditions table to allow 
for compound conditions. 4h
* 2019-09-16 Rewrote fill_conditions_table() to allow for compound conditions. Generalized get_el_id() into 
get_line_item(). 4h
* 2019-09-15 Began enabling leap_years.exem, which has compound conditions in the assertions and is return-oriented 
(with a long IF structure) rather than interactive with the user as in the guess() functions. Created 
are_preambles_consistent() for store_fors(). 4h
* 2019-09-09 Completed work started yesterday. Also, clearing the "environment" (prior_values) between the processing of
 __example__ iterations. 4h
* 2019-09-08 At the point unneeded, removing __example__ loop and the all-in-one unit test (in favor of many). 2h
* 2019-09-05 Organizing Exemplar-related material in OneNote. 2h
* 2019-09-04 Exemplar now considers multiple examples automatically (without need to manually create loops as in 
guess5.exem). As such, both examples of guess4.exem are used to create its solution. 10h
* 2019-08-26 Posted 8min video, solicited ML improvement ideas from CS7641 Machine Learning. 1.5h
* 2019-08-21 Unify single quoting handling. Exemplar.py's internal unit tests now all passing. 2h
* 2019-08-20 "Finished" reading the paper to pickup terms etc for starting my own. 1h
* 2019-08-19 Reading "Program synthesis: challenges and opportunities" by David and Kroenig 2017. 2h
* 2019-08-18 Organizing my research notes. Browsing papers to determine journal to target for my research paper. 2h
* 2019-08-17 Function synthesis from guess5.exem working correctly. 2h 
* 2019-08-16 Debugging generate_code()'s attempts to insert "break" iff a FOR loop ends prematurely. Bug fix in 
update_for_loops_table(). Wrote get_1st_line_of_iteration(last_el_id). 10h
* 2019-08-15 Progress in debugging guess5.exem processing. 4h
* 2019-08-14 Debugging guess5.exem with TestGuess5Manual.py (where guess5 is an important step in being able to synthesize 
from multiple examples). 3h
* 2019-08-13 Refactoring in starter file, reformatting in exemplar.py. 3h
* 2019-08-12 Generalized for_loops_conflict() into get_control_conflicts(table). 3h
* 2019-08-11 All integration tests passing. Refamiliarized myself with the code. 4h
* 2019-08-10 All integration tests pass except get test_fill_cbt_guess4() so investigating that and the ins and outs of
exemplar.for_loop_conflict(). 2h
* 2019-08-09 Finished study of "Daikon system for dynamic detection of likely invariants" paper. 2h
* 2019-08-06 Initially recalled only goal of project. Seeing it anew I am energized for the battle rejoined. 2.5h
* 2019-05-19 *CS7646 ML4T's usurpation of my time begins in earnest.* 
* 2019-05-18 Finished studying DRAKON and conclude that it improves on flowcharting but is not a *r*evolution. 2h
* 2019-05-17 Studying DRAKON algorithmic visual programming and modeling language to plumb its ideas. 3h
* 2019-05-11 Worked on how to present Exemplar. Created get_control_conflicts(). 5.5h
* 2019-05-10 Created for_loops table and update_for_loops_table() to exclude mid-loops as ending points for controls 
opened pre-loop. 5h
* 2019-05-09 Created get_functions() and finished re-enabling the integration tests. 6h
* 2019-05-08 Improving store_ifs() and fill_cbt_with_maybe_rows(). 3.5h
* 2019-05-07 Re-enabling integration tests. 2.5h
* 2019-05-06 Debugging add_control_info_to_example_lines(). 4.25h
* 2019-05-05 Planning addition of columns control_id and controller to table example_lines. 2.25h
* 2019-05-04 To generate code that solves all examples of a problem, guess5.exem combines both examples of guess4 in a 
simulated loop. 7.25h
* 2019-05-03 Morning demonstration via Google Hangout. Finally guess4's User Loses example is working, by differentiating 
IF from FOR endpoints and applying min() and max() to their clei.el_last_id's, respectively. 5.5h
* 2019-05-02 Stopping rollback on last trial. Analyzing final database state versus ideal. 6h
* 2019-05-01 Enabled the favicon. TG and I improved the Copy button. 3h
* 2019-04-30 Organized log, notes. Re: the web UI, TG and I created a favicon. 1.5h
* 2019-04-29 Possibly coinciding with a PyCharm upgrade, Linux VM became slow, so I moved development back to Windows. 
(VirtualBox also prevented laptop from sleeping and frequently crashed it when lid was closed.) Still struggling to 
get Exemplar to consider all valid control block endings for guess4.exem's User Loses example. 7.75h
* 2019-04-28 Lots more work on deducing the possible control block endpoints implied by the exem traces. Got unittest to 
forget old target code and check only the up to date target code. 9.75h
* 2019-04-27 Fixed store_ifs() so IFs not added to CBT when there's a duplicate IF in the open loop started most recently. 6.25h
* 2019-04-26 Same work area as on 4/25, eg, JavaScript function generate_name(). 6h
* 2019-04-25 Worked on UI with TG on, eg, resizeIt(). Then I worked to enable guess4's User Loses example. 3.5h
* 2019-04-24 Worked on UI with TG. Documented plan to allow arbitrary function calls. 2h
* 2019-04-23 Thought about how ML may aid Exemplar. Finished organizing my development notes. 4.5h 
* 2019-04-22 Discussed recent changes to Exemplar with student TG and directed his automatic function naming efforts. 
Finished reading AlphaGo paper. 3.5h
* 2019-04-21 Added a input field for user to name their function. Studied Science 2018 AlphaGo paper. 2.25h
* 2019-04-20 Studied Leslie Lamport's TLA+. Added display of generated unit test to main.py UI. 6.25h
* 2019-04-19 Planning multi-example solving, researching sympy.isAlways(). 5h
* 2019-04-18 Many improvements to the JavaScript in main.py (repl.it's UI), e.g., re-enabling user entry of exem code traces. 10h
* 2019-04-17 Exemplar quickly generates a function that passes the unit test implied by guess4.exem's longest example. 
Controls are now example-dependent instead of problem-wide. Many bug fixes. 10.25h
* 2019-04-16 To simplify code generation, I've focused Exemplar on one example (the longest) of the given exem. 5.25h
* 2019-04-15 Created get_unconditional_post_control() to help narrow the search for code block endpoint. 8.5h
* 2019-04-14 To simplify generate_code() and to call it once not twice, the sequential target function (STF) was obviated
by, e.g., replacing function likely_data_type() with function cast_inputs().  Added function condition_type() to fine-tune
last_el_id calculation, i.e., reject 'assign' conditions as last_el_id's. 6.75h
* 2019-04-13 Nesting transactions so E can most efficiently explore a 2nd tier of possibilities: IF block endpoints. 6.5h
* 2019-04-12 Continuing manual testing. Changing indent (block creation) regime. Confirmed that db transactions can nest. 4.5h
* 2019-04-11 Stepping through guess4 to confirm operation. 1h
* 2019-04-10 Forgoing os.fork()'ing trials in favor of database ROLLBACK because after a fork(), PyCharm will only show 
the original process and worse, the database becomes trial-specific. 6h
* 2019-04-09 Because store_ifs() and store_code() modify the database while trialing last_el_id values, fork()ing added 
to reverse_trace() ahead of those. Read Sumit Gulwani's "Program Synthesis" to page "25". 5h
* 2019-04-08 Commenting store_fors() then reworking store_ifs() in its image. 3h
* 2019-04-07 Adjusted reverse_trace() for plan described in entry 2019-04-05. Added function get_python(el_id). 6.75h
* 2019-04-06 Code added to reverse_trace() to add known end-points (last_el_id value), along with their ct_id (i.e., 
control block identifier) into the table cbt_last_el_id (created yesterday) to offer a single point of last_el_id 
knowledge for SELECTing queries. 2h
* 2019-04-05 insert_for_loop() is now adding all possible last_el_id_maybe's for each ct_id (i.e., control block) into 
table control_block_traces. Each possible combination of those possibilities are instantiated as table cbt_last_el_id 
(columns: ct_id and last_el_id_maybe), one combination at a time, via a cartesian product of control_block_traces 
tables, in new function get_last_el_id_maybes(). Each combination is to be considered in turn for its ability to get all 
unit tests implied by the user examples (exem) to pass, until one is found. 9h 
* 2019-04-04 Bushwacked life's encroachments only enough to make remaining integration tests pass, and tentatively begin 
overhaul of generate_code() to eliminate redundant condition categorization. 2h
* 2019-04-02 store_fors()'s relationship to insert_for_loop_into_cbt() reworked and working, a heavy lift. Improved 
store_ifs() and added supporting functions. 10h
* 2019-04-01 Got exemplar working for guess3.exem again. Created controls table. 6h
* 2019-03-31 Added a handful of working integration tests. Analyzed how guess4.exem should break down, then began migrating
from a control_traces table to control_block_traces and control tables to capture every loop iteration. 8h
* 2019-03-30 Got TestExemplarIntegration.py working. Added tests for fill_conditions_table(). 5.5h
* 2019-03-29 Copied unit tests from (obsolete) TestExemplar.py to exemplar.py and TestExemplarIntegration.py and worked 
on re-enabling the latter. 3.5h
* 2019-03-28 Re-purposed the DB_DEBUG constant to enable database testing (instead of printing). 2.75h
* 2019-03-27 Improved UI significantly (i.e., main.py, visible at the repl.it url, below). Created class MockCursor. 7.5h
* 2019-03-26 Re-enabled test execution. Removed use of examples table. Altered process_examples() to combine examples. 6.75h
* 2019-03-25 Researched integration testing options. Enabled my Data Source in PyCharm and its database tool by switching 
Exemplar's memory database to file. 2.5h
* 2019-03-24 Working to improve and replace logic in generate_code() with use of new info, e.g., control scope, from the 
conditions and control_traces tables. 4.25h
* 2019-03-23 Re-enabled pycallgraph, created call_graph4_cropped.png. 5h
* 2019-03-22 Completed 1st version of store_ifs(). 2.5h
* 2019-03-20 - 2019-03-21 Troubleshot <https://repl.it/@gherson/Exemplar> website and working with a student assistant. 4h 
* 2019-03-19 Finished start_of_open_loop(), which forks the python/sqlite process to deal with ambiguity. 3h
* 2019-03-18 Finished the JavaScript creating an example table from user input ("exem"). 3h
* 2019-03-17 Continuing to fill out start_of_open_loop(). 5h
* 2019-03-16 Got Exemplar running in Linux VM on PyCharm. 2.75h 
* 2019-03-13 - 2019-03-15. Adjustments to Linux virtual machine, caught up on IRL chores. 2.25h
* 2019-03-12 Decided I needed to fork() to follow up on the ambiguity inherent in the exem's, so I researched how to do 
that in Python on Windows. Can't, so researched virtual machine options, then created a 6GB Ubuntu VM and installed PyCharm on it. 5h
* 2019-03-11 Worked on the user interface with TG and on database support Exemplar will need for generate and test. 2h
* 2019-03-10 Integrating use of the control_traces table into generate_code() and (new) top_of_open_loop(el_id). 7h
* 2019-03-09 Improved if_or_while() and fill_conditions_table() with new functions most_repeats_in_an_example(), store_fors(), store_ifs(). 6.75h
* 2019-03-08 More for-loop logistics in new functions get_line_item(), insert_for_loop_into_cbt(). 7.75h
* 2019-03-07 Planned changes to database, largely new tables loops and loop_patterns. 1.75h
* 2019-03-06 Fixed replace_hard_code() to only replace whole words with variable references. 3.25h
* 2019-03-05 get_range() now looking at one example at a time. 3.75h
* 2019-03-04 Adding and shuffling code between get_range(), fill_conditions_table(), fill_control_table(), and 
generate_code() to marshall enough info, in the right order, to solve the scoping problem. 7.25h
* 2019-03-03 fill_control_table() is correctly filling the control table's python, first_el_id, last_el_id1, 
last_el_id3, and control_id columns for FOR loops. 5.5h
* 2019-03-02 Rewriting get_range() as fill_control_table(). 4.75h
* 2019-03-01 Designing means and database columns to scope control structures. 7.75h
* 2019-02-28 Produced a plan and schedule of needed R&D accomplishments and shared with my student, TG. 1h
* 2019-02-27 Fixed an issue where guess3.exem's guess_count + 1 == 3 was showing up in the generated Python code as an 
assignment instead of as an assertion. 1h
* 2019-02-26 I decided that Exemplar (E) cannot always guess a correct interpretation of a correctly specified .exem, so 
I enabled a generate-and-test approach in E which will involve looping until it has generated a function, with control structures,
 that passes all unit tests and that accounts for every user assertion. Got <https://repl.it/@gherson/Exemplar> working again. 6.25h
* 2019-02-25 Automatic casting of sequential target function (STF)'s inputs allows the STF in TestGuess4.py to pass its unit test. 3.5h
* 2019-02-24 Studying Silver et al's 2018 AlphaGo paper. In Exemplar, the sequential version of the target 
function and its unit tests are added to the generated test class. 5h
* 2019-02-23 Discouraging that the problems I'm fixing with guess4's interpretation are the same that I'd fixed in 
guess3. So I'm thinking about how to use the target function's sequential version, whose generation is much more 
straightforward, as a guide rail for the version with control stuctures. 6.25h
* 2019-02-22 Working on guess4, which combines examples of a player losing and winning the eponymous game. 3.75h
* 2019-02-21 guess3 function synthesis working in full. Last bit was allowing automatic substitution of literals 
with expressions asserted equivalent by improving get_range(). 7.25h
* 2019-02-20 guess3 function synthesis working, including automatic unit testing. But I want a constant replaced with a
variable in guess3's last line, so that's next. 5.75h
* 2019-02-19 Almost correct function generated from guess3.exem. 7h
* 2019-02-18 Worked mostly in if_or_while(el_id, line, second_pass) to enable the IFs implied eg in guess3.exem. 4.25h
* 2019-02-17 get_range() supplying scope info of FOR loops. generate_code() adding assertions and control info to 
sequential version of target function. 10.5h
* 2019-02-16 Except for its line_scheme, conditions table is currently redundant with example_lines table.  Latter's
loop_likely now noting likely repetitive, selective, and sequential code as intended. 6.25h
* 2019-02-15 Code committed. Added unit tests directly to examplar.py for documentation; separate testing down, and 
most example problems not working, as I continue focus on conversational problem guess3. 8h
* 2019-02-14 generate_code() now generating a list rather than a string of code so prior code lines can be referenced.  
Table conditions now left outer joined with example_lines table so the former's rows can be referenced along side where 
extant. Manually correcting E's output for guess3, I finally saw the simple, code-able decisions involved (e.g., Do not 
add loop code beyond its 1st iteration). 2.5h
* 2019-02-13 `schematized('guess_count==0') == schematized('guess_count == 1') == 'guess_count==_'` to better detect 
looping of assertions. 1.5h
* 2019-02-12 Liberalized schematize() to reduce varying integers to underscore. Created function store_code and 5 tables 
to enable gradual imposition of flow control onto a baseline satisfying generated function of sequential flow control only. 6h
* 2019-02-11 Considered re-use of c suffix to mark constants (yes) and whether to require i1 or variable name in the 
examples (yes to both). Designed tables iterations, selections, iterations_conditions, and selections_conditions. 3h
* 2019-02-10 Continued to replace the mark_loop_likely function with the finer grained fill_conditions_table(), which 
maps each condition to one of simple assignment, selection, or iteration. 5h
* 2019-02-09 Determining how best to get E able to infer program structure from hints. Coding to fill conditions table. 6h
* 2019-02-08 All variables being created with preferred names in guess3.exem. Continued re-implementing loops and IFs in 
stateful model, looking also at fizz_buzz.exem. Added table conditions. 9.5h
* 2019-02-07 Reviewed code changes with TG. Expanding automatic replacement of hard-coded values with variables. 2.5h
* 2019-02-06 Source .exem file is now appended to target Test-.py file. 1h
* 2019-02-05 guess3.exem's synthesized function has the hinted variable names and passes its unit test. (Loop detection remains.) 4.5h   
* 2019-02-04 Studying Lib/re.py and an example tokenizer. 2h
* 2019-02-03 Working to synthesize guess.py of <http://inventwithpython.com/invent4thed/chapter3.html> via their transcript (as guess3.exem). 5h
* 2019-02-02 jokes.exem working front to back (e.g., creating TestJokes.py) in the new format and model. Code committed. 7h
* 2019-02-01 Programming inner function mark_sequences() during a too busy day. 1h
* 2019-01-31 Test generation recoding on final piece, creating function under test. Good progress. 6h
* 2019-01-30 Test generation coding. Should finish today. 3h
* 2019-01-29 Re-enabled automatic unit testing for a simple example (jokes.exem).  Now onto the others... 9h
* 2019-01-28 Studied a Sumit Gulwani PbE video with TG. Committed code. Determined scheme for unit testing all i/o 
involving mocking print() and input(). 2h
* 2019-01-27 Got a simple example working in new format and modeling except for the automatic unit testing (that's next). 7h
* 2019-01-26 Wholesale code change required for stateful modeling. May have my examples working today. 7h 
* 2019-01-25 Got MS Prose working locally and further work with their C# code doesn't appear cost effective, unless I 
want to use the Prose SDK in my project.  Asked MS Research for access to their very interesting Prose Playground. 
Then determined more of how to allow stateful models: Iff the first i/o in the exem is input, a *function* will be 
generated in which that input or inputs are considered arguments, and the last output is a `return`.  While any inputs 
subsequent to the arguments become input()s and any output before the return become print()s.)  OTOH, users can force a 
non-functional, script interpretation by making their first i/o an output of nothing. 6h
* 2019-01-24 2hrs with TG studying and installing MS Prose and Tabulator. I continued with Prose and my notes at home. 5h
* 2019-01-23 Worked out how to allow users to move forward with imperfect examples, and to receive suggestions back from 
Exemplar: 3 phase interpretation, from a line to tabular orientation. Studied Tabulator (js library).  5h
* 2019-01-22 Exemplar examples are being extended to allow stateful interpretation by lifting the single i/o per example 
requirement and considering all "output" as results to retain through the example (i.e., state).  Also researched 
JavaScript table libraries and will probably go with Tabulator.info. 6h
* 2019-01-21 Committed code to parameterize all SQL queries and allow user to omit 'reason's where s/he simply wants to map input to output. 6h
* 2019-01-20 Committed improvements to file handling and function names. Studied, plotted and planned next steps. 8h
* 2019-01-19 Web UI at repl.it is working and user friendly. Committed code changes. 8h
* 2019-01-18 Fighting with JavaScript, progress to post shortly... 4h
* 2019-01-17 studied Flask and JavaScript. Replaced four hard-coded routing functions in main.py. 3h
* 2019-01-16 Read Code Shrew paper, studied UI examples on repl.it with TG.  Exemplar now has a web UI to all our example transformations. 4h
* 2019-01-15 Got Exemplar working at <https://repl.it/@gherson/Exemplar>. Then, to create a real as opposed to a file-based 
user interface, I compared REMI to Flask then got latter working for output. 4h 
* 2019-01-14 Exemplar's Sqlite dependency precludes use of Skulpt for now, so researched an alternative. 1h
* 2019-01-11 Created prime# call graph annotated.jpg. 2h
* 2019-01-10 TG got Skulpt working. I studied QuickFOIL, Brachylog, Eurisko, and mini-cp while thinking about how to 
make Exemplar (E) less niche and more tolerant of incomplete examples. Answer is nonobvious, so I'll instead concentrate 
on extending E in more or less its current form until it is useful to me. If successful, adaptions can then be made for 
friendliness. E.g., a user won't need to decide if 'reason's are needed for a particular program synthesis before 
investing time in E vs another PbE system if E includes the typical ability to work without them. 3h
* 2019-01-09 Installed pycallgraph and created prime_number_call_graph.png. 2h
* 2019-01-08 Got student TG started figuring out Skulpt (in-browser Python), 12:30 - 13:30. (TG is reminded of another 
UI to Python: Jupyter notebooks. Taking a look now, I wonder if instead of entering Python code and getting plots out, 
user could enter unit tests etc in the cells and get Python functions out. Such that an "Exemplar notebook" == program.) 1h
* 2019-01-07 Explained Exemplar to advanced computer science student TG, 10am - 11am. 1h
