# Plans
* Starting with easy ones, get more Python functions created via Exemplar, improving it as we go.
* ~~For the UI, http://Shrew.app -style Python in-browser, allowing user to see progressive improvements to output as s/he provides more examples.~~ Done 2019-01-19
* Enabling reason-less transformations, where those can be done with confidence, by leveraging PbE techniques of Rishabh Singh and Sumit Gulwani. 

# Considering
* Utilizing Armando Solar-Lezama's Sketch as an Exemplar backend, to help Exemplar fill in more difficult code unknowns ("holes").

# Log of work
* 2019-03-17 Continuing to fill out start_of_open_loop(). 5h
* 2019-03-16 Got Exemplar running in Linux VM on PyCharm. 2.75h 
* 2019-03-13 - 2019-03-15. Adjustments to Linux virtual machine, caught up on IRL chores. 2.25h
* 2019-03-12 Decided I needed to fork() to follow up on the ambiguity inherent in the exem's, so I researched how to do that in Python on Windows. Can't, so researched virtual machine options, then created a 6GB Ubuntu VM and installed PyCharm on it. 5h
* 2019-03-11 Worked on the user interface with TG and on database support Exemplar will need for generate and test. 2h
* 2019-03-10 Integrating use of the control_traces table into generate_code() and (new) top_of_open_loop(el_id). 7h
* 2019-03-09 Improved if_or_while() and fill_conditions_table() with new functions most_repeats_in_an_example(), load_for_loops(), load_ifs(). 6.75h
* 2019-03-08 More for-loop logistics in new functions el_id_peek(), insert_for_loop(). 7.75h
* 2019-03-07 Planned changes to database, largely new tables loops and loop_patterns. 1.75h
* 2019-03-06 Fixed replace_hard_code() to only replace whole words with variable references. 3.25h
* 2019-03-05 get_range() now looking at one example at a time. 3.75h
* 2019-03-04 Adding and shuffling code between get_range(), fill_conditions_table(), fill_control_table(), and generate_code() to marshall enough info, in the right order, to solve the scoping problem. 7.25h
* 2019-03-03 fill_control_table() is correctly filling the control table's python, first_el_id, last_el_id1, last_el_id3, and control_id columns for FOR loops. 5.5h
* 2019-03-02 Rewriting get_range() as fill_control_table(). 4.75h
* 2019-03-01 Designing means and database columns to scope control structures. 7.75h
* 2019-02-28 Produced a plan and schedule of needed R&D accomplishments and shared with my student, TG. 1h
* 2019-02-27 Fixed an issue where guess3.exem's guess_count + 1 == 3 was showing up in the generated Python code as an assignment instead of as an assertion. 1h
* 2019-02-26 I decided that Exemplar (E) cannot always guess a correct interpretation of a correctly specified .exem, so I enabled 
a generate-and-test approach in E which will involve looping until it has generated a function, with control structures,
 that passes all unit tests and that accounts for every user assertion. Got https://repl.it/@gherson/Exemplar working again. 6.25h
* 2019-02-25 Automatic casting of sequential target function (STF)'s inputs allows the STF in TestGuess4.py to pass its unit test. 3.5h
* 2019-02-24 Studying Silver et al's 2018 AlphaGo paper in Science. In Exemplar, the sequential version of the target function and its unit tests are added to the generated test class. 5h
* 2019-02-23 Discouraging that the problems I'm fixing with guess4's interpretation are the same that I'd fixed in guess3. So I'm thinking about how to use the target function's sequential version, whose generation is much more straightfoward, as a guide rail for the version with control stuctures. 6.25h
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
* 2019-02-14 generate_code() now generating a list rather than a string of code so prior code lines can be referenced.  Table conditions now left outer joined with example_lines table so the former's rows can be referenced along side where extant. Manually correcting E's output for guess3, I finally saw the simple, code-able decisions involved (e.g., Do not add loop code beyond its 1st iteration). 2.5h
* 2019-02-13 `schematized('guess_count==0') == schematized('guess_count == 1') == 'guess_count==_'` to better detect looping of assertions. 1.5h
* 2019-02-12 Liberalized schematize() to reduce varying integers to underscore. Created function store_code and 5 tables to enable gradual imposition of flow control onto a baseline satisfying generated function of sequential flow control only. 6h
* 2019-02-11 Considered re-use of c suffix to mark constants (yes) and whether to require i1 or variable name in the examples (yes to both). Designed tables iterations, selections, iterations_conditions, and selections_conditions. 3h
* 2019-02-10 Continued to replace the mark_loop_likely function with the finer grained fill_conditions_table(), which maps each condition to one of simple assignment, selection, or iteration. 5h
* 2019-02-09 Determining how best to get E able to infer program structure from hints. Coding to fill conditions table. 6h
* 2019-02-08 All variables being created with preferred names in guess3.exem. Continued re-implementing loops and IFs in stateful model, looking also at fizz_buzz.exem. Added table conditions. 9.5h
* 2019-02-07 Reviewed code changes with TG. Expanding automatic replacement of hard-coded values with variables. 2.5h
* 2019-02-06 Source .exem file is now appended to target Test-.py file. 1h
* 2019-02-05 guess3.exem's synthesized function has the hinted variable names and passes its unit test. (Loop detection remains.) 4.5h   
* 2019-02-04 Studying Lib/re.py and an example tokenizer. 2h
* 2019-02-03 Working to synthesize guess.py of http://inventwithpython.com/invent4thed/chapter3.html via their transcript (as guess3.exem). 5h
* 2019-02-02 jokes.exem working front to back (e.g., creating TestJokes.py) in the new format and model. Code committed. 7h
* 2019-02-01 Programming inner function mark_sequences() during a too busy day. 1h
* 2019-01-31 Test generation recoding on final piece, creating function under test. Good progress. 6h
* 2019-01-30 Test generation coding. Should finish today. 3h
* 2019-01-29 Re-enabled automatic unit testing for a simple example (jokes.exem).  Now onto the others... 9h
* 2019-01-28 Studied a Sumit Gulwani PbE video with TG. Committed code. Determined scheme for unit testing all i/o involving mocking print() and input(). 2h
* 2019-01-27 Got a simple example working in new format and modeling except for the automatic unit testing (that's next). 7h
* 2019-01-26 Wholesale code change required for stateful modeling. May have my examples working today. 7h 
* 2019-01-25 Got MS Prose working locally and further work with their C# code doesn't appear cost effective, unless I want to use the Prose SDK in my project.  Asked MS Research for access to their very interesting Prose Playground. 
Then determined more of how to allow stateful models: Iff the first i/o in the exem is input, a *function* will be generated in which that input or inputs are considered arguments, and the last output is a `return`.  While any inputs subsequent to the arguments become input()s and any output before the return become print()s.)  OTOH, users can force a non-functional, script interpretation by making their first i/o an output of nothing. 6h
* 2019-01-24 2hrs with TG studying and installing MS Prose and Tabulator. I continued with Prose and my notes at home. 5h
* 2019-01-23 Worked out how to allow users to move forward with imperfect examples, and to receive suggestions back from Exemplar: 3 phase interpretation, from a line to tabular orientation. Studied Tabulator (js library).  5h
* 2019-01-22 Exemplar examples are being extended to allow stateful interpretation by lifting the single i/o per example requirement and considering all "output" as results to retain through the example (i.e., state).  Also researched JavaScript table libraries and will probably go with Tabulator.info. 6h
* 2019-01-21 Committed code to parameterize all SQL queries and allow user to omit 'reason's where s/he simply wants to map input to output. 6h
* 2019-01-20 Committed improvements to file handling and function names. Studied, plotted and planned next steps. 8h
* 2019-01-19 Web UI at repl.it is working and user friendly. Committed code changes. 8h
* 2019-01-18 Fighting with JavaScript, progress to post shortly... 4h
* 2019-01-17 studied Flask and JavaScript. Replaced four hard-coded routing functions in main.py. 3h
* 2019-01-16 Read Code Shrew paper, studied UI examples on repl.it with TG.  Exemplar now has a web UI to all our example transformations. 4h
* 2019-01-15 Got Exemplar working at https://repl.it/@gherson/Exemplar. Then, to create a real as opposed to a file-based user interface, I compared REMI to Flask then got latter working for output. 4h 
* 2019-01-14 Exemplar's Sqlite dependency precludes use of Skulpt for now, so researched an alternative. 1h
* 2019-01-11 Created prime# call graph annotated.jpg. 2h
* 2019-01-10 TG got Skulpt working. I studied QuickFOIL, Brachylog, Eurisko, and mini-cp while thinking about how to make Exemplar (E) less niche and more tolerant of incomplete examples. Answer is nonobvious, so I'll instead concentrate on extending E in more or less its current form until it is useful to me. If successful, adaptions can then be made for friendliness. E.g., a user won't need to decide if 'reason's are needed for a particular program synthesis before investing time in E vs another PbE system if E includes the typical ability to work without them. 3h
* 2019-01-09 Installed pycallgraph and created prime_number_call_graph.png. 2h
* 2019-01-08 Got student TG started figuring out Skulpt (in-browser Python), 12:30 - 13:30. (TG is reminded of another UI to Python: Jupyter notebooks. Taking a look now, I wonder if instead of entering Python code and getting plots out, user could enter unit tests etc in the cells and get Python functions out. Such that an "Exemplar notebook" == program.) 1h
* 2019-01-07 Explained Exemplar to advanced computer science student TG, 10am - 11am. 1h
