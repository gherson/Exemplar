import re
# Testing the re module 4/14/2019.

match = re.search('(?<=abc)def', 'abcdef')
print("Should be 'def':", match.group(0))

match = re.search(r'(?<=-)\w+', 'spam-egg')
print("Should be 'egg':", match.group(0))

# \1 is var name, \2 is datum.
regex = re.compile(r"([A-z]\w+) = input\('\1:'\)  # Eg, ([^ \n]*)")
print("Should be 'v110 is var name, 4 is datum.':",
      regex.sub(r"\1 is var name, \2 is datum.", "v110 = input('v110:')  # Eg, 4"))
print("regex.match should be None:", regex.match(r"asdf"))
print("regex.match should be True:", "True" if regex.match(r"v110 = input('v110:')  # Eg, 4") else "False")
match = regex.match(r"v110 = input('v110:')  # Eg, 4")
print("groups 1 and 2 should be v110, 4:", match.group(1) + ', ' + str(match.group(2)))

# \1 is var name, \2 is datum.
regex = re.compile(r"([A-z]\w+) = input\('\1:'\)  # Eg, ([^ \n]*)")
print("Should be 'v110 = int(input('v110:'))  # Eg, 4':")
print(10 * ' ',
      regex.sub(r"\1 = int(input('\1:'))  # Eg, \2'", "v110 = input('v110:')  # Eg, 4"))