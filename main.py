# main.py is repl.it's starting point.
import exemplar as e
import importlib, unittest
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def begin():
    return demo("fizz_buzz")  # Start user off with this demo.


@app.route('/demo/<string:demo>', methods=['POST'])
def demo(demo):
    return generate(file=demo + ".exem")


@app.route('/generate', methods=['POST'])
def generate(file=""):
    if file:
        examples = e.from_file(file)
    else:
        # Write the user's examples from the request object into a file.
        # trace, code = e.reverse_trace(examples=request.form['examples_ta'])
        examples = request.form['examples_ta']
        examples = examples.splitlines(keepends=True)  # str to List.
        file = str(random.randrange(10)) + ".exem"  # Pick a name at random.
        e.to_file(file, examples)  # Write to it.
    code = e.reverse_trace(file)

    # Run the target function tests just created.
    class_name = "Test" + e.underscore_to_camelcase(file[0:-5])  # prime_number.exem -> TestPrimeNumber
    TestClass = importlib.import_module(class_name)
    suite = unittest.TestLoader().loadTestsFromModule(TestClass)
    unittest.TextTestRunner().run(suite)

    return html(examples, code)


def html(examples, code):
    top_html = """<!DOCTYPE html><html>
    <head><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"></head>\n
    <body><p><b>Instructions</b>: Enter blank-line delimited input↲output[↲reason]
    examples of desired behavior on the left then press Tab.  Exemplar will 
    attempt to generate conforming Python code on the right.</p>\n"""

    demos_html = """<br/>Or, click a button for another demonstration. 
    (There may be a sub-minute delay while tests are run in the console.)\n
    <table><tr>"""
    demos = ['prime_number', 'leap_year', 'guess2', 'fizz_buzz']
    for demo in demos:
        demos_html += "<td><form method='POST' action='/demo/" + demo + \
                      "'>\n<input type='submit' value='" + demo + "'/></form></td>\n"
    demos_html += "</tr></table>\n"

    return top_html + """<table><tr><th>Examples</th><th>Code generated</th></tr>\n
    <tr><td><form id="examples_f" method="POST" action="/generate">\n
    <textarea id="examples_ta" name="examples_ta" rows="14" cols="40" onchange=
    "submit();">""" + ''.join(examples) + \
           """</textarea></form></td>\n
           <td><textarea id="code_generated" rows="14" cols="40" readonly="readonly">""" + \
           code + '</textarea></td></tr></table>\n' + demos_html + '</body></html>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
# With this IF, execution never reaches here.
