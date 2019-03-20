# main.py is repl.it's starting point.
import exemplar as e
import importlib, unittest, random
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def begin():
    return demo("guess3")  # Start user off with this demonstration.


@app.route('/demo/<string:demo>', methods=['POST'])
def demo(demo):
    return generate(file=demo + ".exem")


@app.route('/generate', methods=['POST'])
def generate(file=""):
    if file:
        user_examples = e.from_file(file)
    else:
        # Write the user's examples from the request object into a file.
        user_examples = request.form['examples_ta']
        # examples = examples.splitlines(keepends=True)  # str to List.
        file = 'e' + str(random.randrange(10)) + ".exem"  # Pick a name at random.
        e.to_file(file, user_examples)  # Write to it.
    code = e.reverse_trace(file)  # Capturing code for display.

    # Run the target function tests just created.
    class_name = "Test" + e.underscore_to_camelcase(file[0:-5])  # prime_number.exem -> TestPrimeNumber
    TestClass = importlib.import_module(class_name)
    suite = unittest.TestLoader().loadTestsFromModule(TestClass)
    unittest.TextTestRunner().run(suite)

    return html(user_examples, code)


def html(examples, code):
    top_html = """<!DOCTYPE html><html>
    <head><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">

<script type="text/javascript">
function table_maker(input, truth, output) {
    var examples = document.getElementById("examples");
    examples.innerHTML += "<tr><td>" + input + "</td><td>" + truth + "</td><td>" + output + "</td></tr>\n";
}
function exem_table(examples) {
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
</script>
</head>\n
<body onload="make_table()"><p><b>Instructions</b>: Enter &lt;input↲&gt;output↲assertions↲
    examples of desired behavior on the left then press Tab.  (Assertions may be omitted or comma separated.) Exemplar will 
    attempt to generate conforming Python code on the right.</p>\n"""

    demos_html = """<br/><i>nope, sorry, demos are Under Construction</i><br/>Or, click a button for another demonstration. 
    (There may be a <5sec pause while tests are run in the console.)\n
    <table><tr>"""
    demos = ['prime_number', 'leap_year', 'guess2', 'fizz_buzz']
    for demo in demos:
        demos_html += "<td><form method='POST' action='/demo/" + demo + \
                      "'>\n<input type='submit' value='" + demo + "'/></form></td>\n"
    demos_html += "</tr></table>\n"

    key = """<p>Notes:</p><ul>
  <li><dl><dt>term</dt><dd>definition</dd></dl></li></ul>"""

    # print("example:", examples)  # Took a few restarts to appear (in console).
    return top_html + """<table><tr><th>Examples</th><th>Code generated</th></tr>\n
    <tr><td><form id="examples_f" method="POST" action="/generate">\n
    <textarea id="examples_ta" name="examples_ta" rows="14" cols="40" onchange=
    "submit();">""" + ''.join(examples) + \
        """</textarea></form></td>\n
           <td><textarea id="code_generated" rows="14" cols="40" readonly="readonly">""" + \
           code + '</textarea></td></tr></table>\n' + demos_html + key + '''\n<table id="examples" cellpadding="1" border="1">
 <tr><th>input</th><th>truth</th><th>output</th></tr>
 </table>
<script type="text/javascript">
// Manually creating an examples array: -->
var examples = new Array();
i = 0;
examples[0] = '>Hello! What is your name?';
examples[1] = '<Albert';
examples[2] = 'name==i1';
examples[3] = '>Hello Friend';
examples[4] = '<I am not your friend';
examples[5] = 'True that!';

exem_table(examples);
</script>
<!--
Python pseudocode:
print("var examples = new Array();")
print("i = 0;\n");
for example in examples:
    print("examples[" + i + '] = "' + example + '";\n')
    print("i += 1;\n");
 -->
 </html>'''


if __name__ == '__main__':
    # pass
    app.run(host='0.0.0.0', port=8080)
# With this IF, execution never reaches here.
