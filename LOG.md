# Plans
* Starting with easy ones, get more Python functions created via Exemplar, improving it as we go.
* ~~For the UI, http://Shrew.app -style Python in-browser, allowing user to see progressive improvements to output as s/he provides more examples.~~ Done 2019-01-19
* Enabling reason-less transformations, where those can be done with confidence, by leveraging PbE techniques of Rishabh Singh and Sumit Gulwani. 

# Considering
* Utilizing Armando Solar-Lezama's Sketch as an Exemplar backend, to help Exemplar fill in more difficult code unknowns ("holes").

# Log of work
* 2019-01-27 Wholesale code change required for stateful modeling. May have my examples working today. 7h 
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
