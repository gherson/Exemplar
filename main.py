# main.py is repl.it's starting point for projects of type 'Python'.
import exemplar as e
import html as h  # To avoid weird "AttributeError: 'function' object has no attribute 'escape'" error.
import importlib, unittest, random
from flask import Flask, request  # Flask is a micro web framework.
from typing import List

app = Flask(__name__)


def colorize(lines: List[str]) -> str:
    colorized = ''
    for line in lines:
        if line[0] == '<':
            colorized += "<font color='blue'>" + h.escape(line) + "</font>"
        elif line[0] == '>':
            colorized += "<font color='green'>" + h.escape(line) + "</font>"
        else:
            colorized += h.escape(line)
    return colorized


@app.route('/')
def begin():
    return demo("guess3")  # Start off with a demonstration.


@app.route('/demo/<string:demo>', methods=['POST'])
def demo(demo):
    return generate(file=demo + ".exem")  # Pull guess3.exem.


@app.route('/generate', methods=['POST'])
def generate(file=""):
    if file:
        user_examples = e.from_file(file)
    else:
        # Write the user's examples from the request object into a file.
        user_examples = request.form['examples_edit']
        file = 'e' + str(random.randrange(10)) + ".exem"  # Pick a name at random.
        e.to_file(file, user_examples)  # Write to it.
    code = e.reverse_trace(file)  # Capture code for display.

    # Run the target function tests just created.
    class_name = "Test" + e.underscore_to_camelcase(file[0:-5])  # prime_number.exem -> TestPrimeNumber
    TestClass = importlib.import_module(class_name)
    suite = unittest.TestLoader().loadTestsFromModule(TestClass)
    unittest.TextTestRunner().run(suite)

    return html(user_examples, code)


def html(examples, code):
    head_html = """<!DOCTYPE html><html lang="en">
    <head><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <title>Exemplar</title>

<script>
function table_maker(input, truth, output) { // Line by line.
    var examples = document.getElementById("examples_t");
    examples_t.innerHTML += "<tr><td>" + input + "</td><td>" + truth + "</td><td>" + \
    output + "</td></tr>\\n";
}
function exem_table(examples) { // From iterable to fields to calling table_maker() a line at a time.
    input = ''; truth = ''; 
    for (var i=0; i<examples.length; i++) {
        line = examples[i];
        // Input
        if (line.substring(0,1) == '<') { 
            if (input != '' || truth != '') {  
                table_maker(input, truth, '');
                input = ''; truth = '';
            }
            input = line.substring(1);
        // Truth
        } else if (line.substring(0,1) != '<' && line.substring(0,1) != '>') {
            if (truth != '') {  
                table_maker(input, truth, '');
                input = ''; truth = ''; 
            }
            truth = line;
        // Output
        } else {
            if (line.substring(0,1) != '>') {
                throw new Error("Output line expected, not " + line );
            }  
            table_maker(input, truth, line.substring(1));
            input = ''; truth = ''; 
        }
    }
    // If examples do not end with output, call table_maker() 1 more time.  
    if (line.substring(0,1) != '>') {
        table_maker(input, truth, '');
    }
}
// Creating an examples array: 
    var examples = new Array();\n"""

    # Back to python to...
    clean_examples = e.clean(examples)  # Snip comments and header.
    i = 0
    for example in clean_examples:  # Create a large JS array.
        head_html += "\texamples[" + str(i) + '] = "' + example.rstrip() + '";\n'
        i += 1
    """ What the JS array looks like:
    examples[0] = '>Hello! What is your name?';
    examples[1] = '<Albert';
    examples[2] = 'name==i1';
    """

    head_html += "</script></head>\n"

    demos_html = """<br/><i>Sorry, demos are Under Construction</i><br/>Or, click a button for another demonstration. 
    (There may be a <5sec pause while tests are run in the console.)\n
    <table><tr>"""
    demos = ['prime_number', 'leap_year', 'guess2', 'fizz_buzz']
    for demo in demos:
        demos_html += "<td><form method='POST' action='/demo/" + demo + \
                      "'>\n<input type='submit' value='" + demo + "'/></form></td>\n"
    demos_html += "</tr></table>\n"

    key = ""  # """"<p>Notes:</p><ul><li><dl><dt>term</dt><dd>definition</dd></dl></li></ul>"""

    # print("example:", examples)  # Took a few restarts to appear (in console).

    body_top = """<body onload="exem_table(examples)">
    <h1>Exemplar</h1> <h2>code generation from examples</h2>
    <p><b>Instructions</b>: 
    <ol><li>Enter &lt;<font color='blue'><i>input</i></font>↲&gt;<font color='green'><i>output</i></font>↲<i>assertions</i>↲
    sequences demonstrating desired behavior on the left.</li>\n
    <li>Assertions may be omitted or comma separated.</li>\n
    <li>Separate example runs with a blank line.</li>\n
    <li>Press Tab. Exemplar will attempt to generate conforming Python code on the right.</li>\n  
    </ol>\n"""

    # Show the raw examples, the examples tabulated, the code generated, and finally, a choice of demos.
    return head_html + body_top + """<table cellpadding="7"><tr><th  width="33%">Editable examples</th><th width="33%">Examples tabulated</th><th>Code generated</th></tr>\n
    <tr><td valign="top"><form id="examples_f" method="POST" action="/generate">\n
        <div id="examples_edit" contenteditable="true" style="border: thin solid black" onchange="submit();"><pre>""" + colorize(
        examples) + \
           """</pre></div></form></td>\n
    <td valign="top"><table id="examples_t" cellpadding="1" border="1"><tr><th><u><font color="blue">input</font></u></th><th><u>truth</u></th>
     <th><u><font color="green">output</font></u></th></tr></table></td>\n""" + \
           '<td valign="top"><textarea id="code_generated" rows="40" cols="60" readonly="readonly">' + \
           code + '</textarea></td></tr></table>' + demos_html + key + \
           '</html>'


if __name__ == '__main__':
    # pass
    app.run(host='0.0.0.0', port=8080)
# With this IF, execution never reaches here.
