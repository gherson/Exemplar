

def mysplit(s):
    """Exemplar-related R&D 6/17/18"""

    # Collect the starting position of all the spaces and words in s, ignoring 
    # consecutive spaces and non-space characters, respectively, into lists
    # `spaces` and `words`.
    in_spaces = False
    in_word = False
    spaces = []
    words = []
    for i in range(len(s)):
        if s[i]==" ":
            in_word = False
            if not in_spaces:
                spaces.append(i)
                in_spaces = True
        else:  # In a word.
            in_spaces = False
            if not in_word:
                words.append(i)
                in_word = True

    print(' input: "' + s + '"')
    if len(words) and words[0] == 0:
        print(' words: ' + str(words) + '\nspaces: ' + str(spaces))
        i = 0  # Use first space position as an `s` delimiter.
    else:
        print('spaces: ' + str(spaces) + '\n words: ' + str(words))
        i = 1  # Skip first space position as an `s` delimiter.

    # Loop thru the words of `s`, appending each to return_list.
    spaces.append(len(s))  # A hack allowing last print of `s`.
    return_list = []
    for pos in words:
        print(s[pos:spaces[i]])
        return_list.append(s[pos:spaces[i]])
        i += 1
    return return_list
    
s = ' hello    world  ! '
print(mysplit(s))  # output: ['hello', 'world', '!']
