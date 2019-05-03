# main.py is repl.it's starting point for projects of type 'Python'.
import exemplar as e
import html as h  # To avoid weird "AttributeError: 'function' object has no attribute 'escape'" error.
import random
from flask import Flask, request  # Flask is a micro web framework.
from typing import List

# begin()->demo()->generate() (calls reverse_trace then) ->html(). See method html() after these Flask handlers
# for the HTML and JavaScript that gets returned.

app = Flask(__name__)


def python_colorize(lines: List[str]) -> str:
    colorized = ''
    for line in lines:
        if not line.strip():
          colorized += '\n'
        elif line[0] == '<':
            colorized += "<font color='blue'>" + h.escape(line) + "</font>"
        elif line[0] == '>':
            colorized += "<font color='green'>" + h.escape(line) + "</font>"
        else:
            colorized += h.escape(line)
    return colorized


@app.route('/')
def begin():
    return demo("guess4")  # Start off with a demonstration.


@app.route('/demo/<string:demo>', methods=['POST'])
def demo(demo):
    return generate(file=demo + ".exem")  # Pull guess3.exem.


@app.route('/generate', methods=['POST'])
def generate(file=""):
    if file:
        user_examples_list = e.from_file(file)
    else:
        # Write the user's examples from the request object into a file.
        # request.form   window.form['examples_f'].div['examples_edit']
        user_examples = request.form['examples_i']
        # return "<!DOCTYPE html><html lang='en'><body>" + str(user_examples) + "</body></html>"
        name = request.form['function_name']
        if name and name != 'NameYourFunctionHere':
            file = name + ".exem"  # User-specified function name
        else:
            file = 'e' + str(random.randrange(10)) + ".exem"  # Pick a name at random.
        e.to_file(file, user_examples)  # Write to it.
        user_examples_list = user_examples.split('\n')
    code, test_file_contents = e.reverse_trace(file)  # Capture code for display.
    # return "<!DOCTYPE html><html lang='en'><body>" + str(len(code)) + "</body></html>"

    return html(user_examples_list, code, test_file_contents)

# Return html to the browser with embedded JavaScript.
def html(examples_list, code, test_file_contents):
    # return "<!DOCTYPE html><html lang='en'><body>" + "\n".join(examples_list) + "</body></html>"
    head_html = """<!DOCTYPE html><html lang="en">
    <head><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"><meta charset="UTF-8">
    <link rel="icon" type="image/png" href="https://cultivatedbigcustomization--gherson.repl.co/truth.png">
    <title>Exemplar</title>
<script src="http://www.google.com/jsapi"></script>
<script>google.load('prototype', '1.6.0.2');</script>
<script>
function resizeIt(textarea_name) { // Uses Prototype. From https://stackoverflow.com/a/7523/575012
    var str = $(textarea_name).value;
    var cols = $(textarea_name).cols;
    var lineCount = 0;
    $A(str.split("\\n")).each( function(l) {
        lineCount += Math.ceil( l.length / cols ); // Take into account long lines
    })
    $(textarea_name).rows = lineCount + 1;
};

// Workaround for Flask not putting div elements' content into the Request object.
function copyDivToInput(f) { // examples_edit to examples_i
    var examples = document.getElementById("examples_edit");
    f.examples_i.value = examples.innerText;  
    f.submit();
}

function encodeAndWrap(str, tag) {
     return str.replace(/[\u00A0-\u99999<>\&]/g, function(i) {
         return (tag ? '<'+tag+'>' :'')+'&#'+i.charCodeAt(0)+';'+(tag ? '</'+tag+'>' : '');
    });
}; // HTML entity encoder, from http://jsfiddle.net/E3EqX/4/ 4/18/19

function table_maker(input, truth, output) { // Line by line.
    input = encodeAndWrap(input, '')
    truth = encodeAndWrap(truth, '')
    output = encodeAndWrap(output, '')
    var examples = document.getElementById("examples_t");
    examples_t.innerHTML += "<tr><td>" + input + "</td><td>" + truth + "</td><td>" + \
    output + "</td></tr>\\n";
}
function exem_table(examples) { // From iterable to fields to calling table_maker() a line at a time.
    input = ''; truth = ''; 
    for (var i=0; i<examples.length; i++) {
        line = examples[i];
        if (line == '') table_maker(' ',' ',' ')

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

function copyFunction(textarea_name, button_id) {
    // Get the text field
    var copyText = document.getElementById(textarea_name);

    // Select the text field
    copyText.select();

    // Copy the text inside the text field
    document.execCommand("copy"); 
    document.getElementById(button_id).style.background='#D3D3D3';
    document.getElementById(button_id).innerHTML = "Copied!";       
} // by TG

function mouseUp(button_id) {
    document.getElementById(button_id).innerHTML = "Copy";
    document.getElementById(button_id).style.background='#FFFFFF';
}

function generate_name() { // Provide default function name
    exem = document.getElementById('examples_edit').innerText; // div
    document.getElementById('function_name').value = exem.substring(0,15).trim().replace(/[^a-zA-Z0-9]/g, '');
}

// Creating an examples array: 
var examples = new Array();\n"""

    # Back to python to...
    clean_examples_list = e.clean(examples_list)  # Snip comments and header.
    # return "<!DOCTYPE html><html lang='en'><body>" + "\n".join(clean_examples_list) + "</body></html>"
    i = 0
    for example in clean_examples_list:  # Create a large JS array.
        head_html += "\texamples[" + str(i) + '] = "' + example.rstrip() + '";\n'
        i += 1
    """ What the JS array looks like:
    examples[0] = '>Hello! What is your name?';
    examples[1] = '<Albert';
    examples[2] = 'name==i1';
    """

    head_html += "</script></head>\n"

    demos_html = """<br/><i>Sorry, demos are Under Construction</i><br/>Or, click a button for another demonstration. 
    (There may be a &lt;5sec pause while tests are run in the console.)\n
    <table><tr>"""
    demos = ['prime_number', 'leap_year', 'guess2', 'fizz_buzz']
    for demo in demos:
        demos_html += "<td><form method='POST' action='/demo/" + demo + \
                      "'>\n<input type='submit' value='" + demo + "'/></form></td>\n"
    demos_html += "</tr></table>\n"

    key = ""  # """"<p>Notes:</p><ul><li><dl><dt>term</dt><dd>definition</dd></dl></li></ul>"""

    # print("example:", examples)  # Took a few restarts to appear (in console).

    body_top = """<body onload="exem_table(examples);">
    <h1>Exemplar</h1> <h2>code generation from examples</h2>\n
    <i>Proof of concept that the essential elements of a general algorithm, i.e., input, output, control structure, 
    calculation, variable naming and substitution, can be demonstrated with little abstraction or structure 
    and still be understood and matched by a code generator. 
    <br/>gherson 2019-04-18 </i>\n
    <p><b>Instructions</b>: 
    <ul><li>Enter &lt;<font color='blue'><i>input</i></font>↲&gt;<font color='green'><i>output</i></font>↲<i>assertions</i>↲
    sequences demonstrating desired behavior on the left.</li>\n
    <li>Assertions ("truth") may be line or comma separated.</li>\n
    <li>To name your input, immediately follow it with assertion <code><i>yourname</i>==i1</code></li>\n
    <li>Separate your example traces with a blank line. (Currently only longest example is used.)</li>\n
    <li>Then press Submit below to have Exemplar attempt to generate conforming Python code on the right.</li>\n  
    </ul>\n"""

    # Show the raw examples, the examples tabulated, the code generated, and finally, a choice of demos.
    # The HTML structure is a table: the 1st row is headings and the second row cells are form, table, and textarea, respectively. 4/18/19
    # return "<!DOCTYPE html><html lang='en'><body>" + str(len(clean_examples_list)) + "</body></html>"
    return head_html + body_top + '''<table cellpadding="7"><tr><th width="25%">Editable examples</th><th width="33%">Examples tabulated</th><th>Code generated &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </th></tr>\n
    <tr><td valign="top">
    <form name="examples_f" id="examples_f" method="POST" action="/generate">\n
    Editable function name<br/>\n
    <input type="text" id="function_name" name="function_name" value="NameYourFunctionHere"/><input type="hidden" name="examples_i"/>
        <div name="examples_edit" id="examples_edit" contenteditable="true" style="border: thin solid black; width: 400px; overflow: auto"><pre>''' + python_colorize(examples_list) + '''</pre></div><input type="submit" value="Submit" onclick="copyDivToInput(this.form)"/> </form><br/></td>\n<td valign="top"><table id="examples_t" cellpadding="1" border="1"><tr><th><font color="blue">input</font></th><th>truth</th>
    <th><font color="green">output</font></th></tr></table></td>\n
    <td valign="top"><textarea name="code_generated" id="code_generated" rows="10" cols="60" readonly = "readonly">''' + code + '''</textarea><br/>\n
    <button id="code_button" onmousedown="copyFunction('code_generated', 'code_button')" onmouseup="mouseUp('code_button')">Copy</button><br/><br/>\n
    <button id="test_file_button" onmousedown="copyFunction('test_file_contents', 'test_file_button')" onmouseup="mouseUp('test_file_button')">Copy</button><b><center>Code generated with unit test</center></b><textarea name="test_file_contents" id="test_file_contents" rows="10" cols="60" readonly = "readonly">''' + test_file_contents + '''</textarea><br/></td></tr></table>\n''' + demos_html + key + """<script>
    resizeIt('code_generated'); // Initial on load
    resizeIt('test_file_contents'); // Initial on load
    generate_name(); // Provide default function name
</script></html>"""


if __name__ == '__main__':
    # pass
    app.run(host='0.0.0.0', port=8080)
# With this IF, execution never reaches here.
